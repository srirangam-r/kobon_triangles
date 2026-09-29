#include "graph.h"
#include <stdlib.h>
#include <string.h>

Graph *graph_new(void) { return calloc(1, sizeof(Graph)); }

static void freeall(Graph *g) {
    free(g->foff); free(g->flen); free(g->face_of); free(g->kind); free(g->nxt); free(g->sel);
    free(g->mask); free(g->below); free(g->pe); free(g->pi); free(g->tri); free(g->starts);
    free(g->eidx); free(g->ewire); free(g->vmask);
    free(g->fL); free(g->fR); free(g->lhead); free(g->ltail); free(g->nodeE); free(g->nodeN);
    free(g->eb); free(g->ea); free(g->est); free(g->vf); free(g->vs); free(g->vnp);
}

void graph_free(Graph *g) { freeall(g); free(g); }

static void reserve(Graph *g, int n, int nt) {
    int F = 2 + n + 2 * nt + 2, E = n + 3 * nt + 2, V = nt + 1;
    int S = 2 * E + 6 * V + 2 * F + 8, N = 8 * nt + 4 * n + 16;
    if (F <= g->capF && E <= g->capE && V <= g->capV && S <= g->capS && N <= g->capN) return;
    freeall(g);
    g->capF = F; g->capE = E; g->capV = V; g->capS = S; g->capN = N;
    g->foff = malloc(F * sizeof(int)); g->flen = malloc(F * sizeof(int));
    g->face_of = malloc(S * sizeof(int)); g->kind = malloc(S * sizeof(int)); g->nxt = malloc(S * sizeof(int));
    g->sel = malloc(S * sizeof(int));
    g->mask = malloc(S * sizeof(uint32_t)); g->below = malloc(F * sizeof(uint32_t));
    g->pe = malloc((S + F) * sizeof(int)); g->pi = malloc((S + F) * sizeof(int));
    g->tri = malloc(F); g->starts = malloc(S * sizeof(int));
    g->eidx = malloc(E * sizeof(int)); g->ewire = malloc(E * sizeof(int)); g->vmask = malloc(V * sizeof(uint32_t));
    g->fL = malloc(F * sizeof(int)); g->fR = malloc(F * sizeof(int));
    g->lhead = malloc(2 * F * sizeof(int)); g->ltail = malloc(2 * F * sizeof(int));
    g->nodeE = malloc(N * sizeof(int)); g->nodeN = malloc(N * sizeof(int));
    g->eb = malloc(E * sizeof(int)); g->ea = malloc(E * sizeof(int)); g->est = malloc(2 * E * sizeof(int));
    g->vf = malloc(6 * V * sizeof(int)); g->vs = malloc(6 * V * sizeof(int)); g->vnp = malloc(V * sizeof(int));
}

/* element encoding in lists: edge e -> 2e, vertex v -> 2v+1 */
static inline void push(Graph *g, int f, int which, int elem, int *nn) {
    int k = (*nn)++;
    g->nodeE[k] = elem; g->nodeN[k] = -1;
    int *h = &g->lhead[which * g->capF + f], *t = &g->ltail[which * g->capF + f];
    if (*h < 0) *h = k; else g->nodeN[*t] = k;
    *t = k;
}

int graph_build(Graph *g, int n, int nt, const int *tg, const int *tw) {
    if (n > 32 || n < 2) return -1;
    reserve(g, n, nt);
    g->n = n; g->nt = nt;
    int nf = 0, ne = 0, nv = 0, nn = 0;
    for (int f = 0; f < g->capF; f++) { g->lhead[f] = g->lhead[g->capF + f] = -1; }
    for (int w = 0; w < n; w++) { g->nvw[w] = 0; g->new_[w] = 0; }
    int a[MAXW], cur[MAXW];
    uint32_t curmask;
#define NEWFACE(bm) (g->fL[nf] = g->fR[nf] = -1, g->below[nf] = (bm), nf++)
#define NEWEDGE(w, bl, ab) (g->eb[ne] = (bl), g->ea[ne] = (ab), g->ewire[ne] = (w), \
                            g->eidx[ne] = g->new_[w], g->wedge[w][g->new_[w]++] = ne, ne++)
    int B = NEWFACE(0), Tp = NEWFACE(graph_full_mask(n));
    for (int i = 0; i < n; i++) a[i] = i;
    for (int h = 0; h < n - 1; h++) cur[h] = NEWFACE((1u << (h + 1)) - 1);
#define GAP(h) ((h) < 0 ? B : ((h) > n - 2 ? Tp : cur[h]))
    int curedge[MAXW];
    for (int s = 0; s < n; s++) {
        int e = NEWEDGE(a[s], GAP(s - 1), GAP(s));
        curedge[a[s]] = e;
    }
    for (int h = 0; h < n - 1; h++) {
        push(g, cur[h], 0, 2 * curedge[a[h]], &nn);
        push(g, cur[h], 1, 2 * curedge[a[h + 1]], &nn);
    }
    push(g, B, 1, 2 * curedge[a[0]], &nn);
    push(g, Tp, 0, 2 * curedge[a[n - 1]], &nn);
    for (int t = 0; t < nt; t++) {
        int gg = tg[t], width = tw[t];
        if (gg < 0 || gg + width > n) return -2;
        int v = nv++;
        int S = GAP(gg - 1), N = GAP(gg + width - 1);
        uint32_t bm = 0;
        for (int k = 0; k < width; k++) bm |= 1u << a[gg + k];
        g->vmask[v] = bm;
        for (int k = 0; k < width; k++) {
            int w = a[gg + k];
            g->wrow[w][g->nvw[w]] = bm & ~(1u << w);
            g->wvert[w][g->nvw[w]++] = v;
        }
        curmask = 0;
        for (int k = 0; k < gg; k++) curmask |= 1u << a[k];
        int low, high;
        if (width == 2) {
            int p = a[gg], q = a[gg + 1];
            int W = cur[gg];
            a[gg] = q; a[gg + 1] = p;
            int E = NEWFACE(curmask | (1u << q)); cur[gg] = E;
            g->fR[W] = v; g->fL[E] = v;
            int eq = NEWEDGE(q, S, E), ep = NEWEDGE(p, E, N);
            push(g, E, 0, 2 * eq, &nn); push(g, E, 1, 2 * ep, &nn);
            int *vf = g->vf + 6 * v;
            vf[0] = W; vf[1] = E; vf[2] = S; vf[3] = N; g->vnp[v] = 2;
            low = eq; high = ep;
        } else {
            int p = a[gg], m = a[gg + 1], q = a[gg + 2];
            int W0 = cur[gg], W1 = cur[gg + 1];
            a[gg] = q; a[gg + 1] = m; a[gg + 2] = p;
            int E0 = NEWFACE(curmask | (1u << q));
            int E1 = NEWFACE(curmask | (1u << q) | (1u << m));
            cur[gg] = E0; cur[gg + 1] = E1;
            g->fR[W0] = v; g->fR[W1] = v; g->fL[E0] = v; g->fL[E1] = v;
            int eq = NEWEDGE(q, S, E0), em = NEWEDGE(m, E0, E1), ep = NEWEDGE(p, E1, N);
            push(g, E0, 0, 2 * eq, &nn); push(g, E0, 1, 2 * em, &nn);
            push(g, E1, 0, 2 * em, &nn); push(g, E1, 1, 2 * ep, &nn);
            int *vf = g->vf + 6 * v;
            vf[0] = E1; vf[1] = W0; vf[2] = W1; vf[3] = E0; vf[4] = N; vf[5] = S; g->vnp[v] = 3;
            low = eq; high = ep;
        }
        push(g, S, 1, 2 * v + 1, &nn); push(g, S, 1, 2 * low, &nn);
        push(g, N, 0, 2 * v + 1, &nn); push(g, N, 0, 2 * high, &nn);
    }
    g->nf = nf; g->ne = ne; g->nv = nv;
    if (nn > g->capN || nf > g->capF || ne > g->capE) return -3;
    /* emit cyclic element lists */
    int pos = 0, tmp[4 * MAXE * MAXE + 64];
    for (int f = 0; f < nf; f++) {
        g->foff[f] = pos;
        int m = 0;
        int *cyc = tmp;   /* encoded: -1 inf, 2e edge (bot: +0 / top: use flag bit 30), 2v+1 vertex */
        int side[4 * MAXE * MAXE + 64];
        if (f == B) {
            cyc[m] = -1; side[m++] = 0;
            for (int k = g->lhead[g->capF + f]; k >= 0; k = g->nodeN[k]) { cyc[m] = g->nodeE[k]; side[m++] = 1; }
        } else if (f == Tp) {
            cyc[m] = -1; side[m++] = 0;
            for (int k = g->lhead[f]; k >= 0; k = g->nodeN[k]) { cyc[m] = g->nodeE[k]; side[m++] = 0; }
        } else {
            if (g->fL[f] >= 0) { cyc[m] = 2 * g->fL[f] + 1; side[m++] = 0; } else { cyc[m] = -1; side[m++] = 0; }
            for (int k = g->lhead[f]; k >= 0; k = g->nodeN[k]) { cyc[m] = g->nodeE[k]; side[m++] = 0; }
            if (g->fR[f] >= 0) { cyc[m] = 2 * g->fR[f] + 1; side[m++] = 0; } else { cyc[m] = -1; side[m++] = 0; }
            int t0 = m;
            for (int k = g->lhead[g->capF + f]; k >= 0; k = g->nodeN[k]) { cyc[m] = g->nodeE[k]; side[m++] = 1; }
            for (int i = t0, j = m - 1; i < j; i++, j--) {
                int x = cyc[i]; cyc[i] = cyc[j]; cyc[j] = x;
                x = side[i]; side[i] = side[j]; side[j] = x;
            }
        }
        g->flen[f] = m;
        for (int i = 0; i < m; i++) {
            int s = pos + i, el = cyc[i];
            g->face_of[s] = f;
            if (el < 0) { g->kind[s] = 0; g->mask[s] = 0; g->sel[s] = -1; g->nxt[s] = -1; }
            else if (!(el & 1)) {
                int e = el >> 1;
                g->kind[s] = 1; g->mask[s] = 1u << g->ewire[e]; g->sel[s] = e;
                g->est[2 * e + side[i]] = s;
            } else {
                int v = el >> 1;
                g->kind[s] = 2; g->mask[s] = g->vmask[v]; g->sel[s] = v;
                for (int k = 0; k < 2 * g->vnp[v]; k++)
                    if (g->vf[6 * v + k] == f) g->vs[6 * v + k] = s;
            }
        }
        pos += m;
    }
    g->ns = pos;
    if (pos > g->capS) return -4;
    /* est[2e+1]: state of edge e in its below face (top list); est[2e]: state in its above face (bot list) */
    for (int s = 0; s < pos; s++) {
        if (g->kind[s] == 1) { int e = g->sel[s]; g->nxt[s] = (g->est[2 * e] == s) ? g->est[2 * e + 1] : g->est[2 * e]; }
        else if (g->kind[s] == 2) {
            int v = g->sel[s], nx = -1;
            for (int k = 0; k < 2 * g->vnp[v]; k++)
                if (g->vs[6 * v + k] == s) nx = g->vs[6 * v + (k ^ 1)];
            g->nxt[s] = nx;
        }
    }
    /* per-face data */
    g->T0 = 0; g->nstarts = 0;
    for (int f = 0; f < nf; f++) {
        int base = g->foff[f], m = g->flen[f], bounded = 1, nedg = 0;
        int *pe = g->pe + base + f, *pi = g->pi + base + f;
        pe[0] = pi[0] = 0;
        for (int i = 0; i < m; i++) {
            int k = g->kind[base + i];
            if (k == 0) { bounded = 0; g->starts[g->nstarts++] = base + i; }
            nedg += k == 1;
            pe[i + 1] = pe[i] + (k == 1);
            pi[i + 1] = pi[i] + (k == 0);
        }
        g->tri[f] = bounded && nedg == 3;
        g->T0 += g->tri[f];
    }
    return 0;
}
