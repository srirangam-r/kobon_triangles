# T20 — line automaton (search/line_automaton.py)

**Summary (≤ 200 words).**
- **Built:** an automaton over one line L. Frames are vertex types with segment face bits, and there are 145 of them.
  Windows are (prev, cur, next) triples. Hidden variables (far-end multiplicities) are minimised adversarially.
  A min-plus DP (numpy Bellman–Ford) does the following:
  - detects negative cycles;
  - tracks parity, end classes and feature flags;
  - returns witnesses.
- **Validation:** all lines of 128,513 arrangements (2,158,133 lines) are paths of the automaton, with **0 failures**.
  - Data: work/phi/*.jsonl, pilot.jsonl, gallery 10–18 (even and variant dirs).
  - Compared quantities: portions p, 2·v_L, #unserved RN and RR blocks, #triple points.
  - They equal `bbl_hall.values()` / `portions()` exactly.
  - 10 planted mutations are detected.
- **M1 ✔.** A clean line has min portions 1 for even n (m = n−1 odd) and 0 for odd n. The end-compatibility fact carries this.
- **M2 ✔.** v_L + ½#RN + 3/2#RR ≥ −1 for all n, with no multiplicity ≥ 4.
  - Both coefficients are sharp: reducing either one gives −∞ (a T–S(1,1)–T "kite" cycle).
  - Tight against the data minimum.
  - Also a table for X-point axes.
- **M3 not done:** search/bbl_rules2.py is still WIP (R3/R4 use value comparisons on other lines).
- **Speed:** M1 0.2 s; each M2 solve is about 4 s, on a graph with 22k nodes and 0.49M edges.

Reproduce: `python search/line_automaton.py {validate <in>.. | m1 | m2 | crosscheck | datamin <in>.. | coverage <pkl>..}`
(`uv run --no-project --with numpy`). Logs are in work/eng/T20/.

## 1. Model

L is oriented left to right, with sides + (smaller slot index, "above") and −. Vertices are V_1..V_m. Bounded segments
are s_1..s_{m−1}; s_0 and s_m are the unbounded rays. Every bounded segment carries bits (tb, bb): the face on that side
is a triangle. Unbounded rays carry (0,0). Then n − 1 = #simple + 2·#triple.

A **frame** is the local configuration of one vertex:
- `S` (simple, L∩W): (bin, bout, ub = (W's ray on side +/− is unbounded)).
- `T` (triple, L∩a∩b): (bin, bout, h = (the hidden sector a|b on side +/− is a triangle), ub = "some hidden ray on that
  side is unbounded", used only at end vertices).

The six rays at a triple point are, in cyclic order, E, E+, W+, W, W−, E−.
- E, W are L's own rays.
- E+ and E− are the rays adjacent to E on the + / − side; W+ and W− are adjacent to W.
- The six sectors are:

  | sector | bit |
  |---|---|
  | (E, E+) | tb_out |
  | (E+, W+) | h+ |
  | (W+, W) | tb_in |
  | (W, W−) | bb_in |
  | (W−, E−) | h− |
  | (E−, E) | bb_out |

- A ray is *doubly used* iff both adjacent sectors are triangles. Its status is N if it is not doubly used, and
  otherwise B (far end simple) or R (far end triple).

An **Info** tuple `(kind, h, bits, end-flag)` is what a neighbour needs to know: bin for a predecessor, bout for a
successor.

Everything `bbl_hall.values()` attributes to L splits into **window weights** on (prev, cur, next) plus the segment
term. In halves, with v2 = 2·v_L:
- Own unused bounded segment: p+1, v2+2 (attached to the segment after `cur`).
- Simple vertex:
  - touches: for each bounded W-ray with used count = 0, p+1 (the used count of u+ is tb_in+tb_out);
  - T1 with L as cap: if L caps a block on side k (both bits on side k are 1) and *both neighbours are triple*, L pays
    3 per N gap-end ray; that ray is N iff the other-side bit of that adjacent segment is 0.
- Triple vertex:
  - L's rays: N +3, B −3, R 0.
  - L is the axis of a block on E (or W): T1 gains 3 per N gap ray if both flankers (far ends of E+, E−) are triple.
    The gap ray is N iff the bit of the segment beyond X on that side is 0.
  - Otherwise F gains 2 per N flank ray (E+ is N iff h+ = 0).
  - L's N ray E flanks an adjacent block on E+ or E− (sector triangle, far end simple). If that block is unserved, L pays 2.
    "Served" needs the neighbour vertex to be triple with its gap ray N (visible), and the second flanker to be triple with
    its gap ray N (hidden).
  - Blocks on W: same with `prev`.

**Hidden variables** are sig[R] (far end of E+, E−, W+, W− is triple) and g[R] (gap ray N at that far end).
- They are chosen adversarially per window. This is sound because the automaton ignores correlations between windows.
- Each vertex's hidden variables occur in exactly one window. Neighbours see only h, which is part of the frame.
- g only enters "served", and unserved is never better for v_L. So the DP fixes g = 0, which is valid for
  objectives with a nonnegative v2 coefficient. The membership check on data uses all g.

**Objective vector** per window: (p, v2, nRN, nRR, nT). nRN and nRR count unserved blocks with axis L whose flank rays
are (R,N) and (R,R). v_L = v2/2 − 1.

## 2. Local facts imposed (each proved)

All arguments use only that pseudolines pairwise cross exactly once, and that faces are the faces of the arrangement.

- **F1 (faces).** A triangle is a bounded face with three bounded sides. The two faces adjacent to a segment are
  distinct, one on each side. Hence unbounded rays carry (0,0), and a triangle adjacent to an unbounded ray does not exist.
- **F2 (simple vertex).** The four faces at V = L∩W are (±, left) and (±, right). The two faces adjacent to W's ray u+
  are exactly (+,left) and (+,right), so
  - used(u+) = tb_in + tb_out (and likewise used(u−) = bb_in + bb_out);
  - if u+ is unbounded then tb_in = tb_out = 0 (analogously for u−).
  Consequences: touches, P2, and the block status
  - I: the segment beyond X is unbounded;
  - U: it is bounded with bits (0,0);
  - M: otherwise.
  Consecutive same-side triangles at V (tb_in = tb_out = 1) mean L caps the block u+ at V (P1).
- **F3 (doubly used ⇒ multiple end).** Let a segment σ of ℓ have both endpoints simple, ℓ∩A and ℓ∩B, with triangles on
  both sides. The triangle on either side has sides σ, a piece of A at the first end and a piece of B at the second (the
  only other lines there). So its apex is A∩B on that side. A∩B is one point on one side, contradiction. Hence a bounded
  segment with bits (1,1) has a triple endpoint, and S–S edges with (1,1) are dropped.
- **F3′ (apex multiplicity).** Let s_i = [P, X] with P triple and X simple, and tb(s_i) = 1. The triangle above s_i has
  vertices P, X, Y, with [X,Y] on C = the other line at X, and [P,Y] the first segment of E+. So Y is the first vertex on
  both E+ (from P) and C+ (from X). If also tb(s_{i+1}) = 1 (the face on the other side of C+ at X), then C+ =[X,Y]
  is doubly used with X simple, so Y is triple by F3. Hence sig[E+] = 1. Symmetrically for the − side and for W (using
  `prev`). Implemented as `forced` in `sig_domain`.
- **F4 (two blocks at a triple point are never adjacent).** Suppose rays r, r+1 of P are both blocks, with far ends X_r,
  X_{r+1} simple. The triangle in sector (r, r+1) has third side on the second line C at X_r and, by the same argument at
  X_{r+1}, on the second line at X_{r+1}. So both lie on one line C, which does not pass through P. The triangles in
  sectors (r−1, r) and (r+1, r+2) also have third sides on C through X_r resp. X_{r+1}. So C meets ℓ_{r−1} and ℓ_{r+2}.
  These are the same line (rays 3 apart are antipodal), and the meeting points lie on opposite rays. Contradiction, since
  C crosses it once. Implemented as the "no two adjacent B in the ring" condition on hidden assignments.
- **F5 (ends).** Let M pass through V_1 and N through V_m, both different from L, with m ≥ 2. Suppose M's + ray at V_1 is
  unbounded (no vertex on it). Then all crossings of M other than V_1 lie on its − ray. Suppose N's − ray at V_m is
  unbounded. Then all crossings of N other than V_m lie on its + ray. M∩N lies on M's − ray and N's + ray, but these
  are on opposite sides of L, and M∩N ∉ L because M ≠ N and both cross L at different points. Contradiction. So
  ¬(ub_first(+) ∧ ub_last(−)) and ¬(ub_first(−) ∧ ub_last(+)). For triple ends "any hidden ray" is enough: the argument
  applies to any pair (M, N).
- **F6 (triple vertex).** Six rays and six sectors as in §1. A ray is doubly used iff its two adjacent sectors are
  triangles. A hidden ray on side + that is unbounded forces h+ = 0 and one adjacent segment bit to be 0
  (`frame_ok`). Interior triple frames drop their ub flags (normalisation, a coarsening). Only the end vertices keep
  them, since the end fact F5 is the only place they matter.
- **F7 (simple W has a vertex).** For n ≥ 3, W crosses the other lines, so at least one of its two rays at V contains a
  vertex: ub ≠ (1,1).
- **F8 (T1 / F in bit form).**
  - *L = cap of the block on u+ at V.* The block's flankers are the neighbours V_{i±1}. The triangle (+,left) has
    vertices P, V, V_{i−1}, and its side [P, V_{i−1}] is the first segment of the flank ray; symmetrically on the
    right. The gap-end ray of L at V_{i−1} towards X is s_{i−1}, so it is N iff s_{i−1} is not doubly used, i.e. bb_in = 0.
  - *L = axis of the block on E (X = next vertex, simple).* The flankers are the far ends Y± of E±, which lie on the cap C,
    consecutive with X. The gap ray of C at Y+ towards X is C+ = [X, Y+]. Its two faces are the triangle above s_i and
    the face above s_{i+1}. So it is N iff Y+ is triple and tb(s_{i+1}) = 0.
  - *L's N ray flanks a block on E+ (F).* The flankers are next (far end of E) and the far end of W+ (hidden). The gap
    ray at next is its W+ ray, doubly used iff h+(next) = 1, since tb_in(next) = tb_out(cur) = 1.

## 3. Soundness validation (mandatory part)

`validate` extracts the true frames and hidden values from `Charge`/`Arr` for every line of every arrangement.
- It checks: each frame is enumerated; each edge is allowed; the ends are compatible; the parity n−1 ≡ #S; the true
  hidden tuple is inside `sig_domain`.
- It checks: the window sum of `exact_vec` equals the reference (p, 2(v_L+1), nRN, nRR, nT) *exactly*.
- The extraction itself asserts that sector bits agree with segment bits and with each other, so the side conventions
  are validated as well.

**Result, on the final code:** 128,513 distinct arrangements, of which 55 are odd-n (pilot, n = 11) and the rest are even
n = 10…18, with 2,158,133 lines and **0 failing lines**. Inputs:
- work/phi/*.jsonl (all nine files)
- work/bbl/lineadv/pilot.jsonl
- gallery data/{10,12,14,16,18} and the variant dirs 10-2, 10-4, 12-4, 14-4, 14-6, 16-4, 16-7, 18-1, 18-4, 18-6, 18-9

374 words were skipped because some pair never crosses (the "-k" variant dirs contain incomplete words, so they are not
pseudoline arrangements). Skipped as well: arrangements with a 4-fold point (`Charge` raises).

**Planted mutations (detected):**

| mutation | failing lines |
|---|---|
| T1-cap coefficient 3→2 | 2,670 / 2.16M |
| T1-cap needs only one triple neighbour | 301 / 24k |
| T1 axis needs "or" instead of "and" | 300 / 24k |
| drop F payments | 893 / 24k |
| F ignores the gap clause | 8 / 2.16M |
| drop touches | 23,745 / 24k |
| forced-sig too strong | 2,339 / 24k |
| adjacency rule too strong | 392 / 24k |
| nRN/nRR count | 250 / 24k |

See planted.log and planted_full.log.

**DP cross-check.** `crosscheck` is an independent layered DP by exact length (no graph, no Bellman–Ford). It agrees on
all finite minima (M1: 1 and 0; M2a (1,3): 0; X-only: 0). For the −∞ cases the layered value falls linearly with length
(−4, −8, −10 at length ≤ 6, 10, 12).

**Coverage** (coverage.log):
- Frames: 145 enumerated (24 S, 121 T); **122 occur in data**.
  - All 23 unseen frames are T frames carrying ub flags, which only matter at triple end vertices (the S frame with
    both W rays unbounded is now excluded by F7). Every enumerated S frame and every T frame without ub flags occurs
    in data.
- Windows: 4,379 distinct windows in data, versus about 51k enumerated (bounded enumeration). The rest are combinations
  of hidden bits and neighbour infos that the over-approximation allows but real arrangements never show.
- The 4-triangle simple vertex S[(1,1)(1,1)] does occur (90 times), so the T–S(1,1)–T kite cannot be excluded locally.

## 4. Milestones

### M1 (L3 for all even n) — done

Clean line = no multiple point and no capped block (tb_in·tb_out = bb_in·bb_out = 0 at each vertex).

| n | min portions over all locally consistent clean lines of every length |
|---|---|
| even (m = n−1 odd) | **1** |
| odd | **0** |

The odd-n witness has 4 vertices, with the unbounded rays on the same side. The result is exact for all lengths
(BF and layered DP agree).

Ablation: dropping the end-compatibility fact F5 makes the even-n minimum 0. So P1 (alternation and parity) and P2 (end
rays) are automatic in the bit formalism, and F5 is what closes the argument. Human version: with no unused segment, the
sides alternate. For m−1 segments with m odd the end triangles are on opposite sides. By F2, the far rays at the ends
are unbounded on the opposite sides −σ and +σ, which contradicts F5.

This M1 is valid for any multiplicity (only simple vertices on L are used).

The pure-line refinements (M2d) also hold:
- Even n, no multiple point, an even number of capped blocks ⇒ ≥ 1 portion.
- An odd number of capped blocks allows 0.
- A pure cap with p = 0 caps only status-I blocks: with a bounded segment beyond X (status U/M) the minimum is ≥ 1.

### M2 (certified lower bounds for v_L after T1 and F, all n) — done for multiplicity ≤ 3

**M2a.** Table: min over all locally consistent lines, of every length, of v_L + (a/2)·#unserved RN + (b/2)·#unserved RR.
The result is the same for all n and for even n.

| a \ b | 0 | 1 | 2 | 3 | 4–6 |
|---|---|---|---|---|---|
| 0 | −∞ | −∞ | −∞ | −∞ | −∞ |
| ≥ 1 | −∞ | −∞ | −∞ | **−1** | −1 |

So **v_L + ½·#(unserved RN) + 3/2·#(unserved RR) ≥ −1** is certified, and both coefficients are sharp:
- With b ≤ 2 the negative cycle is T[(1,1)(1,1) h(1,1)] – S[(1,1)(1,1)] – … (the kite line).
- With a = 0 the negative cycle is T[h=(0,1)] with S[(1,1)(0,1)], S[(0,1)(1,1)].

Data minimum of v_L + comp over a 25% sample (32k arrangements, 539k lines) is exactly −1.0, so the bound is attained.
The same sample has min v_L = −2.

Consequences:
- Lines with a triple point and no unserved RN/RR block have v_L ≥ −1 (M2e; witness: an X axis with p = 0).
- Lines whose only triple points are isolated X points have raw v_L ≥ −1 (M2c).

**M2b.** X-point axes (both L-rays B, neighbours simple, h = 0). Certified bound on v_L + comp for lines containing such
a point, by block statuses (W side, E side), versus the data minimum on the sample:

| statuses | certified | data |
|---|---|---|
| (U,U) | 2.0 | 3.0 |
| (I,U) | **1.0** | 1.0 |
| (M,U) | 0.5 | 1.0 |
| (I,M) | **−0.5** | −0.5 |
| (M,M) | −1.0 | 0.0 |
| (I,I) | 0.0 (n odd only; n/a for even n) | not seen |

In particular the axis of an X point whose other block is U has v_L + comp ≥ 1/2, and ≥ 1 when the partner is I.

**Limits of the relaxation (honest).** Without compensation the bound is −∞ (M2f). The negative cycle is the kite
T–S(1,1)–T: a line alternating triple points and simple vertices with all four faces around each simple vertex
triangles. It is locally consistent, and S[(1,1)(1,1)] does occur in data (90 times), so no *local* fact can remove it.
Excluding it needs a global argument. The compensation terms are exactly the ones that make it neutral.

### M3 — not done

search/bbl_rules2.py was still work in progress while I was working (last modified 19:21).
- R3 chooses donors by comparing a density ρ(d) on other lines, and R4 is a flow over relation neighbours. Both need
  worst-case (nondeterministic) donor values on other lines.
- R1 and R2 could be modelled (R2 is a local ray rule), but R1's donor and amount depend on |capped blocks| of a
  *different* line. So verifying "every line ends ≥ 0" needs a structural form of the rules first (T18).

The automaton has the required hooks: `feat`, `cnt` and per-window options.

## 5. Scope and caveats

- Multiplicities ≤ 3 for M2 (as in bbl_hall.py). M1 holds for any multiplicity.
- The bounds are relaxations: real lines can be strictly better. Only proven implications were imposed. Realizability
  of frames or windows was not used. Unseen windows are unrealised combinations.
- Hidden g is fixed to 0 in the DP (monotone), and sig is constrained only by F3′ and F4. More facts (for example
  relations between sig and far-end structure) would sharpen the bounds but are not needed for M1 and M2.
- Frames at ends (first and last vertices) keep their ub flags. At interior triple vertices the flags are dropped.
- The end fact F5 pairs only the two end vertices of L. No other cross-window correlation is modelled.
