/* Compiled port of the one-line extension DP (work/research2/extend_dp.py: solve / all_paths).
 * The face structure is flattened by the Python wrapper into "states" = (face, cyc index) pairs:
 *   kind[s]: 0 inf, 1 edge, 2 vertex;  mask[s]: bitmask of lines through the element;
 *   nxt[s]: state of the same element in the face on the other side (-1 for inf);
 *   below[f]: bitmask of lines below face f;  foff[f], flen[f]: cyc slice of face f.
 * A directed path starts at an inf element (start state), crosses each base line once and
 * leaves through an inf element of the antipodal face.  gain = sum of per-face gains.
 */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define NEG (-9999)

typedef struct {
    int n, nf, ns, K;
    int *foff, *flen, *face_of, *kind, *nxt, *goff;
    uint32_t *mask, *below;
    int16_t *gain;      /* per face: len*len table, gain[goff[f] + i*len + j] */
    int16_t *memo;      /* ns*K */
    int *stamp;
    int cur;
    uint32_t side0, allw;
    int allow4;
    int base_T;         /* triangles of the base, from the structure */
    int *starts, nstarts;
} Ctx;

static int piece_tri(Ctx *c, int f, int i, int j) {
    int base = c->foff[f], m = c->flen[f];
    if (c->kind[base + i] == 0 || c->kind[base + j] == 0) return 0;
    int cnt = (c->kind[base + i] == 1) + (c->kind[base + j] == 1);
    int k = (i + 1) % m;
    while (k != j) {
        if (c->kind[base + k] == 0) return 0;
        cnt += c->kind[base + k] == 1;
        k = (k + 1) % m;
    }
    return cnt == 2;
}

void *dp1_new(int n, int nf, int ns, const int *foff, const int *flen, const int *kind,
              const uint32_t *mask, const int *nxt, const uint32_t *below) {
    Ctx *c = calloc(1, sizeof(Ctx));
    c->n = n; c->nf = nf; c->ns = ns; c->K = n + 2;
    c->foff = malloc(nf * sizeof(int)); memcpy(c->foff, foff, nf * sizeof(int));
    c->flen = malloc(nf * sizeof(int)); memcpy(c->flen, flen, nf * sizeof(int));
    c->goff = malloc(nf * sizeof(int));
    c->kind = malloc(ns * sizeof(int)); memcpy(c->kind, kind, ns * sizeof(int));
    c->nxt = malloc(ns * sizeof(int)); memcpy(c->nxt, nxt, ns * sizeof(int));
    c->mask = malloc(ns * sizeof(uint32_t)); memcpy(c->mask, mask, ns * sizeof(uint32_t));
    c->below = malloc(nf * sizeof(uint32_t)); memcpy(c->below, below, nf * sizeof(uint32_t));
    c->face_of = malloc(ns * sizeof(int));
    int tot = 0;
    for (int f = 0; f < nf; f++) {
        c->goff[f] = tot; tot += flen[f] * flen[f];
        for (int i = 0; i < flen[f]; i++) c->face_of[foff[f] + i] = f;
    }
    c->gain = malloc(tot * sizeof(int16_t));
    c->base_T = 0;
    for (int f = 0; f < nf; f++) {
        int m = flen[f], bounded = 1, ne = 0;
        for (int i = 0; i < m; i++) {
            int k = kind[foff[f] + i];
            if (k == 0) bounded = 0;
            ne += k == 1;
        }
        int tri = bounded && ne == 3;
        c->base_T += tri;
        for (int i = 0; i < m; i++)
            for (int j = 0; j < m; j++)
                c->gain[c->goff[f] + i * m + j] =
                    i == j ? 0 : (int16_t)(-tri + piece_tri(c, f, i, j) + piece_tri(c, f, j, i));
    }
    c->memo = malloc((size_t)ns * c->K * sizeof(int16_t));
    c->stamp = calloc(ns, sizeof(int));
    c->allw = (n >= 32) ? 0xffffffffu : ((1u << n) - 1);
    c->starts = malloc(ns * sizeof(int));
    for (int s = 0; s < ns; s++)
        if (kind[s] == 0) c->starts[c->nstarts++] = s;
    return c;
}

void dp1_free(void *p) {
    Ctx *c = p;
    free(c->foff); free(c->flen); free(c->goff); free(c->kind); free(c->nxt); free(c->mask);
    free(c->below); free(c->face_of); free(c->gain); free(c->memo); free(c->stamp); free(c->starts);
    free(c);
}

int dp1_base_T(void *p) { return ((Ctx *)p)->base_T; }
int dp1_nstarts(void *p) { return ((Ctx *)p)->nstarts; }
void dp1_starts(void *p, int *out) { Ctx *c = p; memcpy(out, c->starts, c->nstarts * sizeof(int)); }

static inline int gainof(Ctx *c, int f, int i, int j) {
    return c->gain[c->goff[f] + i * c->flen[f] + j];
}

static int16_t *best(Ctx *c, int s) {
    int16_t *out = c->memo + (size_t)s * c->K;
    if (c->stamp[s] == c->cur) return out;
    int f = c->face_of[s], base = c->foff[f], m = c->flen[f], ei = s - base, K = c->K;
    uint32_t C = c->side0 ^ c->below[f];
    for (int k = 0; k < K; k++) out[k] = NEG;
    for (int xj = 0; xj < m; xj++) {
        if (xj == ei) continue;
        int t = base + xj, kd = c->kind[t];
        if (kd == 0) {
            if (C == c->allw) {
                int g = gainof(c, f, ei, xj);
                if (out[0] < g) out[0] = g;
            }
            continue;
        }
        if (!c->allow4 && __builtin_popcount(c->mask[t]) > 2) continue;
        if (c->mask[t] & C) continue;
        int16_t *sub = best(c, c->nxt[t]);
        int g = gainof(c, f, ei, xj), dk = kd == 2;
        for (int k = 0; k + dk < K; k++)
            if (sub[k] > NEG && out[k + dk] < sub[k] + g) out[k + dk] = sub[k] + g;
    }
    c->stamp[s] = c->cur;
    return out;
}

static void begin_start(Ctx *c, int s0) {
    c->cur++;
    c->side0 = c->below[c->face_of[s0]];
}

/* s is a start state; canonical: skip starts that are reverses of others (keep left-inf starts and
 * the bottom face).  Returns 1 if the start is used. */
static int use_start(Ctx *c, int s, int canonical) {
    if (!canonical) return 1;
    int f = c->face_of[s];
    uint32_t b = c->below[f];
    if (b == c->allw) return 0;                 /* top face: reverse of the bottom face's paths */
    if (b == 0) return 1;
    return s == c->foff[f];                     /* left inf is cyc[0]; right infs are reversals */
}

/* Per start: best_start[i] (max over k, NEG if none), best_start_k[i*K + k].
 * Global: best_k[K]; argmax path: exits (start state, then exit state per step) in path_out
 * (length n), path_len; returns overall max gain. */
int dp1_solve(void *p, int allow4, int canonical, int *best_start, int16_t *best_start_k,
              int *best_k, int *path_start, int *path_out, int *path_len) {
    Ctx *c = p; int K = c->K, overall = NEG;
    c->allow4 = allow4;
    for (int k = 0; k < K; k++) best_k[k] = NEG;
    *path_len = 0; *path_start = -1;
    for (int i = 0; i < c->nstarts; i++) {
        int s0 = c->starts[i];
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
            /* reconstruct */
            int s = s0, kk = bk, len = 0; *path_start = s0;
            for (;;) {
                int f = c->face_of[s], base = c->foff[f], m = c->flen[f], ei = s - base;
                uint32_t C = c->side0 ^ c->below[f];
                int16_t val = c->memo[(size_t)s * K + kk], found = 0;
                for (int xj = 0; xj < m && !found; xj++) {
                    if (xj == ei) continue;
                    int t = base + xj, kd = c->kind[t];
                    if (kd == 0) {
                        if (C == c->allw && kk == 0 && gainof(c, f, ei, xj) == val) { found = 2; }
                        continue;
                    }
                    if (!allow4 && __builtin_popcount(c->mask[t]) > 2) continue;
                    if (c->mask[t] & C) continue;
                    int dk = kd == 2;
                    if (kk - dk < 0) continue;
                    int16_t sv = c->memo[(size_t)c->nxt[t] * K + kk - dk];
                    if (sv > NEG && sv + gainof(c, f, ei, xj) == val) {
                        path_out[len++] = t; s = c->nxt[t]; kk -= dk; found = 1;
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
    int f = c->face_of[s], base = c->foff[f], m = c->flen[f], ei = s - base, K = c->K;
    uint32_t C = c->side0 ^ c->below[f];
    for (int xj = 0; xj < m; xj++) {
        if (xj == ei) continue;
        int t = base + xj, kd = c->kind[t];
        int g = gainof(c, f, ei, xj);
        if (kd == 0) {
            if (C == c->allw && partial + g >= e->thr) {
                if (e->count < e->cap) {
                    memcpy(e->buf + e->count * e->stride, e->path, depth * sizeof(int));
                    for (int d = depth; d < e->stride; d++) e->buf[e->count * e->stride + d] = -1;
                    e->sbuf[e->count] = s0;
                }
                e->count++;
            }
            continue;
        }
        if (!c->allow4 && __builtin_popcount(c->mask[t]) > 2) continue;
        if (c->mask[t] & C) continue;
        int16_t *sub = best(c, c->nxt[t]);
        int mx = NEG;
        for (int k = 0; k < K; k++) if (sub[k] > mx) mx = sub[k];
        if (mx <= NEG || partial + g + mx < e->thr) continue;
        e->path[depth] = t;
        erec(c, e, c->nxt[t], partial + g, depth + 1, s0);
    }
}

/* Enumerate all directed paths with total gain >= thr.  buf: cap x stride ints (exit states,
 * -1 padded), sbuf: cap start states.  Returns the total count (may exceed cap). */
long dp1_enum(void *p, int allow4, int canonical, int thr, long cap, int stride, int *buf, int *sbuf) {
    Ctx *c = p; Enum e; e.thr = thr; e.cap = cap; e.count = 0; e.buf = buf; e.sbuf = sbuf; e.stride = stride;
    c->allow4 = allow4;
    for (int i = 0; i < c->nstarts; i++) {
        int s0 = c->starts[i];
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
