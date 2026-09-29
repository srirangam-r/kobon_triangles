/* Face graph of a wiring word, built in C.  Port of work/research2/extend_dp.build plus the flattening done by
 * dp1fast.Dp1: the arrays (foff, flen, kind, mask, nxt, below) are element-for-element identical to what
 * dp1fast feeds to dp1.c (same face numbering, same cyclic element order).
 *
 * States s = (face f, cyc index i) = foff[f] + i.  kind: 0 inf, 1 edge, 2 vertex.  mask: lines through the element
 * (edge: 1<<wire; vertex: block mask).  nxt: same element in the face on the other side (-1 for inf).
 * Extra data for extension: per wire the ordered edge / vertex lists and the event rows.
 */
#ifndef GRAPH_H
#define GRAPH_H
#include <stdint.h>

#define MAXW 32      /* wires */
#define MAXE 34      /* events (or edges) per wire */

typedef struct Graph {
    int n, nt, nf, ns, nv, ne;
    int capF, capS, capV, capE, capN;
    int *foff, *flen, *face_of, *kind, *nxt, *sel;
    uint32_t *mask, *below;
    int *pe, *pi;                 /* per face prefix counts of edges / infs, length m+1 at foff[f]+f */
    uint8_t *tri;                 /* face is a bounded triangle */
    int T0;
    int *starts, nstarts;
    /* wire structure */
    int nvw[MAXW], new_[MAXW];
    int wvert[MAXW][MAXE], wedge[MAXW][MAXE];
    uint32_t wrow[MAXW][MAXE];
    int *eidx, *ewire;            /* per edge: index in its wire's edge list, wire */
    uint32_t *vmask;              /* per vertex: block mask */
    /* build scratch */
    int *fL, *fR, *lhead, *ltail;      /* lhead/ltail: [2][capF]; list 0 = bot, 1 = top */
    int *nodeE, *nodeN;
    int *eb, *ea, *est;                /* edge below/above face; est[2e], est[2e+1]: state in below / above face */
    int *vf, *vs, *vnp;                /* vertex: 6 face ids, 6 states, number of opposite pairs */
} Graph;

Graph *graph_new(void);
void graph_free(Graph *g);
/* Build from tokens (tg[i] = slot, tw[i] = 2 or 3).  Returns 0 on success. */
int graph_build(Graph *g, int n, int nt, const int *tg, const int *tw);

static inline uint32_t graph_full_mask(int n) { return n >= 32 ? 0xffffffffu : ((1u << n) - 1); }

static inline int graph_piece_tri(const Graph *g, int f, int i, int j) {
    int base = g->foff[f], m = g->flen[f];
    if (g->kind[base + i] == 0 || g->kind[base + j] == 0) return 0;
    const int *pe = g->pe + base + f, *pi = g->pi + base + f;
    int ce, ci;
    if (i < j) { ce = pe[j] - pe[i + 1]; ci = pi[j] - pi[i + 1]; }
    else { ce = pe[m] - pe[i + 1] + pe[j]; ci = pi[m] - pi[i + 1] + pi[j]; }
    if (ci) return 0;
    return (g->kind[base + i] == 1) + (g->kind[base + j] == 1) + ce == 2;
}

/* gain of a path entering face f at element i and leaving at element j (i != j) */
static inline int graph_gain(const Graph *g, int f, int i, int j) {
    return -(int)g->tri[f] + graph_piece_tri(g, f, i, j) + graph_piece_tri(g, f, j, i);
}
/* start state of a left-end at `gap` wires below (gap in 0..n) */
static inline int graph_start_state(const Graph *g, int gap) {
    int f = gap == 0 ? 0 : (gap == g->n ? 1 : gap + 1);
    return g->foff[f];
}
#endif
