/* walkc: compiled hot paths of the DP ruin-and-recreate walk (search/dpwalk_c.py).
 *
 * One translation unit: it #includes the (unmodified) face-graph builder and one-line DP of search/dp1fast2 so that
 * the DP handle, the Graph and the rebuild share memory.  A "word" is a byte string of (g, w) pairs (slot, width 2|3),
 * i.e. the wiring word of search/dpwalk.py as 2*nt bytes.
 *
 *   wc_delete        word with line d removed        (= extend_dp.delete_wire)
 *   wc_info          T, k, bridges, Z, D (+ per line Z, D, incident Z)   (= quick_check.count_triangles, Arr.Z/D,
 *                    test_k5L_layer.geometry bridges)
 *   wc_rows_hash     64-bit hash of the event rows (labelled arrangement identity, cheap)
 *   wc_canon         canonical chi form under the 4n end-circle symmetries + global sign flip (= coverage.canon),
 *                    and its 64-bit hash
 *   wc_rows_to_word  rows (masks) -> wiring word, mode 0 = dpwalk.sweep, mode 1 = audit_planted.rows_to_word
 *   wc_insert_path   base word + DP path (exit states) -> word of the extended arrangement (= Base.word_of)
 *   wc_eval          insert_path + info + rows hash in one call
 *   dp1_*            (from dp1.c) the one-line DP handle
 */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "../dp1fast2/graph.c"
#include "../dp1fast2/dp1.c"

/* fused-enum scratch, see wc_prepare */
static int16_t *w_memo;
static size_t w_cap;
static void *w_owner;
static int *w_bs;
static int w_nstarts;

/* ------------------------------------------------------------------------------------------ small helpers */
static inline uint64_t mix64(uint64_t x) {
    x ^= x >> 30; x *= 0xbf58476d1ce4e5b9ULL;
    x ^= x >> 27; x *= 0x94d049bb133111ebULL;
    x ^= x >> 31;
    return x;
}

uint64_t wc_hash_bytes(const uint8_t *p, int len) {
    uint64_t h = 0x9e3779b97f4a7c15ULL ^ (uint64_t)len;
    int i = 0;
    for (; i + 8 <= len; i += 8) { uint64_t v; memcpy(&v, p + i, 8); h = mix64(h ^ v) + 0x9e3779b97f4a7c15ULL; }
    uint64_t v = 0;
    for (int j = 0; i + j < len; j++) v |= (uint64_t)p[i + j] << (8 * j);
    return mix64(h ^ v ^ 0x1234567ULL);
}

typedef struct {
    int n;
    int len[MAXW];
    uint32_t row[MAXW][MAXE];        /* per line: mask of the other lines at each event */
} Rows;

/* rows from a word; -1 on a malformed word */
static int build_rows(const uint8_t *word, int nt, int n, Rows *R) {
    int a[MAXW];
    if (n < 2 || n > 32) return -1;
    R->n = n;
    for (int i = 0; i < n; i++) { a[i] = i; R->len[i] = 0; }
    for (int t = 0; t < nt; t++) {
        int g = word[2 * t], w = word[2 * t + 1];
        if ((w != 2 && w != 3) || g + w > n) return -1;
        uint32_t bm = 0;
        for (int k = 0; k < w; k++) bm |= 1u << a[g + k];
        for (int k = 0; k < w; k++) {
            int x = a[g + k];
            if (R->len[x] >= MAXE) return -1;
            R->row[x][R->len[x]++] = bm & ~(1u << x);
        }
        for (int i = 0, j = w - 1; i < j; i++, j--) { int x = a[g + i]; a[g + i] = a[g + j]; a[g + j] = x; }
    }
    return 0;
}

/* ------------------------------------------------------------------------------------------ delete */
/* extend_dp.delete_wire.  Returns the number of tokens written to out (capacity >= nt). */
int wc_delete(const uint8_t *word, int nt, int n, int d, uint8_t *out) {
    int a[MAXW], slot[MAXW], no = 0;
    for (int i = 0; i < n; i++) a[i] = slot[i] = i;
    for (int t = 0; t < nt; t++) {
        int g = word[2 * t], w = word[2 * t + 1];
        int cnt = 0, lo = 1 << 20;
        for (int k = 0; k < w; k++) {
            int x = a[g + k];
            if (x == d) continue;
            cnt++;
            if (slot[x] < lo) lo = slot[x];
        }
        if (cnt >= 2) {
            out[2 * no] = (uint8_t)(lo - (slot[d] < lo ? 1 : 0));
            out[2 * no + 1] = (uint8_t)cnt;
            no++;
        }
        for (int i = 0, j = w - 1; i < j; i++, j--) { int x = a[g + i]; a[g + i] = a[g + j]; a[g + j] = x; }
        for (int k = 0; k < w; k++) slot[a[g + k]] = g + k;
    }
    return no;
}

/* ------------------------------------------------------------------------------------------ counts */
/* out[0..4] = T, k, bridges, Z, D; then Zl[n], Dl[n], Zi[n].  Returns 0, or -1 for a malformed word. */
static int info_rows(const Rows *R, int32_t *out) {
    int n = R->n;
    int8_t pos[MAXW][MAXW];
    uint8_t use[MAXW][MAXE];
    int T = 0, k = 0, Z = 0, D = 0, br = 0;
    memset(pos, -1, sizeof pos);
    memset(use, 0, sizeof use);
    for (int x = 0; x < n; x++)
        for (int e = 0; e < R->len[x]; e++) {
            uint32_t m = R->row[x][e];
            for (int y = 0; y < n; y++) if ((m >> y) & 1) pos[x][y] = e;
            if (__builtin_popcount(m) == 2 && x < __builtin_ctz(m)) k++;   /* lowest line of a triple point counts it */
        }
    /* k: count triple points once (at their lowest line). x < ctz(m) is the lowest of {x} + m. */
    for (int a = 0; a < n; a++)
        for (int b = a + 1; b < n; b++) {
            int pab = pos[a][b], pba = pos[b][a];
            if (pab < 0) continue;
            for (int c = b + 1; c < n; c++) {
                int pac = pos[a][c], pbc = pos[b][c], pca = pos[c][a], pcb = pos[c][b];
                if (pac < 0 || pbc < 0 || pab == pac) continue;
                int da = pab - pac, db = pba - pbc, dc = pca - pcb;
                if ((da == 1 || da == -1) && (db == 1 || db == -1) && (dc == 1 || dc == -1)) {
                    T++;
                    use[a][pab < pac ? pab : pac]++;
                    use[b][pba < pbc ? pba : pbc]++;
                    use[c][pca < pcb ? pca : pcb]++;
                }
            }
        }
    int32_t *Zl = out + 5, *Dl = out + 5 + n, *Zi = out + 5 + 2 * n;
    for (int x = 0; x < n; x++) Zl[x] = Dl[x] = Zi[x] = 0;
    for (int x = 0; x < n; x++)
        for (int e = 0; e + 1 < R->len[x]; e++) {
            int u = use[x][e];
            if (u == 0) {
                Z++; Zl[x]++;
                for (int q = 0; q < 2; q++) {
                    uint32_t m = R->row[x][e + q];
                    if (__builtin_popcount(m) == 1) Zi[__builtin_ctz(m)]++;
                }
            } else if (u == 2) {
                D++; Dl[x]++;
                if (__builtin_popcount(R->row[x][e]) == 2 && __builtin_popcount(R->row[x][e + 1]) == 2) br++;
            }
        }
    out[0] = T; out[1] = k; out[2] = br; out[3] = Z; out[4] = D;
    return 0;
}

int wc_info(const uint8_t *word, int nt, int n, int32_t *out) {
    Rows R;
    if (build_rows(word, nt, n, &R)) return -1;
    return info_rows(&R, out);
}

static uint64_t rows_hash(const Rows *R) {
    uint64_t h = 0x243f6a8885a308d3ULL;
    for (int x = 0; x < R->n; x++) {
        h = mix64(h ^ (0xabcdefULL + x));
        for (int e = 0; e < R->len[x]; e++) h = mix64(h + R->row[x][e] * 0x9e3779b97f4a7c15ULL + e);
    }
    return h;
}

uint64_t wc_rows_hash(const uint8_t *word, int nt, int n) {
    Rows R;
    if (build_rows(word, nt, n, &R)) return 0;
    return rows_hash(&R);
}

/* ------------------------------------------------------------------------------------------ canonical form */
static int8_t *tabF[MAXW + 1];
static int32_t *tabP[MAXW + 1];
static int tabA[MAXW + 1];
static int16_t *tabIdx[MAXW + 1];     /* [i][j][k] -> lexicographic rank of the sorted triple */

/* P: A x m source indices, F: A x m factors (A images incl. the global sign flip), m = C(n,3) */
int wc_set_tables(int n, int A, const int32_t *P, const int8_t *F) {
    if (n < 3 || n > 32) return -1;
    int m = n * (n - 1) * (n - 2) / 6;
    free(tabP[n]); free(tabF[n]); free(tabIdx[n]);
    tabP[n] = malloc((size_t)A * m * sizeof(int32_t));
    tabF[n] = malloc((size_t)A * m);
    memcpy(tabP[n], P, (size_t)A * m * sizeof(int32_t));
    memcpy(tabF[n], F, (size_t)A * m);
    tabA[n] = A;
    tabIdx[n] = calloc(32 * 32 * 32, sizeof(int16_t));
    int r = 0;
    for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) for (int k = j + 1; k < n; k++)
        tabIdx[n][(i * 32 + j) * 32 + k] = r++;
    return 0;
}

/* chi vector of a word (values -1/0/1 in trip order, = run_lns.chi_from_word).  -1 if some triple is unset. */
static int word_chi(const uint8_t *word, int nt, int n, int8_t *chi) {
    int m = n * (n - 1) * (n - 2) / 6, a[MAXW], slot[MAXW], set = 0;
    const int16_t *idx = tabIdx[n];
    if (!idx) return -2;
    for (int i = 0; i < n; i++) a[i] = slot[i] = i;
    for (int t = 0; t < nt; t++) {
        int g = word[2 * t], w = word[2 * t + 1];
        uint32_t bm = 0;
        for (int q = 0; q < w; q++) bm |= 1u << a[g + q];
        for (int p = 0; p < w; p++) for (int q = p + 1; q < w; q++) {
            int i = a[g + p], k = a[g + q];
            if (i > k) { int x = i; i = k; k = x; }
            for (int j = i + 1; j < k; j++) {
                chi[idx[(i * 32 + j) * 32 + k]] = ((bm >> j) & 1) ? 0 : (g > slot[j] ? 1 : -1);
                set++;
            }
        }
        for (int i = 0, j = w - 1; i < j; i++, j--) { int x = a[g + i]; a[g + i] = a[g + j]; a[g + j] = x; }
        for (int q = 0; q < w; q++) slot[a[g + q]] = g + q;
    }
    return set == m ? 0 : -1;
}

/* Canonical form: the byte-wise (unsigned, i.e. -1 = 0xFF) minimum over all images F[a] * chi[P[a]].
 * canon_out (m bytes) may be NULL.  Returns 0 or an error code; *hash = 64-bit hash of the canonical form. */
int wc_canon(const uint8_t *word, int nt, int n, uint8_t *canon_out, uint64_t *hash) {
    int m = n * (n - 1) * (n - 2) / 6;
    int8_t chi[5000];
    uint8_t best[5000];
    if (m > 5000) return -3;
    int rc = word_chi(word, nt, n, chi);
    if (rc) return rc;
    const int32_t *P = tabP[n];
    const int8_t *F = tabF[n];
    int A = tabA[n];
    int have = 0;
    for (int a = 0; a < A; a++) {
        const int32_t *pa = P + (size_t)a * m;
        const int8_t *fa = F + (size_t)a * m;
        int j = 0, better = !have;
        if (have) {
            for (; j < m; j++) {
                uint8_t v = (uint8_t)(int8_t)(fa[j] * chi[pa[j]]);
                if (v != best[j]) { better = v < best[j]; break; }
            }
            if (!better) continue;     /* equal or worse */
            if (j == m) continue;
        }
        for (; j < m; j++) best[j] = (uint8_t)(int8_t)(fa[j] * chi[pa[j]]);
        have = 1;
    }
    if (canon_out) memcpy(canon_out, best, m);
    *hash = wc_hash_bytes(best, m);
    return 0;
}

/* ------------------------------------------------------------------------------------------ rows -> word */
/* rows[w*MAXE + i]: mask of the other lines at the i-th event of line w; rl[w]: events; init[]: bottom-to-top order.
 * mode 0: stack sweep of dpwalk.sweep; mode 1: leftmost-first sweep of audit_planted.rows_to_word / ext2.c.
 * Returns the number of tokens or -1 (no wiring word). */
static int sweep_rows(uint32_t (*rows)[MAXE], const int *rl, int N, const int *init, int mode, uint8_t *out) {
    int a[MAXW], ptr[MAXW] = {0}, nt = 0, total = 0, done = 0;
    int64_t nxt[MAXW];
    for (int i = 0; i < N; i++) { a[i] = init[i]; total += rl[i]; nxt[i] = rl[i] ? (int64_t)rows[i][0] : -1; }
#define ADVANCE(l) (ptr[l]++, nxt[l] = ptr[l] < rl[l] ? (int64_t)rows[l][ptr[l]] : -1)
    if (mode == 0) {
        int stack[MAXW * MAXW * 12], sp = 0;
        for (int g = N - 2; g >= 0; g--) stack[sp++] = g;
        while (sp) {
            int g = stack[--sp];
            int x = a[g], y = a[g + 1], w;
            int64_t ex = nxt[x];
            if (ex < 0 || !((ex >> y) & 1)) continue;
            if (__builtin_popcountll(ex) == 1) {
                if (nxt[y] != (int64_t)(1u << x)) continue;
                w = 2;
            } else {
                if (g + 2 >= N) continue;
                int z = a[g + 2];
                if (ex != (int64_t)((1u << y) | (1u << z)) || nxt[y] != (int64_t)((1u << x) | (1u << z)) ||
                    nxt[z] != (int64_t)((1u << x) | (1u << y))) continue;
                w = 3;
            }
            for (int q = 0; q < w; q++) ADVANCE(a[g + q]);
            for (int i = 0, j = w - 1; i < j; i++, j--) { int t = a[g + i]; a[g + i] = a[g + j]; a[g + j] = t; }
            out[2 * nt] = (uint8_t)g; out[2 * nt + 1] = (uint8_t)w; nt++;
            done += w;
            int lo = g - 2 > 0 ? g - 2 : 0, hi = g + w + 1 < N - 1 ? g + w + 1 : N - 1;
            for (int h = lo; h < hi; h++) stack[sp++] = h;
        }
        return done == total ? nt : -1;
    }
    while (done < total) {
        int progressed = 0;
        for (int s = 0; s < N - 1 && !progressed; s++) {
            int u = a[s], v = a[s + 1];
            int64_t ru = nxt[u];
            if (ru < 0 || !((ru >> v) & 1)) continue;
            if (__builtin_popcountll(ru) == 1) {
                if (nxt[v] == (int64_t)(1u << u)) {
                    a[s] = v; a[s + 1] = u; ADVANCE(u); ADVANCE(v); done += 2;
                    out[2 * nt] = (uint8_t)s; out[2 * nt + 1] = 2; nt++; progressed = 1;
                }
            } else if (__builtin_popcountll(ru) == 2 && s + 2 < N) {
                int w = a[s + 2];
                if (ru == (int64_t)((1u << v) | (1u << w)) && nxt[v] == (int64_t)((1u << u) | (1u << w)) &&
                    nxt[w] == (int64_t)((1u << u) | (1u << v))) {
                    a[s] = w; a[s + 2] = u; ADVANCE(u); ADVANCE(v); ADVANCE(w); done += 3;
                    out[2 * nt] = (uint8_t)s; out[2 * nt + 1] = 3; nt++; progressed = 1;
                }
            }
        }
        if (!progressed) return -1;
    }
    return nt;
}

int wc_rows_to_word(const uint32_t *rows, const int *rl, int N, const int *init, int mode, uint8_t *out) {
    return sweep_rows((uint32_t(*)[MAXE])rows, rl, N, init, mode, out);
}

/* ------------------------------------------------------------------------------------------ insert a DP path */
/* Rows of base + new line (label n) along `path` (exit states, up to the first negative entry or `len`). */
static int path_to_rows(const Graph *g, const int *path, int len, uint32_t (*rows)[MAXE], int *rl, uint32_t *newrow) {
    int n = g->n, insk[MAXW], insi[MAXW];
    for (int w = 0; w < n; w++) insk[w] = -1;
    for (int i = 0; i < len; i++) {
        int t = path[i], e = g->sel[t];
        if (g->kind[t] == 1) {
            int w = g->ewire[e];
            insk[w] = 0; insi[w] = g->eidx[e];
            newrow[i] = 1u << w;
        } else {
            uint32_t bm = g->vmask[e];
            for (int w = 0; w < n; w++)
                if ((bm >> w) & 1) {
                    int j = 0;
                    while (g->wvert[w][j] != e) j++;
                    insk[w] = 1; insi[w] = j;
                }
            newrow[i] = bm;
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
    for (int i = 0; i < len; i++) rows[n][i] = newrow[i];
    rl[n] = len;
    return 0;
}

/* Wiring word of base + path.  `start` = start state of the path (hint: slot and direction of the new line at the
 * left end), or < 0.  Candidate order as Base.word_of: hinted first, then hl = 0..n, rev = 0, 1.  Returns nt or < 0. */
static int insert_path_g(const Graph *g, const int *path, int len, int start, uint8_t *out) {
    int n = g->n, N = n + 1, rl[MAXW], init[MAXW];
    uint32_t rows[MAXW][MAXE], newrow[MAXE * 2];
    if (len > 2 * MAXE) return -7;
    int rc = path_to_rows(g, path, len, rows, rl, newrow);
    if (rc) return rc;
    int hint_hl = -1, hint_rev = 0;
    if (start >= 0) {
        int f = g->face_of[start], s = __builtin_popcount(g->below[f]);
        int left = (f == 0 || f == 1) ? 1 : g->fL[f] < 0;
        int right = (f == 0 || f == 1) ? 0 : g->fR[f] < 0;
        if (left && !right) { hint_hl = s; hint_rev = 0; }
        else if (right && !left) { hint_hl = n - s; hint_rev = 1; }
    }
    /* reversed new row, built once */
    uint32_t rev_row[MAXE * 2];
    for (int i = 0; i < len; i++) rev_row[i] = newrow[len - 1 - i];
    for (int c = -1; c <= 2 * (n + 1); c++) {
        int hl, rev;
        if (c < 0) { if (hint_hl < 0) continue; hl = hint_hl; rev = hint_rev; }
        else { hl = c / 2; rev = c & 1; if (hl == hint_hl && rev == hint_rev) continue; }
        for (int i = 0; i < hl; i++) init[i] = i;
        init[hl] = n;
        for (int i = hl; i < n; i++) init[i + 1] = i;
        uint32_t *nr = rows[n];
        for (int i = 0; i < len; i++) nr[i] = rev ? rev_row[i] : newrow[i];
        int nt = sweep_rows(rows, rl, N, init, 0, out);
        if (nt >= 0) return nt;
    }
    return -6;
}

/* dp = handle from dp1_from_tokens (its Ctx starts with the Graph pointer) */
int wc_insert_path(void *dp, const int *path, int len, int start, uint8_t *out) {
    return insert_path_g(*(Graph **)dp, path, len, start, out);
}

/* path[] is -1 padded (as dp1_enum rows).  out_stats: int32[5 + 3(n+1)] as wc_info, then out_stats_extra[0..1] =
 * rows hash (2 x int32, low / high).  Returns nt of the new word (in out) or < 0. */
int wc_eval(void *dp, const int *path, int maxlen, int start, uint8_t *out, int32_t *stats) {
    const Graph *g = *(Graph **)dp;
    int len = 0;
    while (len < maxlen && path[len] >= 0) len++;
    int nt = insert_path_g(g, path, len, start, out);
    if (nt < 0) return nt;
    Rows R;
    if (build_rows(out, nt, g->n + 1, &R)) return -8;
    info_rows(&R, stats);
    uint64_t h = rows_hash(&R);
    int off = 5 + 3 * (g->n + 1);
    stats[off] = (int32_t)(uint32_t)h; stats[off + 1] = (int32_t)(uint32_t)(h >> 32);
    return nt;
}

/* Standalone: base word + path (builds the graph itself). */
int wc_insert_path_word(const uint8_t *word, int nt, int n, const int *path, int len, int start, uint8_t *out) {
    int tg[600], tw[600];
    if (nt > 600) return -9;
    for (int i = 0; i < nt; i++) { tg[i] = word[2 * i]; tw[i] = word[2 * i + 1]; }
    Graph *g = graph_new();
    if (graph_build(g, n, nt, tg, tw)) { graph_free(g); return -10; }
    int r = insert_path_g(g, path, len, start, out);
    graph_free(g);
    return r;
}

/* DP handle straight from a byte word (invalidates the prepared scratch: a freed handle's address may be reused) */
void *wc_base_new(const uint8_t *word, int nt, int n) {
    int tg[600], tw[600];
    w_owner = NULL;
    if (nt > 600) return NULL;
    for (int i = 0; i < nt; i++) { tg[i] = word[2 * i]; tw[i] = word[2 * i + 1]; }
    return dp1_from_tokens(n, nt, tg, tw);
}

/* ------------------------------------------------------------------------------------------ fused solve + enum */
/* dp1_solve_max + dp1_enum share one scalar DP: per start a memo of "best gain from this state" (max over the number
 * of new triple points, which is all dp1_enum's pruning uses), kept for all starts between wc_prepare and wc_enum.
 * wc_enum enumerates exactly the paths dp1_enum(allow4 = 0, canonical = 1) does, in the same order.
 * Scratch is global: one prepared base at a time (not thread-safe, one process per worker). */

typedef struct { Ctx *c; int16_t *memo; uint32_t side0; } S1;

static int b1(S1 *z, int s) {
    const Graph *g = z->c->g;
    int16_t mm = z->memo[s];
    if (mm != (int16_t)0x8080) return mm;
    int f = g->face_of[s], base = g->foff[f], m = g->flen[f], ei = s - base, out = NEG;
    uint32_t C = z->side0 ^ g->below[f];
    for (int xj = 0; xj < m; xj++) {
        if (xj == ei) continue;
        int t = base + xj, kd = g->kind[t];
        if (kd == 0) {
            if (C == z->c->allw) {
                int gn = graph_gain(g, f, ei, xj);
                if (out < gn) out = gn;
            }
            continue;
        }
        if (__builtin_popcount(g->mask[t]) > 2) continue;
        if (g->mask[t] & C) continue;
        int sub = b1(z, g->nxt[t]);
        if (sub > NEG) { int v = sub + graph_gain(g, f, ei, xj); if (v > out) out = v; }
    }
    z->memo[s] = out;
    return out;
}

/* Returns the best gain over all starts (NEG if none); T = T0 + gain. */
int wc_prepare(void *dp) {
    Ctx *c = dp;
    const Graph *g = c->g;
    size_t need = (size_t)g->nstarts * g->ns;
    if (need > w_cap) { free(w_memo); w_cap = need * 2; w_memo = malloc(w_cap * sizeof(int16_t)); }
    if (g->nstarts > w_nstarts) { free(w_bs); w_bs = malloc(g->nstarts * 2 * sizeof(int)); w_nstarts = g->nstarts * 2; }
    memset(w_memo, 0x80, need * sizeof(int16_t));
    int overall = NEG;
    for (int i = 0; i < g->nstarts; i++) {
        int s0 = g->starts[i];
        S1 z = {c, w_memo + (size_t)i * g->ns, g->below[g->face_of[s0]]};
        w_bs[i] = b1(&z, s0);
        if (w_bs[i] > overall) overall = w_bs[i];
    }
    w_owner = dp;
    return overall;
}

typedef struct { int thr; long cap, count; int *buf, *sbuf; int stride; int path[64]; S1 z; } E1;

static void erec1(E1 *e, int s, int partial, int depth, int s0) {
    const Graph *g = e->z.c->g;
    int f = g->face_of[s], base = g->foff[f], m = g->flen[f], ei = s - base;
    uint32_t C = e->z.side0 ^ g->below[f];
    for (int xj = 0; xj < m; xj++) {
        if (xj == ei) continue;
        int t = base + xj, kd = g->kind[t];
        int gn = graph_gain(g, f, ei, xj);
        if (kd == 0) {
            if (C == e->z.c->allw && partial + gn >= e->thr) {
                if (e->count < e->cap) {
                    memcpy(e->buf + e->count * e->stride, e->path, depth * sizeof(int));
                    for (int d = depth; d < e->stride; d++) e->buf[e->count * e->stride + d] = -1;
                    e->sbuf[e->count] = s0;
                }
                e->count++;
            }
            continue;
        }
        if (__builtin_popcount(g->mask[t]) > 2) continue;
        if (g->mask[t] & C) continue;
        int mx = b1(&e->z, g->nxt[t]);
        if (mx <= NEG || partial + gn + mx < e->thr) continue;
        e->path[depth] = t;
        erec1(e, g->nxt[t], partial + gn, depth + 1, s0);
    }
}

/* thr is a gain threshold (T - T0), as dp1_enum.  Requires wc_prepare(dp) to have been the last prepare. */
long wc_enum(void *dp, int thr, long cap, int stride, int *buf, int *sbuf) {
    if (w_owner != dp) return -1;
    Ctx *c = dp;
    const Graph *g = c->g;
    E1 e;
    e.thr = thr; e.cap = cap; e.count = 0; e.buf = buf; e.sbuf = sbuf; e.stride = stride;
    for (int i = 0; i < g->nstarts; i++) {
        int s0 = g->starts[i];
        if (!use_start(c, s0, 1)) continue;
        if (w_bs[i] < thr) continue;
        e.z.c = c; e.z.memo = w_memo + (size_t)i * g->ns; e.z.side0 = g->below[g->face_of[s0]];
        erec1(&e, s0, 0, 0, s0);
    }
    return e.count;
}
