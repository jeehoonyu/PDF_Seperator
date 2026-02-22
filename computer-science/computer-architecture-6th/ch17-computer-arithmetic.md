# CH17 — Computer Arithmetic (Appendix J) (Summary)

> Source PDF: `ch17-appendix-j-computer-arithmetic.pdf`  
> Note: In this PDF set, “Chapter 17” corresponds to **Appendix J: Computer Arithmetic**.

---

## 0) What this appendix is really teaching you

Computer arithmetic is not “just math.” It’s a set of **representations + algorithms + hardware trade-offs** that determine:

- correctness (overflow, rounding, exceptions, NaNs),
- performance (adder/multiplier/divider latency and throughput),
- and portability (IEEE 754 behavior across systems).

If you can do these three things, you “own” Appendix J:
1) Predict and reason about **IEEE 754** results (rounding + special values + exceptions).  
2) Explain why floating-point **add is harder than multiply** (alignment + cancellation + normalization).  
3) Recognize the classic speedups: **carry-lookahead / carry-select**, **Booth + Wallace tree / CSA**, **SRT / iterative division**, **FMA**.

---

## 1) J.2 — Basic techniques of integer arithmetic

### 1.1 Full adder (3,2) building block
A full adder takes inputs (a, b, cin) and outputs (s, cout):
- `s = (a + b + cin) mod 2`
- `cout = floor((a + b + cin)/2)`

The *system* problem is carry propagation across n bits.

### 1.2 Ripple-carry adder (baseline)
- n full adders chained.
- Latency grows **O(n)** because the carry must ripple through all bits in the worst case.

### 1.3 Two’s complement and overflow
Two’s complement is the default signed-integer representation.
Overflow detection (signed add):
- adding two positives gives a negative, or
- adding two negatives gives a positive
(i.e., carry into MSB differs from carry out of MSB).

Unsigned overflow is simply the carry out of MSB.

### 1.4 Multiplication: shift-and-add
Classic sequential multiplier:
- examines multiplier bits;
- conditionally adds multiplicand shifted by bit position;
- shifts partial product each step.

It produces ~1 bit per cycle (slow but simple).

### 1.5 Booth recoding (reduce additions for signed multiplication)
Booth recoding replaces runs of 1s by fewer operations using ±b.
Radix‑4 Booth (“overlapping triplets”) examines 3 bits to choose among:
- 0, ±b, ±2b  
It roughly halves the number of add/sub steps compared to bit-at-a-time methods.

### 1.6 Division: restoring vs nonrestoring
Sequential division also produces ~1 quotient bit per iteration.
- **Restoring**: if subtract goes negative, restore by adding divisor back.
- **Nonrestoring**: alternates add/sub without restoring every time; fixes sign at end.

### 1.7 Multiple-precision arithmetic note
Many ISAs provide “add-with-carry” (add three operands: a, b, carry-in).
Pitfall: you must update array pointers without destroying the carry bit.

---

## 2) J.3 — Floating point (IEEE 754 core concepts)

### 2.1 Why IEEE 754 exists
IEEE 754 standardizes:
- formats,
- rounding modes,
- special values (±0, ±∞, NaN, denormals/subnormals),
- and exception flags.

It is designed so computations usually **continue** even under exceptional conditions, while flags record what happened.

### 2.2 Normal numbers: sign, exponent, significand
A binary float is:
\[
x = (-1)^{sign} \cdot significand \cdot 2^{exponent}
\]
For normalized numbers the significand is **1.f** (implicit leading 1).

### 2.3 IEEE format parameters (from Figure J.7)
Important parameters:

- **Single precision**: `p = 24` bits of precision, `Emax = 127`, `Emin = -126`, exponent bias **127**.  
- **Double precision**: `p = 53` bits of precision, `Emax = 1023`, `Emin = -1022`, exponent bias **1023**.  
- Extended formats: listed but not fully specified; concept is “carry extra bits to reduce rounding problems.”

### 2.4 Special exponent encodings (Figure J.8 idea)
Let `e` be the **biased exponent field**:

- `e = 0`, `fraction = 0` → ±0
- `e = 0`, `fraction ≠ 0` → **denormal/subnormal**: `0.f × 2^{Emin}` (gradual underflow)
- `e = all 1s`, `fraction = 0` → ±∞
- `e = all 1s`, `fraction ≠ 0` → **NaN** (many NaN payloads exist)

### 2.5 Rounding modes (IEEE)
IEEE supports 4 rounding modes:
1) round to nearest (ties to even) **(default)**
2) round toward 0
3) round toward +∞
4) round toward −∞

“Ties to even” prevents statistical bias (e.g., 3.05 rounds to 3.0, not 3.1).

---

## 3) J.4 — Floating-point multiplication

A multiply:
\[
(s_1 \cdot 2^{e_1})\cdot(s_2 \cdot 2^{e_2}) = (s_1 s_2)\cdot 2^{e_1+e_2}
\]

Algorithm outline:
1) Multiply significands (integer multiply).  
2) Add exponents (with bias correction).  
3) Normalize if needed (product may be in [1,4)).  
4) Round to p bits (needs guard/round/sticky logic).  
5) Handle overflow/underflow/denormals.

### Rounding with guard/round/sticky
The appendix formalizes the classic GRS scheme:
- keep extra bits from the product,
- use a **round digit** and a **sticky bit** (OR of all remaining bits) to decide if increment is required,
- handle carry-out from rounding (may renormalize, affecting exponent).

### Overflow and underflow
- Overflow check must occur **after rounding** (rounding can produce carry-out).
- Underflow must account for denormals: exponent below Emin may still yield a nonzero subnormal by right shifting significand until exponent reaches Emin.

---

## 4) J.5 — Floating-point addition (why it’s harder than multiply)

Addition requires **alignment** of exponents, and subtraction can cause **cancellation**.

The appendix gives an 8-step algorithm (high value; this is the exam-style procedure):

1) If `e1 < e2`, swap operands (so `d = e1 - e2 ≥ 0`). Tentatively set result exponent = `e1`.  
2) If signs differ, two’s-complement `s2` (turn add into subtract).  
3) Shift `s2` right by `d`, collecting **g, r, s** (guard, round, sticky).  
4) Add `S = s1 + s2`. If signs differ and sum negative, take two’s complement of S (only when d=0).  
5) Normalize:
   - if same-sign and carry-out → shift right by 1, increment exponent
   - else shift left until normalized (cancellation case), adjusting exponent; first left shift shifts in `g` once.
6) Update `r` and `s` based on how normalization shifted (different cases for right shift vs left shift count).  
7) Round according to rounding mode using (r,s) and LSB rules.  
8) Set final sign based on operand signs and whether complement/swap occurred.

Key takeaways:
- **Subtraction cancellation** can cause many left shifts → large exponent decreases → precision loss.
- You do not need the full exact sum; p bits + GRS are enough to decide rounding.

---

## 5) J.6 — Division and remainder

### 5.1 Iterative division (Newton and Goldschmidt)
The appendix highlights two fast division strategies that use multiplication:

**Newton’s iteration** for reciprocal:
- For `f(x) = 1/x - b`, iteration yields:
\[
x_{i+1} = x_i(2 - x_i b)
\]
Correct bits roughly **double each iteration**. Early iterations can use reduced precision.

**Goldschmidt’s algorithm**
- Multiply numerator and denominator by factors driving denominator toward 1:
  - `x_{i+1} = r_i x_i`, `y_{i+1} = r_i y_i`, with `y_i → 1`
- Related to unrolled Newton form.

Trade-offs:
- avoids special divide hardware,
- but IEEE requires **correct rounding**, which is nontrivial with pure iteration.

### 5.2 Floating-point remainder (IEEE REM)
IEEE defines remainder using round-to-even on the quotient integer:
- choose `n = INT(x/y)` such that `|x/y - n| ≤ 1/2`, ties to even,
- then `REM = x - y n`
Result satisfies `|REM| < y/2` (unlike integer remainder, which is < y).

---

## 6) J.7 — More on floating-point arithmetic

### 6.1 IEEE exception flags
IEEE defines flags (and optional traps):
- **invalid** (e.g., √−1, 0/0, ∞−∞)
- **divide-by-zero** (1/0 → ∞, with flag distinguishing from overflow-to-∞)
- **overflow**
- **underflow**
- **inexact** (rounding occurred or overflow rounded)

Important practical note: trapping on inexact is usually disastrous for performance because it happens frequently.

### 6.2 Fused multiply-add (FMA)
FMA computes:
\[
a\times b + c
\]
with **one final rounding**, avoiding an intermediate rounding step. This:
- improves numerical accuracy,
- can help implement correctly rounded division and sqrt (via correction steps),
- and improves performance for dot products and polynomial evaluation.

### 6.3 Extended precision and double rounding
Extended precision can simplify algorithms (binary↔decimal conversion, transcendental functions, stable geometric computations).
But **double rounding** can occur when:
- an intermediate is rounded to extended precision,
- then rounded again to target precision,
potentially producing a different result than direct rounding to target precision.

---

## 7) J.8 — Speeding up integer addition

This section is all about reducing carry propagation delay.

### 7.1 Carry lookahead (CLA)
Define per-bit:
- `p_i = a_i + b_i` (propagate)
- `g_i = a_i b_i` (generate)

Then carries can be computed in parallel:
\[
c_{i+1} = g_i + p_i c_i
\]

Group propagate and generate:
- `P_{j,k} = p_j p_{j+1} … p_k`
- `G_{j,k} = g_k + p_k g_{k-1} + … + p_k…p_{j+1} g_j`

Tree structures compute carries in **O(log n)** depth.

### 7.2 Carry-skip
Carry-skip computes only block propagate P:
- ripples within a block,
- but if P is true, the carry can “skip” the whole block quickly.
Good when ripple is fast and block-carry reset/precharge is easy.

### 7.3 Carry-select
Compute sum twice (carry-in=0 and carry-in=1) and mux-select once carry is known.
- Very effective when muxing is cheap (signal can drive many muxes).
- Optimal block sizes matter; hybrids are common.

### 7.4 Carry-save adders (CSA) (note: CSA name conflict!)
Be careful:
- **carry-save adder** is a (3,2) adder used heavily in multiplication trees (J.9).
- **carry-skip adder** is not called CSA (to avoid confusion).

---

## 8) J.9 — Speeding up integer multiplication and division

### 8.1 Shift over zeros (operand-dependent time)
Skip addition steps when multiplier bits are 0.
Not widely used:
- variable-time behavior is hard to pipeline and optimize,
- speedup usually insufficient.

### 8.2 Faster multiplication with one adder
Two major improvements:
1) **carry-save accumulation** (store sum and carry separately to avoid carry propagation each step)  
2) **higher-radix Booth recoding** (radix-4 uses digits −2…+2 via ±b and ±2b)

### 8.3 Faster multiplication with many adders
- **Array multiplier**: regular structure, pipelinable, good throughput.
- **Wallace tree**: log-depth reduction using (3,2) adders; very fast but irregular layout.
- **Signed-digit tree**: more regular log-depth design using signed-digit adders; needs extra encoding bits and conversion to two’s complement at end.

### 8.4 Faster division (SRT + redundancy)
**SRT division** uses redundant quotient digits (e.g., −1, 0, +1) to allow quotient selection without exact remainder.
- quotient digit chosen from a small table using a few high bits of remainder and divisor.
- redundancy allows carry-save remainder representation, enabling faster hardware.

---

## 9) J.10 — Putting it all together (chip comparison)

The appendix compares three IEEE FP chips (historical but conceptually valuable):
- **Weitek 3364**
- **MIPS R3010**
- **TI 8847**

Key lesson: even under similar constraints, designers choose very different algorithms:
- different adders (e.g., carry-select vs carry-lookahead),
- different multiplier organizations (trees, pipelining strategies),
- different division approaches and internal precision (e.g., carrying extra bits to ensure correct rounding).

---

## 10) J.11 — Fallacies and pitfalls (what to not mess up)

- **“Floating-point math is associative.”**  
  False: `(a+b)+c` may differ from `a+(b+c)` due to rounding and cancellation.

- **“IEEE guarantees identical results everywhere.”**  
  Not always: extended precision, compiler reordering, FMA contraction, and different math-library argument reduction can change results (even if all are IEEE-compliant).

- **“Round once is the same as round twice.”**  
  False: double rounding can change results.

- **“Ignoring denormals is harmless.”**  
  Flushing-to-zero changes numerical behavior near underflow; IEEE gradual underflow is more predictable.

- **“Division is just multiplication by reciprocal.”**  
  IEEE requires correct rounding; reciprocal approximations need careful correction (FMA often helps).

---

## 11) Flashcards (quick recall)

**Q1. Single vs double precision p and bias?**  
A. Single: p=24, bias=127; Double: p=53, bias=1023.

**Q2. What are denormals/subnormals for?**  
A. Gradual underflow: represent values below 1.0×2^Emin by using 0.f × 2^Emin.

**Q3. IEEE rounding modes?**  
A. nearest-even, toward 0, toward +∞, toward −∞.

**Q4. Why is FP add harder than FP multiply?**  
A. Must align exponents, manage subtraction/cancellation, normalize (possibly left shifts), and then round.

**Q5. What are guard/round/sticky bits used for?**  
A. Decide rounding direction without computing the full exact infinite-precision result.

**Q6. Newton reciprocal iteration formula?**  
A. x_{i+1} = x_i(2 − x_i b).

**Q7. What does FMA buy you?**  
A. One final rounding → higher accuracy; enables correction steps for division/sqrt.

**Q8. CLA vs ripple?**  
A. Ripple is O(n) carry; CLA uses propagate/generate to compute carries in O(log n).

**Q9. Radix‑4 Booth selects which multiples?**  
A. 0, ±b, ±2b (using overlapping triplets).

**Q10. Why SRT uses redundant quotient digits?**  
A. Allows quotient selection without exact remainder; enables carry-save remainder and faster division.

---

## 12) One-page carryover (low-context)

- Integers: ripple add (slow), Booth+CSA/trees for fast multiply, nonrestoring/SRT for divide.  
- IEEE FP: sign + biased exponent + fraction with implicit leading 1; special e=0 and e=all-1s encodings; denormals; 4 rounding modes; exception flags.  
- FP multiply: multiply significands, add exponents, normalize, round (GRS), then handle overflow/underflow.  
- FP add: align, add/sub, normalize, update GRS, round; cancellation is the enemy.  
- Fast adders: CLA, carry-skip, carry-select, hybrids.  
- Fast multiply: Booth recoding, Wallace/array/signed-digit trees, CSA accumulation.  
- Fast divide: Newton/Goldschmidt (iterative) and SRT (table-based quotient digits); FMA can help with correct rounding.

---

*End of CH17 / Appendix J summary.*
