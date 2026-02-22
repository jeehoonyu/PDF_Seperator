# CH15 — Hardware and Software for VLIW and EPIC (Appendix H) (Summary)

> Source PDF: `ch15-appendix-h-hardware-and-software-for-vliw-and-epic.pdf`  
> Note: In this PDF set, “Chapter 15” corresponds to **Appendix H: Hardware and Software for VLIW and EPIC**.

---

## 0) What this appendix is really teaching you

VLIW/EPIC is “ILP the compiler can see.”

Instead of complex out-of-order hardware discovering parallelism at run time, **the compiler schedules instructions** into parallel groups. Hardware becomes simpler in some ways (less dynamic issue logic), but the system burden shifts to:

- proving loops are parallel (dependence analysis),
- restructuring control flow to expose large straight-line regions,
- placing instructions so that long latencies are hidden (software pipelining),
- and preserving correct behavior under speculation (exceptions + memory aliasing).

The appendix also uses **IA‑64 / Itanium** as the “capstone” example of EPIC.

---

## 1) H.1 — Introduction: exploiting ILP *statically*

### Why static ILP is hard
The compiler must work under uncertainty:
- branch outcomes are not always predictable,
- memory aliasing often can’t be proven away,
- and different microarchitectures change latency parameters.

### Why hardware support still matters
Even in static ILP systems, hardware features can dramatically increase what the compiler can safely do:
- predication (eliminate branches),
- speculation support (avoid exceptions on wrong-path),
- and memory-dependence speculation aids.

IA‑64 is presented as the fullest combination of “compiler + hardware support” for static ILP.

---

## 2) H.2 — Detecting and enhancing loop-level parallelism

### 2.1 Loop-carried dependence is the key blocker
A loop is parallelizable if it has **no loop-carried dependences** (later iterations depending on values from earlier iterations).

Example pattern:
```c
for (i=1000; i>0; i--) x[i] = x[i] + s;
```
- Dependence within iteration exists (read x[i], write x[i]) but is **not loop-carried**, so vectorization / unrolling can work.
- Dependence on induction variable `i` is loop-carried but “easy” (recognized and eliminated by compiler transformation).

### 2.2 Dependence types relevant to loops
- **True data dependences** block parallel execution across iterations.
- **Name dependences** (WAR/WAW) may be eliminated by **renaming** (compiler or hardware).
- Induction variable and indexing recurrences can often be minimized via algebraic rewrite + unrolling (e.g., summation reassociation reduces dependent chain length).

### 2.3 What compilers actually do (high-level)
- identify induction variables and strength-reduce address calculations,
- unroll to expose ILP and reduce branch overhead,
- transform reductions (sum, dot product) to reduce dependence height,
- attempt dependence testing for arrays (distance vectors, affine access patterns).

---

## 3) H.3 — Scheduling and structuring code for parallelism

This is the “compiler toolbox” section.

### 3.1 Software pipelining (symbolic unrolling)
Software pipelining rearranges a loop so that **different iterations overlap**:

- While iteration *k* is executing its add, iteration *k+1* is executing its load, and iteration *k−1* is executing its store.
- The result is a steady-state kernel with high throughput, plus:
  - **prologue** (ramp-up)
  - **epilogue** (drain)

The goal is to achieve an initiation interval close to 1 (or minimal possible) for the bottleneck resource.

**Key hazard:** register reuse across overlapped iterations can introduce WAR hazards unless handled (renaming or careful scheduling).

### 3.2 Trace scheduling
Trace scheduling uses profiling to build a high-probability **trace** (a path through multiple basic blocks), then schedules it as if it were straight-line code.

- It moves instructions across branch boundaries to improve the hot path.
- Requires **compensation code** at trace entry/exit to preserve correctness when execution diverges from the hot trace.

Trace scheduling works well when:
- profiles are stable,
- hot paths dominate,
- code is loop/trace-friendly (many scientific kernels).

It becomes complex and sometimes unattractive when:
- control flow is irregular,
- compensation code overhead is high.

### 3.3 Superblocks and hyperblocks
**Superblock**: a single-entry, multiple-exit region built by merging blocks on a hot path.
- Eliminates many trace-entry complications (fewer mid-trace entries).

**Hyperblock**: a superblock plus **if-conversion** (predication) to reduce control flow and allow even more code motion/scheduling.

The appendix positions these as a “modern alternative” to full trace scheduling, especially when predication is available.

---

## 4) H.4 — Hardware support: predicated instructions

### 4.1 Why predication matters
Control dependences (branches) are a major ILP killer:
- they stop code motion,
- and wide issue requires handling multiple branches per cycle (painful).

**Predication** converts control dependences into data dependences:
- an instruction executes, but its write-back occurs only if a predicate is true.

A common simple form is **conditional move**, used for patterns like:
```c
A = abs(B)
```
via a move plus a conditional move (or two conditional moves).

### 4.2 Benefits
- reduces branch frequency and misprediction penalty,
- enables larger straight-line regions for scheduling,
- improves software pipelining across conditional code.

### 4.3 Costs / limits (why you can’t predication-everything)
- if the predicate depends on data, you may introduce **data hazard stalls** where speculation could have avoided branch stalls.
- complex control flow may require combining predicates (extra instructions to compute compound conditions).
- predicated instruction forms may have extra cost (encoding, datapath gating, or timing), so most ISAs use predication selectively.

---

## 5) H.5 — Hardware support for compiler speculation

Compilers want to move loads and potentially faulting instructions upward to hide latency. But wrong-path speculation must not cause visible exceptions.

### 5.1 “Exception behavior” is the core problem
If an instruction is speculated and later squashed (or its result unused), it **must not** terminate the program or raise an architecturally visible fault.

The appendix lists several general approaches:

1) **Ignore exceptions for speculative ops** (hardware/OS cooperation)  
   Preserves behavior for correct programs but can mask some incorrect behaviors.

2) **Non-faulting speculative ops + explicit checks**  
   Execute a “safe” speculative instruction that never traps; later a check triggers recovery if needed.

3) **Poison/flag bits (“poisoned result”)**  
   Speculative fault sets a status bit on the destination; consuming that value later triggers a fault (or triggers recovery).

4) **Predication-based guarding**  
   Convert potential faulting operations into predicated ops when safe.

### 5.2 Memory dependence speculation (loads across stores)
Loads moved above stores can be wrong if their addresses alias.

To allow speculation when aliasing can’t be proven away:
- execute the load early,
- remember the load’s address,
- later check whether any intervening store wrote that address (or conflicting region).

If conflict detected → recovery path (re-execute or roll back).

---

## 6) H.6 — IA‑64 / Itanium: EPIC “in the real world”

This section ties the compiler ideas to an ISA and a specific microarchitecture.

### 6.1 Register architecture (why it’s unusual)

**Integer registers** include a **register stack** mechanism:
- registers are partitioned into:
  - local registers
  - output registers (for passing args)
- procedure calls update a frame marker so callee’s R32 maps to caller’s output area
- a hardware **Register Stack Engine (RSE)** spills/fills stack frames automatically as needed

Other register files:
- **floating-point registers**
- **predicate registers** (for predication)
- **branch registers** (for indirect branch targets)

### 6.2 Instruction grouping: bundles, templates, and stops
IA‑64 encodes instructions in **128-bit bundles**:
- 3 × 41-bit instruction “syllables”
- 5-bit **template** describes:
  - which execution unit types the 3 instructions require
  - where **stop bits** occur (boundary between instruction groups)

Stops mark where the compiler asserts that instructions cannot be executed in parallel across the boundary.

**Compiler responsibility:** pack independent instructions into bundles/groups and place stops correctly.  
**Hardware benefit:** simpler parallel issue decisions (less dependence discovery logic).

### 6.3 Speculation support via NaT bits (deferred exceptions)
IA‑64 uses **NaT (Not a Thing)** bits to record deferred exceptions from speculative operations.

- A speculative exception doesn’t immediately trap.
- Instead, destination register gets NaT/NaTVal.
- If a non-speculative instruction consumes NaT/NaTVal, it can raise an immediate exception, or:
- a compiler-inserted check (`chk.s` style) can detect NaT and branch to recovery code.

Because OS must save/restore state, IA‑64 includes special save/restore instructions that can handle NaT bits.

### 6.4 Advanced loads and ALAT (memory speculation support)
To move loads above stores safely, IA‑64 adds:
- **ld.a** (“advanced load”) which creates an entry in **ALAT** (Advanced Load Address Table)
- a later check verifies whether an intervening store invalidated the advanced load’s assumption
- if invalidated → recovery path

This is the canonical EPIC mechanism for memory dependence speculation.

### 6.5 Itanium 2 pipeline view (compiler meets real hardware)
The appendix breaks the Itanium 2 pipeline into 4 major parts:

1) **Front-end**: fetches bundles, branch prediction (multi-level adaptive predictor)
2) **Instruction delivery**: distributes to functional units; renaming (for rotation/stacking)
3) **Operand delivery**: register file + bypass; scoreboard to avoid stalling entire bundles when one op is delayed
4) **Execution/retire**: ALUs, load/store, exception detection, NaT posting, retirement/write-back

Important nuance: even EPIC designs often need dynamic mechanisms (scoreboarding) to cope with unpredictable events like cache misses. “Pure static scheduling” is not sufficient in real machines.

---

## 7) H.7 — Concluding remarks (the punchline)

- Static ILP approaches can expose substantial parallelism in regular code (especially loops), but require heavy compiler sophistication.
- Hardware features like predication and speculation support are essential to make static scheduling robust against real control flow and memory uncertainty.
- EPIC’s promise is better “compile-time parallelism” with less OoO hardware, but the costs include:
  - complex compilers,
  - binary compatibility challenges across microarchitectures,
  - and sensitivity to incorrect scheduling assumptions.
- In practice, modern CPUs combine both worlds:
  - compiler optimizations (unrolling, scheduling, vectorization),
  - plus dynamic execution machinery for the unpredictable parts.

---

## Practical checklists

### If you’re analyzing a VLIW/EPIC design
- What is the explicit parallelism model? (bundles/groups/stops?)
- What is the compiler’s scheduling unit? (basic block, superblock, hyperblock, trace?)
- How does the ISA support:
  - predication (predicate registers, conditional ops)?
  - speculation (non-faulting ops, poison bits, check instructions)?
  - memory speculation (advanced loads, address tables)?
- What happens when reality deviates (cache miss, unpredictable branch)?  
  Do you have scoreboarding / replay / dynamic stalls?

### If you’re writing a compiler/optimizer plan
- Identify loop kernels; prioritize modulo scheduling / software pipelining.
- Use superblocks + if-conversion where predication exists.
- Apply profile-guided optimization for trace formation when stable.
- Add alias info and memory-disambiguation to allow load hoisting safely.

---

## Flashcards (quick recall)

**Q1. What’s the defining VLIW idea?**  
A. The compiler schedules multiple independent operations into one wide “issue packet”; hardware issues them together with minimal dynamic scheduling.

**Q2. What does EPIC add beyond classic VLIW?**  
A. ISA features that help compilers expose ILP safely: predication, explicit parallel groups/stops, and speculation mechanisms (including memory speculation).

**Q3. What is software pipelining?**  
A. Scheduling loop instructions from different iterations to overlap in time, forming a steady-state kernel with prologue/epilogue.

**Q4. Why are superblocks useful?**  
A. Single-entry regions simplify scheduling vs full traces (fewer mid-trace entries/compensation complications).

**Q5. What is predication’s purpose?**  
A. Replace branches with predicated instructions to convert control dependences into data dependences and enlarge schedulable regions.

**Q6. Why is speculation tricky?**  
A. Wrong-path speculated instructions must not raise visible exceptions; architectures need deferred exception mechanisms or explicit checks.

**Q7. What are NaT bits (IA‑64)?**  
A. “Not a Thing” flags in registers indicating deferred exceptions from speculative operations; checked later for recovery.

**Q8. What is ALAT used for?**  
A. Track advanced loads (ld.a) so the machine can detect if a later store invalidated a speculated load (memory dependence speculation).

**Q9. How are IA‑64 instructions packaged?**  
A. 128-bit bundles: 3×41-bit syllables + 5-bit template indicating unit types and stop boundaries.

---

*End of CH15 / Appendix H summary.*
