/* Compiled one-line extension DP on a C-built face graph (port of dp1fast/dp1.c; identical semantics).
 * See graph.h for the state layout.  A directed path starts at an inf element, crosses each base line once and
 * leaves through an inf element of the antipodal face.  gain = sum of per-face gains.
 */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "graph.h"

#define NEG (-9999)

typedef struct {
    Graph *g;
    int K;
    int16_t *memo;      /* ns*K */
    int *stamp;
    int cur, cap_ns;
    uint32_t side0, allw;
    int allow4;
} Ctx;

void *dp1_from_tokens(int n, int nt, const int *tg, const int *tw) {
    Ctx *c = calloc(1, sizeof(Ctx));
    c->g = graph_new();
    if (graph_build(c->g, n, nt, tg, tw)) { graph_free(c->g); free(c); return NULL; }
    c->K = n + 2;
    c->cap_ns = c->g->ns;
    c->memo = malloc((size_t)c->g->ns * c->K * sizeof(int16_t));
    c->stamp = calloc(c->g->ns, sizeof(int));
    c->allw = graph_full_mask(n);
    return c;
}

void dp1_free(void *p) {
    Ctx *c = p;
    graph_free(c->g); free(c->memo); free(c->stamp); free(c);
}

int dp1_base_T(void *p) { return ((Ctx *)p)->g->T0; }
int dp1_nstarts(void *p) { return ((Ctx *)p)->g->nstarts; }
void dp1_starts(void *p, int *out) { Ctx *c = p; memcpy(out, c->g->starts, c->g->nstarts * sizeof(int)); }
int dp1_nf(void *p) { return ((Ctx *)p)->g->nf; }
int dp1_ns(void *p) { return ((Ctx *)p)->g->ns; }
void dp1_export(void *p, int *foff, int *flen, int *kind, uint32_t *mask, int *nxt, uint32_t *below, int *face_of,
                int *sel) {
    Graph *g = ((Ctx *)p)->g;
    memcpy(foff, g->foff, g->nf * sizeof(int)); memcpy(flen, g->flen, g->nf * sizeof(int));
    memcpy(below, g->below, g->nf * sizeof(uint32_t));
    memcpy(kind, g->kind, g->ns * sizeof(int)); memcpy(mask, g->mask, g->ns * sizeof(uint32_t));
    memcpy(nxt, g->nxt, g->ns * sizeof(int)); memcpy(face_of, g->face_of, g->ns * sizeof(int));
    memcpy(sel, g->sel, g->ns * sizeof(int));
}

static int16_t *best(Ctx *c, int s) {
    const Graph *g = c->g;
    int16_t *out = c->memo + (size_t)s * c->K;
    if (c->stamp[s] == c->cur) return out;
    int f = g->face_of[s], base = g->foff[f], m = g->flen[f], ei = s - base, K = c->K;
    uint32_t C = c->side0 ^ g->below[f];
    for (int k = 0; k < K; k++) out[k] = NEG;
    for (int xj = 0; xj < m; xj++) {
        if (xj == ei) continue;
        int t = base + xj, kd = g->kind[t];
        if (kd == 0) {
            if (C == c->allw) {
                int gn = graph_gain(g, f, ei, xj);
                if (out[0] < gn) out[0] = gn;
            }
            continue;
        }
        if (!c->allow4 && __builtin_popcount(g->mask[t]) > 2) continue;
        if (g->mask[t] & C) continue;
        int16_t *sub = best(c, g->nxt[t]);
        int gn = graph_gain(g, f, ei, xj), dk = kd == 2;
        for (int k = 0; k + dk < K; k++)
            if (sub[k] > NEG && out[k + dk] < sub[k] + gn) out[k + dk] = sub[k] + gn;
    }
    c->stamp[s] = c->cur;
    return out;
}

static void begin_start(Ctx *c, int s0) {
    c->cur++;
    c->side0 = c->g->below[c->g->face_of[s0]];
}

static int use_start(Ctx *c, int s, int canonical) {
    if (!canonical) return 1;
    const Graph *g = c->g;
    int f = g->face_of[s];
    uint32_t b = g->below[f];
    if (b == c->allw) return 0;
    if (b == 0) return 1;
    return s == g->foff[f];
}

int dp1_solve(void *p, int allow4, int canonical, int *best_start, int16_t *best_start_k,
              int *best_k, int *path_start, int *path_out, int *path_len) {
    Ctx *c = p; const Graph *g = c->g; int K = c->K, overall = NEG;
    c->allow4 = allow4;
    for (int k = 0; k < K; k++) best_k[k] = NEG;
    *path_len = 0; *path_start = -1;
    for (int i = 0; i < g->nstarts; i++) {
        int s0 = g->starts[i];
        best_start[i] = NEG;
        for (int k = 0; k < K; k++) best_start_k[i * K + k] = NEG;
        if (!use_start(c, s0, canonical)) continue;
        begin_start(c, s0);
        int16_t *r = best(c, s0);
        int bs = NEG, bk = -1;
        for (int k = 0; k < K; k++) {
            best_start_k[i * K + k] = r[k];
            if (r[k] > bs) { bs = r[k]; bk = k; }
            if (r[k] > best_k[k]) best_k[k] = r[k];
        }
        best_start[i] = bs;
        if (bs > overall) {
            overall = bs;
            int s = s0, kk = bk, len = 0; *path_start = s0;
            for (;;) {
                int f = g->face_of[s], base = g->foff[f], m = g->flen[f], ei = s - base;
                uint32_t C = c->side0 ^ g->below[f];
                int16_t val = c->memo[(size_t)s * K + kk], found = 0;
                for (int xj = 0; xj < m && !found; xj++) {
                    if (xj == ei) continue;
                    int t = base + xj, kd = g->kind[t];
                    if (kd == 0) {
                        if (C == c->allw && kk == 0 && graph_gain(g, f, ei, xj) == val) { found = 2; }
                        continue;
                    }
                    if (!allow4 && __builtin_popcount(g->mask[t]) > 2) continue;
                    if (g->mask[t] & C) continue;
                    int dk = kd == 2;
                    if (kk - dk < 0) continue;
                    int16_t sv = c->memo[(size_t)g->nxt[t] * K + kk - dk];
                    if (sv > NEG && sv + graph_gain(g, f, ei, xj) == val) {
                        path_out[len++] = t; s = g->nxt[t]; kk -= dk; found = 1;
                    }
                }
                if (found != 1) break;
            }
            *path_len = len;
        }
    }
    return overall;
}

typedef struct { int thr; long cap, count; int *buf; int *sbuf; int stride; int path[64]; } Enum;

static void erec(Ctx *c, Enum *e, int s, int partial, int depth, int s0) {
    const Graph *g = c->g;
    int f = g->face_of[s], base = g->foff[f], m = g->flen[f], ei = s - base, K = c->K;
    uint32_t C = c->side0 ^ g->below[f];
    for (int xj = 0; xj < m; xj++) {
        if (xj == ei) continue;
        int t = base + xj, kd = g->kind[t];
        int gn = graph_gain(g, f, ei, xj);
        if (kd == 0) {
            if (C == c->allw && partial + gn >= e->thr) {
                if (e->count < e->cap) {
                    memcpy(e->buf + e->count * e->stride, e->path, depth * sizeof(int));
                    for (int d = depth; d < e->stride; d++) e->buf[e->count * e->stride + d] = -1;
                    e->sbuf[e->count] = s0;
                }
                e->count++;
            }
            continue;
        }
        if (!c->allow4 && __builtin_popcount(g->mask[t]) > 2) continue;
        if (g->mask[t] & C) continue;
        int16_t *sub = best(c, g->nxt[t]);
        int mx = NEG;
        for (int k = 0; k < K; k++) if (sub[k] > mx) mx = sub[k];
        if (mx <= NEG || partial + gn + mx < e->thr) continue;
        e->path[depth] = t;
        erec(c, e, g->nxt[t], partial + gn, depth + 1, s0);
    }
}

long dp1_enum(void *p, int allow4, int canonical, int thr, long cap, int stride, int *buf, int *sbuf) {
    Ctx *c = p; const Graph *g = c->g;
    Enum e; e.thr = thr; e.cap = cap; e.count = 0; e.buf = buf; e.sbuf = sbuf; e.stride = stride;
    c->allow4 = allow4;
    for (int i = 0; i < g->nstarts; i++) {
        int s0 = g->starts[i];
        if (!use_start(c, s0, canonical)) continue;
        begin_start(c, s0);
        int16_t *r = best(c, s0);
        int mx = NEG;
        for (int k = 0; k < c->K; k++) if (r[k] > mx) mx = r[k];
        if (mx < thr) continue;
        erec(c, &e, s0, 0, 0, s0);
    }
    return e.count;
}

/* Scalar variant (max over the number of new triple points folded in): best_start[i] identical to
 * max_k best_start_k[i][k] of dp1_solve.  Returns the overall maximum gain (NEG if none). */
static int best1(Ctx *c, int s) {
    const Graph *g = c->g;
    int16_t mm = c->memo[s];        /* stamp-free: reset by memset per start */
    if (mm != (int16_t)0x8080) return mm;
    int f = g->face_of[s], base = g->foff[f], m = g->flen[f], ei = s - base, out = NEG;
    uint32_t C = c->side0 ^ g->below[f];
    for (int xj = 0; xj < m; xj++) {
        if (xj == ei) continue;
        int t = base + xj, kd = g->kind[t];
        if (kd == 0) {
            if (C == c->allw) {
                int gn = graph_gain(g, f, ei, xj);
                if (out < gn) out = gn;
            }
            continue;
        }
        if (!c->allow4 && __builtin_popcount(g->mask[t]) > 2) continue;
        if (g->mask[t] & C) continue;
        int sub = best1(c, g->nxt[t]);
        if (sub > NEG) { int v = sub + graph_gain(g, f, ei, xj); if (v > out) out = v; }
    }
    c->memo[s] = out;
    return out;
}

int dp1_solve_max(void *p, int allow4, int canonical, int *best_start) {
    Ctx *c = p; const Graph *g = c->g; int overall = NEG;
    c->allow4 = allow4;
    for (int i = 0; i < g->nstarts; i++) {
        int s0 = g->starts[i];
        best_start[i] = NEG;
        if (!use_start(c, s0, canonical)) continue;
        c->side0 = g->below[g->face_of[s0]];
        memset(c->memo, 0x80, (size_t)g->ns * sizeof(int16_t));
        int v = best1(c, s0);
        best_start[i] = v;
        if (v > overall) overall = v;
    }
    return overall;
}
