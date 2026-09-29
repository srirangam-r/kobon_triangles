/* Exact two-line extension search in C: port of search/extend2_dp.py (pair_search and everything below it).
 *
 * A "base" is a face graph (graph.c).  All one-line DPs (modes G / N / S), the (G, D)-Pareto tables, the plan
 * costs (count_ge), the (G, D)-constrained enumeration, the base+L1 rebuild (rows -> wiring word -> face graph)
 * and the exact second-line DP run in C.  Semantics identical to extend2_dp.pair_search; see that file for the
 * bound (T <= T0 + Kx + G1 + G2 + min(D1, D2)).  Kx is computed by the Python wrapper (interaction_bound).
 * Not thread-safe (static count hash).
 */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "graph.h"

#define ENEG (-99)
#define UNSET ((int16_t)0x8080)

/* per-state transition lists of the base graph (non-inf exits without 4-fold points) and end gains */
typedef struct {
    int *off, *t, *nx;
    int8_t *gn;
    uint32_t *mk;
    int8_t *eg;                 /* best gain of ending at an infinity of the face entered at this state, ENEG if none */
} Trans;

typedef struct {
    const Graph *g;
    uint32_t s0, full;
    const uint8_t *bonus;       /* per face, or NULL */
    int16_t *memo;              /* per state */
    const Trans *tr;            /* optional (base graph) */
} DpC;

static int endgain(const Graph *g, int f, int ei) {
    int base = g->foff[f], m = g->flen[f], b = ENEG;
    for (int xj = 0; xj < m; xj++)
        if (xj != ei && g->kind[base + xj] == 0) {
            int v = graph_gain(g, f, ei, xj);
            if (v > b) b = v;
        }
    return b;
}

static int dpb(DpC *c, int s) {
    int16_t mm = c->memo[s];
    if (mm != UNSET) return mm;
    const Graph *g = c->g;
    int f = g->face_of[s], base = g->foff[f], m = g->flen[f], ei = s - base;
    uint32_t C = c->s0 ^ g->below[f];
    int bo = c->bonus ? c->bonus[f] : 0, b = ENEG;
    if (c->tr) {
        const Trans *T = c->tr;
        if (C == c->full && T->eg[s] > ENEG) b = T->eg[s] + bo;
        for (int i = T->off[s]; i < T->off[s + 1]; i++) {
            if (T->mk[i] & C) continue;
            int v = dpb(c, T->nx[i]);
            if (v > ENEG) { int cand = v + T->gn[i] + bo; if (cand > b) b = cand; }
        }
        c->memo[s] = b;
        return b;
    }
    if (C == c->full) {
        int e = endgain(g, f, ei);
        if (e > ENEG) b = e + bo;
    }
    for (int xj = 0; xj < m; xj++) {
        if (xj == ei) continue;
        int t = base + xj;
        if (g->kind[t] == 0 || __builtin_popcount(g->mask[t]) > 2 || (g->mask[t] & C)) continue;
        int v = dpb(c, g->nxt[t]);
        if (v > ENEG) {
            int cand = v + graph_gain(g, f, ei, xj) + bo;
            if (cand > b) b = cand;
        }
    }
    c->memo[s] = b;
    return b;
}

typedef struct {
    int start, val, Dc;
    uint32_t s0;
    const uint8_t *bonus;
    int16_t *memo;
    int16_t *byd;               /* ns * Dc, lazily; entries ENEG = none */
    uint8_t *bydone;
} DpObj;

typedef struct {
    Graph *g, *scr;
    Trans tr;
    int n, T0, Kx, Dc;
    uint32_t full;
    DpObj *dp[MAXW + 1][2];     /* [gap][0 = G, 1 = N] */
    int16_t *f2[MAXW + 1];
    int f2n[MAXW + 1];
    uint8_t *zero, *flags;
    int16_t *fmemo, *smemo;
    int cap_smemo;
    /* search state */
    int inc, bestk, bestlen, bestseq[64];
    long evals, pruned2, nodes;
    int gaps[3], pgap[3], MG[3], MN[3];
    int path[64], fs[64];
    int stop, target_mode, wcount;
    int cond_kind, ca, ce, cf;
} Ext2;

static inline int X(const Ext2 *E) { return E->inc + 1 - E->T0 - E->Kx; }

static DpC dpc_of(const DpObj *d, const Ext2 *E) {
    DpC c = {E->g, d->s0, E->full, d->bonus, d->memo, &E->tr};
    return c;
}

static void build_trans(Ext2 *E) {
    const Graph *g = E->g;
    Trans *T = &E->tr;
    int ns = g->ns, cap = 0;
    for (int f = 0; f < g->nf; f++) cap += g->flen[f] * g->flen[f];
    T->off = malloc((ns + 1) * sizeof(int)); T->t = malloc(cap * sizeof(int)); T->nx = malloc(cap * sizeof(int));
    T->gn = malloc(cap); T->mk = malloc(cap * sizeof(uint32_t)); T->eg = malloc(ns);
    int k = 0;
    for (int s = 0; s < ns; s++) {
        int f = g->face_of[s], base = g->foff[f], m = g->flen[f], ei = s - base;
        T->off[s] = k;
        T->eg[s] = (int8_t)endgain(g, f, ei);
        for (int xj = 0; xj < m; xj++) {
            int t = base + xj;
            if (xj == ei || g->kind[t] == 0 || __builtin_popcount(g->mask[t]) > 2) continue;
            T->t[k] = t; T->nx[k] = g->nxt[t]; T->mk[k] = g->mask[t]; T->gn[k] = (int8_t)graph_gain(g, f, ei, xj);
            k++;
        }
    }
    T->off[ns] = k;
}

void *ext2_new(int n, int nt, const int *tg, const int *tw, int Kx) {
    if (n > 30) return NULL;
    Ext2 *E = calloc(1, sizeof(Ext2));
    E->g = graph_new(); E->scr = graph_new();
    if (graph_build(E->g, n, nt, tg, tw)) { graph_free(E->g); graph_free(E->scr); free(E); return NULL; }
    E->n = n; E->T0 = E->g->T0; E->Kx = Kx; E->Dc = n + 4;
    E->full = graph_full_mask(n);
    E->zero = calloc(E->g->nf, 1); E->flags = calloc(E->g->nf, 1);
    E->fmemo = malloc((size_t)E->g->ns * sizeof(int16_t));
    build_trans(E);
    return E;
}

void ext2_free(void *p) {
    Ext2 *E = p;
    for (int i = 0; i <= MAXW; i++) {
        for (int m = 0; m < 2; m++) {
            DpObj *d = E->dp[i][m];
            if (d) { free(d->memo); free(d->byd); free(d->bydone); free(d); }
        }
        free(E->f2[i]);
    }
    graph_free(E->g); graph_free(E->scr);
    free(E->tr.off); free(E->tr.t); free(E->tr.nx); free(E->tr.gn); free(E->tr.mk); free(E->tr.eg);
    free(E->zero); free(E->flags); free(E->fmemo); free(E->smemo); free(E);
}

int ext2_T0(void *p) { return ((Ext2 *)p)->T0; }

static DpObj *dp_get(Ext2 *E, int gap, int mode) {
    DpObj *d = E->dp[gap][mode];
    if (d) return d;
    const Graph *g = E->g;
    d = calloc(1, sizeof(DpObj));
    d->start = graph_start_state(g, gap);
    d->s0 = g->below[g->face_of[d->start]];
    d->Dc = E->Dc;
    d->bonus = mode ? g->tri : E->zero;
    d->memo = malloc((size_t)g->ns * sizeof(int16_t));
    memset(d->memo, 0x80, (size_t)g->ns * sizeof(int16_t));
    DpC c = dpc_of(d, E);
    d->val = dpb(&c, d->start);
    E->dp[gap][mode] = d;
    return d;
}

static int16_t *byd(Ext2 *E, DpObj *d, int s) {
    const Graph *g = E->g;
    const Trans *T = &E->tr;
    if (!d->byd) {
        d->byd = malloc((size_t)g->ns * d->Dc * sizeof(int16_t));
        d->bydone = calloc(g->ns, 1);
    }
    int16_t *r = d->byd + (size_t)s * d->Dc;
    if (d->bydone[s]) return r;
    int f = g->face_of[s], Dc = d->Dc;
    uint32_t C = d->s0 ^ g->below[f];
    int d0 = g->tri[f];
    for (int k = 0; k < Dc; k++) r[k] = ENEG;
    if (C == E->full && T->eg[s] > ENEG) r[d0] = T->eg[s];
    for (int i = T->off[s]; i < T->off[s + 1]; i++) {
        if (T->mk[i] & C) continue;
        int16_t *sub = byd(E, d, T->nx[i]);
        int gn = T->gn[i];
        for (int k = 0; k + d0 < Dc; k++)
            if (sub[k] > ENEG && r[k + d0] < sub[k] + gn) r[k + d0] = sub[k] + gn;
    }
    d->bydone[s] = 1;
    return r;
}

/* f2[D] = max_d (bestG[d] + min(D, d)) for the start at `gap`; length = max d + 1 (0 if no path) */
static void f2_make(Ext2 *E, int gap) {
    if (E->f2[gap]) return;
    DpObj *d = dp_get(E, gap, 0);
    int16_t *bd = byd(E, d, d->start);
    int mx = -1;
    for (int k = 0; k < d->Dc; k++) if (bd[k] > ENEG) mx = k;
    E->f2n[gap] = mx + 1;
    E->f2[gap] = malloc((mx + 2) * sizeof(int16_t));
    for (int D = 0; D <= mx; D++) {
        int b = -30000;
        for (int k = 0; k <= mx; k++)
            if (bd[k] > ENEG) { int v = bd[k] + (D < k ? D : k); if (v > b) b = v; }
        E->f2[gap][D] = b;
    }
}
static inline int f2v(const Ext2 *E, int gap, int D) {
    int n = E->f2n[gap];
    return E->f2[gap][D < n - 1 ? D : n - 1];
}

/* ---- count_ge ---------------------------------------------------------------------------------------- */
#define HB 20
static int64_t *h_keys, *h_vals;
static int *h_stamp, h_cur;

static int64_t cnt(Ext2 *E, DpObj *d, DpC *c, int s, int need) {
    int64_t key = ((int64_t)s << 32) | (uint32_t)(need + (1 << 30));
    uint32_t h = (uint32_t)(((uint64_t)key * 0x9E3779B97F4A7C15ull) >> (64 - HB));
    while (h_stamp[h] == h_cur) {
        if (h_keys[h] == key) return h_vals[h];
        h = (h + 1) & ((1u << HB) - 1);
    }
    const Graph *g = E->g;
    const Trans *T = &E->tr;
    int f = g->face_of[s];
    uint32_t C = d->s0 ^ g->below[f];
    int bo = d->bonus[f];
    int64_t r = 0;
    if (C == E->full && T->eg[s] > ENEG && T->eg[s] + bo >= need) r++;
    for (int i = T->off[s]; i < T->off[s + 1]; i++) {
        if (T->mk[i] & C) continue;
        int v = dpb(c, T->nx[i]);
        int gn = T->gn[i];
        if (v > ENEG && gn + bo + v >= need) r += cnt(E, d, c, T->nx[i], need - gn - bo);
    }
    h = (uint32_t)(((uint64_t)key * 0x9E3779B97F4A7C15ull) >> (64 - HB));   /* re-probe: table grew in recursion */
    while (h_stamp[h] == h_cur) h = (h + 1) & ((1u << HB) - 1);
    h_stamp[h] = h_cur; h_keys[h] = key; h_vals[h] = r;
    return r;
}

static int64_t count_ge(Ext2 *E, DpObj *d, int thr) {
    if (!h_keys) {
        h_keys = malloc(sizeof(int64_t) << HB); h_vals = malloc(sizeof(int64_t) << HB);
        h_stamp = calloc(1u << HB, sizeof(int));
    }
    h_cur++;
    DpC c = dpc_of(d, E);
    return cnt(E, d, &c, d->start, thr);
}

/* ---- extension: base + one new line ------------------------------------------------------------------- */
static int rows_to_tokens(uint32_t rows[MAXW][MAXE], int *rl, int N, const int *init, int *tg, int *tw) {
    int order[MAXW], pos[MAXW] = {0}, left = 0, nt = 0;
    for (int i = 0; i < N; i++) { order[i] = init[i]; left += rl[i]; }
#define NX(w) (pos[w] < rl[w] ? (int64_t)rows[w][pos[w]] : -1)
    while (left) {
        int progressed = 0;
        for (int s = 0; s < N - 1 && !progressed; s++) {
            int u = order[s], v = order[s + 1];
            int64_t ru = NX(u);
            if (ru < 0 || !((ru >> v) & 1)) continue;
            if (__builtin_popcountll(ru) == 1) {
                if (NX(v) == (int64_t)(1u << u)) {
                    order[s] = v; order[s + 1] = u; pos[u]++; pos[v]++; left -= 2;
                    tg[nt] = s; tw[nt++] = 2; progressed = 1;
                }
            } else if (__builtin_popcountll(ru) == 2 && s + 2 < N) {
                int w = order[s + 2];
                if (ru == (int64_t)((1u << v) | (1u << w)) && NX(v) == (int64_t)((1u << u) | (1u << w)) &&
                    NX(w) == (int64_t)((1u << u) | (1u << v))) {
                    order[s] = w; order[s + 2] = u; pos[u]++; pos[v]++; pos[w]++; left -= 3;
                    tg[nt] = s; tw[nt++] = 3; progressed = 1;
                }
            }
        }
        if (!progressed) return -1;
    }
    return nt;
}

/* Build the face graph of base + the line following exit states path[0..len) that starts at base gap `gap`.
 * Result in E->scr.  Returns 0 on success. */
static int build_ext(Ext2 *E, int gap, const int *path, int len) {
    const Graph *g = E->g;
    int n = E->n, N = n + 1;
    static uint32_t rows[MAXW][MAXE];
    int rl[MAXW], insk[MAXW], insi[MAXW];
    for (int w = 0; w < n; w++) { rl[w] = g->nvw[w]; insk[w] = -1; }
    uint32_t L[MAXE * 2];
    for (int i = 0; i < len; i++) {
        int t = path[i], e = g->sel[t];
        if (g->kind[t] == 1) {
            int w = g->ewire[e];
            insk[w] = 0; insi[w] = g->eidx[e];
            L[i] = 1u << w;
        } else {
            uint32_t bm = g->vmask[e];
            for (int w = 0; w < n; w++)
                if ((bm >> w) & 1) {
                    int j = 0;
                    while (g->wvert[w][j] != e) j++;
                    insk[w] = 1; insi[w] = j;
                }
            L[i] = bm;
        }
    }
    for (int w = 0; w < n; w++) {
        if (insk[w] < 0) return -5;
        int k = 0;
        for (int j = 0; j <= g->nvw[w]; j++) {
            if (insk[w] == 0 && j == insi[w]) rows[w][k++] = 1u << n;
            if (j < g->nvw[w]) {
                uint32_t r = g->wrow[w][j];
                if (insk[w] == 1 && j == insi[w]) r |= 1u << n;
                rows[w][k++] = r;
            }
        }
        rl[w] = k;
    }
    for (int i = 0; i < len; i++) rows[n][i] = L[i];
    rl[n] = len;
    int init[MAXW], tg[512], tw[512];
    for (int i = 0; i < gap; i++) init[i] = i;
    init[gap] = n;
    for (int i = gap; i < n; i++) init[i + 1] = i;
    int nt = rows_to_tokens(rows, rl, N, init, tg, tw);
    if (nt < 0) return -6;
    return graph_build(E->scr, N, nt, tg, tw);
}

/* exact best gain of one more line at left gap pgap of base + line (path from gap) ; -1000 on build failure */
static int partner(Ext2 *E, int gap, const int *path, int len, int pgap) {
    if (build_ext(E, gap, path, len)) return -1000;
    const Graph *sg = E->scr;
    if (sg->ns > E->cap_smemo) {
        free(E->smemo); E->cap_smemo = sg->ns * 2; E->smemo = malloc((size_t)E->cap_smemo * sizeof(int16_t));
    }
    memset(E->smemo, 0x80, (size_t)sg->ns * sizeof(int16_t));
    int s = graph_start_state(sg, pgap);
    DpC c = {sg, sg->below[sg->face_of[s]], graph_full_mask(sg->n), NULL, E->smemo, NULL};
    return dpb(&c, s);
}

/* ---- search ------------------------------------------------------------------------------------------ */
static void evaluate(Ext2 *E, int k, int g, int depth) {
    const Graph *bg = E->g;
    E->nodes++;
    for (int i = 0; i <= depth; i++) if (bg->tri[E->fs[i]]) E->flags[E->fs[i]] = 1;
    int need = E->inc + 1 - E->T0 - E->Kx - g;
    DpObj *o = dp_get(E, E->gaps[3 - k], 0);
    memset(E->fmemo, 0x80, (size_t)bg->ns * sizeof(int16_t));
    DpC c = {bg, o->s0, E->full, E->flags, E->fmemo, &E->tr};
    int v = dpb(&c, o->start);
    for (int i = 0; i <= depth; i++) E->flags[E->fs[i]] = 0;
    if (v < need) { E->pruned2++; return; }
    E->evals++;
    int pv = partner(E, E->gaps[k], E->path, depth, E->pgap[k]);
    if (pv == -1000) { E->stop = -1; return; }
    if (pv > ENEG && E->T0 + g + pv > E->inc) {
        E->inc = E->T0 + g + pv;
        E->bestk = k; E->bestlen = depth;
        memcpy(E->bestseq, E->path, depth * sizeof(int));
        if (E->target_mode) E->stop = 1;
    }
}

/* warm-up: paths of the G-mode DP with weight >= thr, stop after 301 evaluations */
static void rec_w(Ext2 *E, int k, DpObj *d, int s, int acc, int accg, int depth, int thr) {
    const Graph *g = E->g;
    const Trans *T = &E->tr;
    int f = g->face_of[s];
    uint32_t C = d->s0 ^ g->below[f];
    E->fs[depth] = f;
    if (C == E->full && T->eg[s] > ENEG && acc + T->eg[s] >= thr) {
        evaluate(E, k, accg + T->eg[s], depth);
        if (E->stop) return;
        if (E->wcount++ >= 300) { E->stop = 2; return; }
    }
    DpC c = dpc_of(d, E);
    for (int i = T->off[s]; i < T->off[s + 1]; i++) {
        if (T->mk[i] & C) continue;
        int v = dpb(&c, T->nx[i]);
        int gn = T->gn[i];
        if (v > ENEG && acc + gn + v >= thr) {
            E->path[depth] = T->t[i];
            rec_w(E, k, d, T->nx[i], acc + gn, accg + gn, depth + 1, thr);
            if (E->stop) return;
        }
    }
}

static inline int cond(const Ext2 *E, int g, int d) {
    int x = X(E);
    if (E->cond_kind == 0) {
        int t1 = E->ca > x - E->MG[E->cf] ? E->ca : x - E->MG[E->cf];
        return g + d >= t1 && g + f2v(E, E->gaps[E->cf], d) >= x;
    } else {
        int a = x - E->ca + 1, b = x - E->MN[E->ce], t1 = a > b ? a : b;
        return g >= t1 && g + f2v(E, E->gaps[E->ce], d) >= x;
    }
}

static void rec_gd(Ext2 *E, int k, DpObj *d, int s, int accg, int accd, int depth) {
    const Graph *g = E->g;
    const Trans *T = &E->tr;
    int f = g->face_of[s];
    uint32_t C = d->s0 ^ g->below[f];
    int d0 = g->tri[f];
    E->fs[depth] = f;
    if (C == E->full && T->eg[s] > ENEG && cond(E, accg + T->eg[s], accd + d0)) {
        evaluate(E, k, accg + T->eg[s], depth);
        if (E->stop) return;
    }
    for (int i = T->off[s]; i < T->off[s + 1]; i++) {
        if (T->mk[i] & C) continue;
        int nf = T->nx[i];
        int16_t *sub = byd(E, d, nf);
        int a2 = accg + T->gn[i], d2 = accd + d0, any = 0;
        for (int dd = 0; dd < d->Dc && !any; dd++)
            if (sub[dd] > ENEG && cond(E, a2 + sub[dd], d2 + dd)) any = 1;
        if (any) {
            E->path[depth] = T->t[i];
            rec_gd(E, k, d, nf, a2, d2, depth + 1);
            if (E->stop) return;
        }
    }
}

/* Returns T (target mode: >= target, first placement found; else the exact maximum), -1 if none, -2 on an
 * internal error.  out[0] = k (which line was enumerated: 1 = L1 at base gap r1, 2 = L2 at base gap r2-1),
 * out[1] = path length, out[2..] = exit states of the enumerated line in the base graph. */
int ext2_pair(void *p, int r1, int r2, int target, int warm, int *out) {
    Ext2 *E = p;
    int T0 = E->T0, Kx = E->Kx;
    E->gaps[1] = r1; E->gaps[2] = r2 - 1; E->pgap[1] = r2; E->pgap[2] = r1;
    E->target_mode = target >= 0;
    E->inc = target >= 0 ? target - 1 : -1;
    E->bestk = 0; E->stop = 0;
    for (int k = 1; k <= 2; k++) {
        DpObj *g_ = dp_get(E, E->gaps[k], 0), *n_ = dp_get(E, E->gaps[k], 1);
        E->MG[k] = g_->val; E->MN[k] = n_->val;
        if (E->MG[k] <= ENEG) return -1;
    }
    int *MG = E->MG, *MN = E->MN;
#define UB() (T0 + Kx + (MN[1] + MG[2] < MG[1] + MN[2] ? MN[1] + MG[2] : MG[1] + MN[2]))
    if (UB() < E->inc + 1) return -1;
    if (warm && target < 0) {
        for (int k = 1; k <= 2; k++) {
            DpObj *d = dp_get(E, E->gaps[k], 0);
            E->wcount = 0; E->stop = 0;
            rec_w(E, k, d, d->start, 0, 0, 0, MG[k] - 1);
            if (E->stop < 0) return -2;
            E->stop = 0;
        }
        if (UB() < E->inc + 1) goto done;
    }
    {
        int x = X(E), pe = 0, pf = 0, pa = 0;
        int64_t best_cost = -1;
        int half = (x + 1) >> 1;
        for (int ord = 0; ord < 2; ord++) {
            int e = ord ? 2 : 1, f = ord ? 1 : 2;
            DpObj *dN = dp_get(E, E->gaps[e], 1), *dG = dp_get(E, E->gaps[f], 0);
            int lo = half - 2 > 1 ? half - 2 : 1;
            for (int a = lo; a < half + 3; a++) {
                int lo_a = a > x - MG[f] ? a : x - MG[f];
                int lo_b = x - a + 1 > x - MN[e] ? x - a + 1 : x - MN[e];
                int64_t cost = (lo_a <= MN[e] ? count_ge(E, dN, lo_a) : 0) + (lo_b <= MG[f] ? count_ge(E, dG, lo_b) : 0);
                if (best_cost < 0 || cost < best_cost) { best_cost = cost; pe = e; pf = f; pa = a; }
            }
        }
        E->ca = pa; E->ce = pe; E->cf = pf;
        f2_make(E, E->gaps[pf]); f2_make(E, E->gaps[pe]);
        DpObj *de = dp_get(E, E->gaps[pe], 0);
        E->cond_kind = 0; E->stop = 0;
        rec_gd(E, pe, de, de->start, 0, 0, 0);
        if (E->stop < 0) return -2;
        if (!(E->target_mode && E->bestk)) {
            DpObj *df = dp_get(E, E->gaps[pf], 0);
            E->cond_kind = 1; E->stop = 0;
            rec_gd(E, pf, df, df->start, 0, 0, 0);
            if (E->stop < 0) return -2;
        }
    }
done:
    if (!E->bestk) return -1;
    out[0] = E->bestk; out[1] = E->bestlen;
    memcpy(out + 2, E->bestseq, E->bestlen * sizeof(int));
    return E->inc;
}

void ext2_stats(void *p, long *out) {
    Ext2 *E = p;
    out[0] = E->evals; out[1] = E->pruned2; out[2] = E->nodes;
}

/* test hooks */
int ext2_mgmn(void *p, int gap, int *mg, int *mn) {
    Ext2 *E = p;
    *mg = dp_get(E, gap, 0)->val; *mn = dp_get(E, gap, 1)->val;
    return 0;
}
int ext2_partner(void *p, int gap, const int *path, int len, int pgap) { return partner(p, gap, path, len, pgap); }
int ext2_bydn(void *p, int gap, int *out) {
    Ext2 *E = p;
    DpObj *d = dp_get(E, gap, 0);
    int16_t *bd = byd(E, d, d->start);
    for (int k = 0; k < d->Dc; k++) out[k] = bd[k];
    return d->Dc;
}
int ext2_scratch_T0(void *p) { return ((Ext2 *)p)->scr->T0; }
int ext2_count_ge(void *p, int gap, int mode, int thr) { Ext2 *E = p; return (int)count_ge(E, dp_get(E, gap, mode), thr); }
