# Chapter 3 — Instruction-Level Parallelism and Its Exploitation (Summary)

> Source PDF: `ch03-instruction-level-parallelism-and-its-exploitation.pdf`  
> Note: I did **not** receive `extraction_prompt.md` in the uploaded sources, so I used a consistent “engineering notebook” format: concepts → mechanisms → trade-offs → rules of thumb → flashcards.

---

## 0) What this chapter is really teaching you

Instruction-Level Parallelism (ILP) is about getting **more useful work per cycle** from a single core.  
Chapter 3’s message is:

- ILP exists, but **dependences + branches + memory** limit it hard.
- You can exploit ILP with:
  1) **compiler scheduling** (static),  
  2) **dynamic scheduling** (out-of-order), and  
  3) **speculation** (execute past unresolved control).
- Past a point, “wider + deeper + more speculative” becomes a **complexity/power trap**, and **caches/memory** dominate.

---

## 1) ILP foundations: dependences vs hazards (Section 3.1)

### 1.1 Loop-level parallelism vs ILP
A loop can have *independent iterations* (parallel loop-level work), but inside one iteration you may have little overlap. The chapter shows that you often convert loop-level parallelism into ILP by **unrolling** (compiler) or **dynamic unrolling** (hardware).

### 1.2 The three dependences
Dependences are properties of the **program** (semantic constraints). Hazards/stalls are properties of the **pipeline implementation**.

1) **True data dependence** (RAW dependence): value produced by i is needed by j.  
2) **Name dependence** (fake dependence):
   - **WAR** (antidependence): j writes a name that i reads.
   - **WAW** (output dependence): i and j write same name.
   These can be removed by **renaming**.
3) **Control dependence**: instruction execution is guarded by a branch; violating it means executing instructions that “shouldn’t run” unless you can roll back.

### 1.3 Hazard taxonomy (pipeline view)
Given i precedes j in program order:

- **RAW (read-after-write)**: j reads before i writes → wrong old value.
- **WAW (write-after-write)**: j writes before i writes → final value wrong.
- **WAR (write-after-read)**: j writes before i reads → i reads wrong new value.  
  (Typically appears with reordering or unusual read/write stage timing.)

Key implication: **WAW/WAR are about names, not values**, so renaming can eliminate them.

---

## 2) Basic compiler techniques to expose ILP (Section 3.2)

### 2.1 Scheduling (instruction reordering)
Goal: keep the pipeline busy by moving independent instructions into stall “bubbles” while preserving true dependences.

A classic example loop (load → FP add → store + pointer update + branch) illustrates:
- **unscheduled** execution inserts stalls after load and FP add,
- **scheduled** version moves pointer update early to reduce stalls.

### 2.2 Loop unrolling
Unrolling increases straight-line code, which:
- reduces **branch overhead**,
- exposes more ILP across iterations,
- but increases **code size** and **register pressure** (more live values).

### 2.3 Register pressure (why unrolling can backfire)
Aggressive unrolling/scheduling increases the number of simultaneously-live values; if registers run out, spills can destroy the theoretical gain.

---

## 3) Reducing branch costs with advanced prediction (Section 3.3)

Branches break instruction fetch and create control stalls. Two levers:
1) **predict better**, and
2) **fetch/steer faster** (handled later in 3.9).

### 3.1 Correlating predictors and (m, n) notation
A correlating predictor uses recent outcomes of *other* branches (global history) to improve accuracy.

- In an **(m, n)** predictor:
  - m = number of global history bits used,
  - n = number of bits in the saturating counter per entry,
  - total bits scale like:  
    \[
    2^m \times n \times \text{(# entries selected by branch address)}
    \]

### 3.2 gshare (the baseline)
**gshare** hashes branch PC bits with global history (XOR) to index a table of 2-bit counters. It’s simple and strong, so it’s used as a baseline.

### 3.3 Tournament predictors
A tournament predictor uses multiple predictors (often local + global) and a chooser that learns which predictor to trust per branch.

### 3.4 Tagged hybrid predictors (PPM-inspired) / TAGE-family ideas
As of the chapter’s framing (circa 2017):
- top predictors combine multiple global-history tables of varying lengths,
- they include **tags (≈4–8 bits)** so predictions are used only when the tag matches the branch context,
- selection uses the “best / longest history” matching entry.

Key intuition: tags reduce harmful **aliasing** (reusing the same prediction entry for unrelated branches).

---

## 4) Dynamic scheduling: why out-of-order exists (Section 3.4)

A simple in-order pipeline stalls on dependences even when independent work exists later. Dynamic scheduling tries to:
- keep **in-order issue** (often),
- but allow **out-of-order execution** when operands are ready.

Benefits highlighted:
- binary compiled for one pipeline can run well on another (less compiler retargeting),
- can tolerate unpredictable delays (esp. cache misses) by running independent instructions,
- helps with dependences unknown at compile time (memory aliasing, data-dependent control).

---

## 5) Tomasulo’s algorithm (Section 3.5)

Tomasulo’s approach is dynamic scheduling + dynamic renaming.

### 5.1 Core structures
- **Reservation stations (RS)**: hold an operation until operands are ready.
- **Tags**: identify “who will produce this operand” (acts as a virtual register name).
- **Common Data Bus (CDB)**: broadcasts completed results; RS entries “snoop” and capture values.

### 5.2 What Tomasulo eliminates
- **RAW hazards**: delayed execution until operands available.
- **WAR/WAW hazards**: eliminated via **dynamic renaming** (tagging destinations with RS/Buffer IDs).

### 5.3 Loads/stores in Tomasulo
- Address computed first → then placed into load/store buffers.
- Maintaining memory order and alias safety is tricky:
  - load/store reordering is allowed only when it won’t violate true dependences through memory.

### 5.4 Important cost: extra latency vs simple forwarding
Because results are broadcast and captured at “write result,” dynamic scheduling often adds at least **~1 cycle of effective producer→consumer latency** compared to a simple in-order forwarded pipeline.

---

## 6) Hardware-based speculation (Section 3.6)

Dynamic scheduling alone still respects control dependences by not *executing* beyond unresolved branches. Speculation goes further.

### 6.1 What speculation adds
Speculation = **fetch, issue, execute** along predicted control flow *as if* predictions are correct, with rollback if wrong.

The chapter frames speculation as combining:
1) **dynamic branch prediction** (choose path),
2) **speculative execution** (execute before control resolved, with undo),
3) **dynamic scheduling** (manage mixed basic blocks).

### 6.2 Commit: the key extra phase
To support rollback + precise exceptions:
- instructions may execute out of order,
- but must **commit in order**,
- and cannot make irrevocable state changes until commit.

This requires a **Reorder Buffer (ROB)** to hold results and bookkeeping until it’s safe.

### 6.3 ROB intuition
- ROB entries act like extra registers for in-flight instructions.
- Result forwarding can use ROB values even while speculative.
- At commit (head of ROB), architectural state is updated; if mispredicted, ROB state is flushed/rolled back.

### 6.4 Exceptions + speculation
You can’t take exceptions early if the instruction might later be squashed.
Typical policy: record the exception, then raise it only when the instruction reaches commit and is known non-speculative.

---

## 7) Multiple issue: getting CPI < 1 (Sections 3.7–3.8)

If you issue only 1 instruction per cycle, CPI can’t go below 1. Multiple-issue architectures allow >1 issue per cycle.

### 7.1 Three flavors
1) **Statically scheduled superscalar** (usually narrow; e.g., 2-issue)
2) **VLIW / EPIC** (compiler packs explicit parallel ops)
3) **Dynamically scheduled superscalar** (out-of-order, speculative)

### 7.2 VLIW trade-off
Pros:
- simpler hardware issue logic (compiler does the scheduling),
- high peak issue possible.

Cons:
- heavy compiler burden; binary compatibility across implementations is hard,
- sensitive to stalls/latency variation unless the ISA provides mitigation (predication/speculation support).

### 7.3 Wide out-of-order is issue/commit limited
For wide issue, the bottleneck becomes:
- detecting dependences *within the issue bundle*,
- renaming (mapping arch regs → physical/virtual regs) in essentially one cycle,
- plus similar complexity at commit/retire.

---

## 8) Advanced instruction delivery & speculation (Section 3.9)

Multiple-issue cores need **instruction bandwidth** (often 4–8 per cycle). Branches are the main obstacle.

### 8.1 Branch-Target Buffer (BTB)
A BTB is a cache indexed by the fetch PC:
- if the PC hits, it identifies the instruction as a predicted-taken branch and supplies the predicted next PC immediately.
- correct hit + correct prediction ⇒ near-zero branch penalty (in the simplified model).

### 8.2 Simple expected penalty example (from the chapter)
If:
- BTB hit rate on taken branches = 90%
- prediction accuracy for BTB entries = 90%
- penalty for “BTB wrong” cases = 2 cycles

Then expected branch penalty is:
- P(in BTB but actually not taken) = 0.9 × 0.1 = 0.09
- P(taken but not in BTB) = 0.10
- penalty = (0.09 + 0.10) × 2 = **0.38 cycles/branch**

### 8.3 Branch folding
If BTB stores target instructions (not just target address), some unconditional branches (and occasionally conditional) can be “folded” to 0-cycle.

---

## 9) Multithreading (Section 3.11)

Multithreading is introduced as a cross-cutting way to use **thread-level parallelism** to hide pipeline/memory latencies.

### 9.1 Hardware requirement
Duplicate per-thread architectural state:
- separate PC + register state per thread,
- fast thread switch (much cheaper than full process switch),
- OS/VM support already provides shared address space mechanisms.

### 9.2 Three approaches
1) **Fine-grained MT**: switch threads every cycle (round-robin, skip stalled threads)  
   - hides short + long stalls well  
   - hurts single-thread latency (each thread gets fewer issue slots)

2) **Coarse-grained MT**: switch only on long stalls (e.g., L2/L3 miss)  
   - better single-thread latency than fine-grained  
   - but less effective at hiding short stalls; start-up bubbles after switch

3) **Simultaneous Multithreading (SMT)**: built atop wide out-of-order  
   - dynamic scheduling + renaming lets independent threads fill execution slots  
   - in practice, many designs fetch/issue from one thread at a time, but allow execution from multiple threads once in the window  
   - needs per-thread rename maps + PCs + commit support for multiple contexts

### 9.3 Measured effect (i7 example in chapter)
For a set of parallel apps + multithreaded Java workloads, SMT on one core showed:
- ~**1.28×** harmonic-mean speedup for the Java set,
- ~**1.31×** for PARSEC-like apps,
- energy efficiency gains depended heavily on whether the workload had real parallelism (some multithreaded programs gained little and lost energy efficiency).

---

## 10) Putting it together: ARM Cortex-A53 vs Intel Core i7-6700 (Section 3.12)

### 10.1 ARM Cortex-A53 (in-order dual-issue)
- Dual-issue, statically scheduled, scoreboard-based issue detection.
- Branch handling uses multiple predictors with different delays:
  1) **Single-entry branch target cache** (stores two I-cache fetches) → on hit + correct, **0-cycle** branch delay.
  2) **3072-entry hybrid predictor** (F3) → **2-cycle** delay on correct prediction.
  3) **256-entry indirect predictor** (F4) → **3-cycle** delay on correct prediction.
  4) **8-deep return stack** (F4) → **3-cycle** delay on correct prediction.

Key point: shallow-ish pipeline + decent prediction ⇒ modest pipeline losses, but stalls from cache/TLB misses still matter.

### 10.2 Intel Core i7-6700 (aggressive out-of-order + speculation)
- Deep speculative out-of-order design optimized for high throughput.
- Approx. **17-cycle** branch misprediction penalty (order-of-magnitude).
- Front-end highlights:
  - fetch block (e.g., 16 bytes) into predecode buffer,
  - **macro-op fusion** (certain instruction pairs fuse),
  - decode into micro-ops (RISC-like internal ops), with a microcode engine for complex ops,
  - rename/allocate ROB entries, dispatch to reservation stations, execute, then **retire/commit** from ROB head.

Generational improvements from i7-920 → i7-6700 were largely about:
- larger windows/buffers (more in-flight work),
- better branch prediction,
- better cache/prefetch behavior,
- and generally fewer stalls.

---

## 11) Fallacies & pitfalls worth remembering (Section 3.13)

### Fallacy: “Lower CPI always means faster.”
### Fallacy: “Higher clock rate always means faster.”
Reality: performance depends on **CPI × clock cycle time** (or CPI / frequency). Deep pipelines can raise CPI via hazards/mispredict penalties; a high clock alone can lose.

### Pitfall: “Bigger and dumber is better” (sometimes)
When memory dominates, spending transistors on:
- bigger caches / better memory hierarchy  
can beat spending transistors on deeper/wider speculative ILP machinery.

### Pitfall: “Smarter can beat bigger”
Example framing: tagged hybrid predictors can beat simpler predictors (like gshare) even with the same storage budget by reducing aliasing via tags.

### Pitfall: “There’s tons of ILP if we just try hard enough”
Classic studies show that even highly idealized wide-issue machines hit ceilings due to:
- limited independent work in conventional code,
- control dependences,
- and especially memory latency.

---

## 12) Compact carry-forward summary (low-context version)

- **Dependences** constrain correctness; **hazards** are pipeline artifacts.  
- **RAW** is real; **WAR/WAW** are name dependences that renaming can remove.  
- Compiler ILP: scheduling + unrolling (watch **register pressure**).  
- Branch prediction evolves: 2-bit → gshare/tournament → tagged hybrids/TAGE-like.  
- Dynamic scheduling (Tomasulo): RS + tags + CDB; hides latency but adds complexity/latency.  
- Speculation requires **in-order commit** via **ROB** for rollback/precise state.  
- Wide issue hits hard limits in **issue/rename/commit complexity** and power.  
- Multithreading (fine/coarse/SMT) exploits TLP to fill bubbles from stalls.  
- Pitfalls: don’t worship CPI or GHz; memory + branch behavior often decides.

---

## 13) Flashcards (quick recall)

**Q1. What’s the difference between dependence and hazard?**  
A. Dependence is a program property (semantic ordering). Hazard is a pipeline timing conflict that can cause wrong results unless the pipeline stalls/renames/reorders safely.

**Q2. Which hazards are removed by register renaming?**  
A. WAR and WAW (name dependences). Not RAW.

**Q3. What extra phase does speculation require beyond “execute”?**  
A. **Commit** (in order), typically via a **reorder buffer**.

**Q4. Why does a BTB help?**  
A. It identifies branches early and provides the predicted next PC before decode, reducing branch fetch bubbles.

**Q5. Why is wide issue hard even if you can duplicate ALUs?**  
A. Issue logic must find intra-bundle dependences and rename/register-map in (effectively) one cycle; commit must retire in order and manage state recovery.

**Q6. How do fine-grained MT and SMT differ?**  
A. Fine-grained MT switches threads every cycle (interleaving), usually on simpler cores; SMT sits on out-of-order multiple-issue cores and uses renaming/scheduling to mix threads to fill execution slots.

---

*End of Chapter 3 summary.*
