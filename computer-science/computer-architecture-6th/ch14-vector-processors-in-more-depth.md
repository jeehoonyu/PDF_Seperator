# CH14 — Vector Processors in More Depth (Appendix G) (Summary)

> Source PDF: `ch14-appendix-g-vector-processors-in-more-depth.pdf`  
> Theme: vector machines are still about the same core idea—**one instruction controls many element operations**—but real performance depends on start-up costs, memory banking, and chaining/pipelining details.

---

## 0) What this appendix is really teaching you

A “vector ISA” is the easy part. The hard part is **sustained performance**:
- **start-up latency** (pipeline depth) can dominate at moderate vector lengths
- **memory banking + conflicts** decide whether you actually get 1 element/cycle
- **chaining** and **overlap** decide whether dependent ops behave like 1 convoy or multiple
- compilers determine whether real code runs in vector mode at all

This appendix gives:
- a more accurate performance model than the simple “chime” approximation,
- a deeper look at vector memory systems and bank conflicts,
- and a modern case study (Cray X1).

---

## 1) G.1 — Context (why this appendix exists)

Chapter 4 introduced vector/SIMD/GPU. Appendix G dives into:
- better timing models (start-up + loop overhead),
- vector memory banking in more detail,
- and concrete performance metrics used to compare vector machines.

---

## 2) G.2 — Vector performance in more depth

### 2.1 The chime model (baseline)
- A **chime** is one pass through the vector pipeline for a convoy.
- The chime model works best for **long vectors** where start-up is amortized.

But it ignores two big realities:
1) **vector start-up time** (pipeline fill latency)
2) overhead from **strip mining** and scalar loop control

### 2.2 Start-up time (the dominant overhead)
Start-up time comes from **pipeline depth**:
- if the initiation rate is 1 result/cycle, then pipeline depth roughly matches latency in cycles
- deeper pipelines → higher start-up

Typical pipeline depths vary widely (heavily used units ~4–8 stages; more complex ops can be deeper).

### 2.3 Strip mining and the “full” timing equation
Real loops usually don’t have length equal to MVL (maximum vector length), so they’re strip-mined.

The appendix gives a practical total time model for a vector sequence of length **n**:

\[
T_n \approx \left\lceil\frac{n}{MVL}\right\rceil\cdot (T_{loop}+T_{start}) + n\cdot T_{chime}
\]

Where:
- **MVL**: max vector length in elements
- **T_loop**: scalar overhead per strip-mined chunk (setup, pointer bumps, loop branch)
- **T_start**: vector start-up overhead per convoy sequence (pipeline startup, per instruction)
- **T_chime**: chimes per element (convoys per loop iteration, assuming 1 element/cycle per active pipeline)

**Interpretation:** even if you’re “3 chimes” theoretically, start-up can push sustained cost to 4+ cycles/element.

### 2.4 Dead time / recovery time
Some machines require **dead time** between issuing two vector instructions to the same unit (even if independent).  
Dead time reduces peak utilization, and the penalty gets smaller as:
- vector length grows, or
- the number of lanes grows (each instruction “occupies” the unit fewer cycles).

---

## 3) G.3 — Vector memory systems in more depth

### 3.1 Why banks exist
To sustain 1 word/cycle for loads/stores, memory must be **interleaved into banks** so consecutive accesses land on different banks.

If:
- each bank has access time **B** cycles,
- you want 1 access/cycle,

you need at least **B banks** for unit-stride access without stalls (in the simplest model).

### 3.2 Bank conflicts and stride
Bank conflicts disappear when:
- **stride** and **#banks** are relatively prime (and banks are sufficient for stride 1), but
- many strides (e.g., power-of-two strides) can collide badly with power-of-two bank counts.

Rules of thumb:
- **unit stride** is safest and fastest.
- prefer bank counts that reduce collisions for common non-unit strides.
- modern vector systems use **hundreds of banks** per CPU to lower conflict probability.

### 3.3 System-level reality: switching networks to banks
When you have many CPUs and many memory pipelines, you can’t hardwire every pipeline to every bank.
Instead, supercomputers use a **multistage switching network** between:
- vector memory pipelines and
- the set of memory banks.

This introduces an additional contention point: the switch network itself can congest.

---

## 4) G.4 — Enhancing vector performance (deeper than Chapter 4)

### 4.1 Chaining, but “for real”
Chaining reduces the **chime** component by allowing dependent vector ops to overlap (like forwarding).
But chaining does **not** eliminate **start-up overhead**. For accurate timing:
- count start-up within and across convoys.

Constraints:
- a convoy can’t contain a structural hazard (e.g., two vector loads if there’s only one load/store unit).

**Key point:** modern vector machines support *flexible chaining* because it’s essential.

### 4.2 Sparse matrices, conditionals, and gather/scatter
Sparse and irregular access patterns often break classic vectorization:
- conditional updates,
- indirect addressing through index arrays,
- non-unit stride accesses.

Two important techniques discussed:
1) **predicate/mask approaches** (execute but suppress updates)
2) **scatter-gather** (indexed loads/stores)

Scatter-gather can be much faster than scalar—even if slower than unit stride—when:
- the fraction of active elements is low, or
- the same index vector is reused, or
- the “if body” contains multiple vector ops (amortizing index cost).

### 4.3 “Vectorizing around potential dependences” (runtime checks)
Compilers may insert runtime checks to ensure that vectorized iterations don’t violate dependences (aliasing).
This is similar in spirit to an address-check mechanism:
- fast path: proceed at max MVL if no conflicts detected
- slow path: reduce vector length (or fall back) when conflicts occur

It adds overhead but can still beat scalar code when common case has no dependences.

---

## 5) G.5 — Effectiveness of compiler vectorization (why it fails)

Vectorization success depends heavily on:
- whether dependences are provably absent,
- whether memory access patterns are analyzable (unit stride / affine),
- whether control flow is regular,
- whether data types and alignment are friendly,
- and whether the compiler has enough context (e.g., non-aliasing info).

Practical takeaway: directives, annotations, and disciplined data layout often matter as much as hardware.

---

## 6) G.6 — Putting it all together: performance measures (VMIPS + DAXPY)

### 6.1 Why “MFLOPS for a loop” is reported
For vector loops, people often quote MFLOPS rather than time. That’s fine only if:
- FLOP count is clearly defined, and
- loop overhead is included.

### 6.2 Three “length-based” metrics used for vector machines
Given R∞ = peak MFLOPS on infinite vector length:

- **R∞**: infinite-length rate (mostly peak capability; not realistic alone)
- **N1/2**: vector length needed to reach half of R∞ (measures overhead sensitivity)
- **Nv**: vector length where vector mode beats scalar mode (measures scalar-vs-vector speed + overhead)

### 6.3 DAXPY on VMIPS (what the appendix demonstrates)
For a classic DAXPY inner loop (Y = aX + Y), the appendix shows:
- theoretical chimes can be optimistic,
- start-up + strip-mining overhead raise cycles/element,
- real vector lengths (e.g., average ~66 in Linpack) reduce sustained MFLOPS far below ideal peak.

### 6.4 Memory-limited loops: more memory pipelines help
DAXPY is often **memory bandwidth limited**.
Adding more memory pipelines (load/store bandwidth) can increase performance more than adding arithmetic units.

### 6.5 Overlapping convoys and “tailgating”
If the machine allows:
- overlapping convoys,
- overlapping scalar overhead with vector execution,
- and even overlapping strip-mined chunks,

then much of T_loop and multiple T_start components can be hidden.
This requires more complex issue logic (and hazard handling), but can yield large gains (historical example: “tailgating” approach in Cray-2).

---

## 7) G.7 — Modern vector supercomputer: Cray X1 (architecture highlights)

### 7.1 Multi-Streaming Processor (MSP)
Cray X1 groups four **Single-Streaming Processors (SSPs)** to form one **MSP**.

### 7.2 Ecache + line size choice
- Four SSPs share a **2 MB external cache (Ecache)**.
- 2-way set associative, 32-byte lines, write-back.
- ISA includes load/store variants that **don’t allocate** in cache to avoid polluting Ecache with streaming data.

The X1 uses **short 32B lines** to reduce wasted bandwidth on non-unit-stride patterns, and relies on many outstanding misses to tolerate latency.

### 7.3 Massive memory-level parallelism
A core differentiator: **outstanding memory requests**
- A superscalar CPU might support ~8–16 outstanding misses.
- An MSP supports **up to 2048 outstanding memory requests** (512 per SSP).
This is a vector-friendly way to hide long memory latency without huge cache lines.

### 7.4 Node-level memory bandwidth
An X1 node includes multiple MSPs and many memory controllers:
- each controller has multiple DRAM channels,
- the aggregate node memory bandwidth is **hundreds of GB/s** (order-of-magnitude takeaway: far above typical commodity servers of that era).

### 7.5 Two ways to use the MSP (important programming insight)
1) **Gang SSPs together** to emulate a wider-lane vector processor (e.g., 8 lanes).  
   - Works best when inner loops are long enough to keep all SSPs busy.
2) **Parallelize across outer loops** (task-level parallelism) when inner loops are short or triangular.  
   - Avoids wasting lanes on short vectors (where start-up dominates).

This is a recurring “vector reality”: lane width is only useful if you can feed it.

---

## 8) G.8 — Concluding remarks (modern relevance)

Key messages:
- Scalar CPUs closed the raw peak gap via high clocks and superscalar/OoO, but **memory bandwidth** remains the decisive advantage for vector supercomputers.
- Modern vectors use DRAM (SRAM is too expensive), so they must solve latency via banking + many in-flight requests.
- Meanwhile, commodity CPUs increasingly adopted vector ideas via SIMD extensions; GPUs further expanded wide-SIMD execution.
- If GPUs become tightly integrated with scalar cores and gain strong gather/scatter, it’s plausible to say “vector architectures won” in practice.

---

## Practical checklists

### If you are analyzing a vector loop
- Determine MVL and the expected vector length distribution (not just max).
- Count convoys → estimate T_chime.
- Include T_start and T_loop (strip mining + pipeline fills).
- Evaluate memory access pattern:
  - unit stride? good
  - fixed stride? check bank conflicts
  - indirect? consider scatter-gather cost and conflict probability

### If you are designing or tuning code for vector machines
- Make accesses unit stride whenever possible (layout transforms, blocking/tiling).
- Avoid power-of-two stride conflicts (especially for matrix columns).
- Reduce short-vector work; fuse loops or vectorize outer loops when possible.
- Provide compiler aliasing information (restrict, directives) to enable vectorization.

---

## Flashcards (quick recall)

**Q1. Why does the chime model overestimate performance?**  
A. It ignores vector start-up (pipeline fill) and strip-mining scalar overhead.

**Q2. What is the “full” vector timing model in this appendix?**  
A. \(T_n \approx \lceil n/MVL\rceil(T_{loop}+T_{start}) + n\cdot T_{chime}\).

**Q3. Minimum #banks to sustain 1 word/cycle if bank busy time is B cycles?**  
A. At least B banks (unit stride case).

**Q4. What are R∞, N1/2, Nv?**  
A. Infinite-length MFLOPS; length for half of R∞; length where vector beats scalar.

**Q5. Why are short cache lines used in Cray X1?**  
A. Reduce wasted bandwidth on non-unit-stride; rely on many outstanding misses for latency tolerance.

**Q6. Two ways to use an MSP?**  
A. Gang SSPs for wide vectors (long loops) or parallelize outer loops (short/triangular loops).

---

*End of CH14 summary.*
