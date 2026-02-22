# CH09 — Review of Memory Hierarchy (Appendix B) (Summary)

> Source PDF: `ch09-appendix-b-review-of-memory-hierarchy.pdf`  
> Note: In this PDF set, “Chapter 9” corresponds to **Appendix B: Review of Memory Hierarchy**.

---

## 0) What this appendix is really teaching you

Memory hierarchy performance is not magic — it’s a **small set of reusable models** plus a handful of **engineering trade-offs**.

You should leave this appendix able to do three things reliably:

1) **Predict performance** from cache/TLB parameters (hit time, miss rate, miss penalty).  
2) **Explain misses** (compulsory/capacity/conflict; and for VM: page faults).  
3) **Choose optimizations** that target the right term (miss rate vs miss penalty vs hit time), without breaking correctness.

---

## B.1 Roadmap (sections)

- **B.1** Introduction  
- **B.2** Cache Performance  
- **B.3** Six Basic Cache Optimizations  
- **B.4** Virtual Memory  
- **B.5** Protection and Examples of Virtual Memory  
- **B.6** Fallacies and Pitfalls  
- **B.7** Concluding Remarks  
- **B.8** Historical Perspective + Exercises

---

## B.2 Cache performance (the core equations)

### 1) Cache indexing / organization
For a cache with:
- size = `CacheSize` bytes
- block size = `BlockSize` bytes
- associativity = `A` (ways)

Number of sets:
\[
\#sets = \frac{CacheSize}{BlockSize \cdot A}
\]

Index size is based on:
\[
2^{Index} = \frac{CacheSize}{BlockSize \cdot A}
\]

(Bigger cache → bigger index; bigger block or bigger associativity → smaller index.)

### 2) Average Memory Access Time (AMAT)
The basic performance model:

\[
\textbf{AMAT} = \text{Hit time} + (\text{Miss rate}) \cdot (\text{Miss penalty})
\]

- **Hit time**: time to access cache on a hit (often 1–few cycles in L1).
- **Miss rate**: misses / accesses (for that cache).
- **Miss penalty**: extra time to service a miss from the next level (often 100s of cycles to DRAM).

### 3) CPU time with memory stalls
A common decomposition:

\[
CPU\ time = \frac{CPU\ cycles + Memory\ stall\ cycles}{Clock\ rate}
\]

Memory stall cycles:
\[
Memory\ stall\ cycles = \#misses \cdot Miss\ penalty
\]

Often expressed per instruction:

\[
Memory\ stall\ cycles/inst = Misses/inst \cdot Miss\ penalty
\]

and

\[
Misses/inst = Miss\ rate \cdot (Memory\ accesses/inst)
\]

So:

\[
Memory\ stall\ cycles/inst = Miss\ rate \cdot (MemAccess/inst)\cdot Miss\ penalty
\]

### 4) In-order vs out-of-order caution (what “miss penalty” means)
For **in-order** cores: miss penalty ≈ full miss latency (stall until data arrives).

For **out-of-order** cores: the relevant “miss penalty” is the **non-overlapped latency** (the part the core cannot hide).  
So you think in terms of *exposed stalls*, not raw memory latency.

---

## B.3 Six basic cache optimizations (mapped to AMAT terms)

The appendix organizes the optimizations by which AMAT component they improve:

### A) Reduce **miss rate**
1) **Larger block size**  
   - reduces compulsory misses (spatial locality)  
   - can increase miss penalty (more bytes) and can increase conflict/capacity pressure if blocks get too large relative to cache

2) **Larger cache size**  
   - reduces capacity misses  
   - but bigger caches can increase hit time and power; beyond some point, thrashing indicates cache is far too small

3) **Higher associativity**  
   - reduces conflict misses  
   - can increase hit time (more tag comparisons / muxing), and can impact clock frequency

#### The 3C model (how to “explain” misses)
Misses can be categorized as:
- **Compulsory** (cold-start / first reference)
- **Capacity** (working set too large for cache)
- **Conflict** (mapping collisions in direct-mapped / set-associative caches)

### B) Reduce **miss penalty**
4) **Multilevel caches**  
   - use a small fast L1 and a larger slower L2 to reduce the average penalty seen by the CPU  
   - important concept: L2 miss rate can be discussed as:
     - **local miss rate**: misses_L2 / accesses_L2  
     - **global miss rate**: misses_L2 / accesses_from_CPU = MissRate_L1 · MissRate_L2

   Two-level AMAT form:
\[
AMAT = HitTime_{L1} + MissRate_{L1}\cdot\big(HitTime_{L2} + MissRate_{L2}\cdot MissPenalty_{L2}\big)
\]

   Policy note:
   - **Inclusion**: L1 contents are also in L2 (simplifies some coherence/management).
   - **Exclusion**: L1 blocks are not in L2; L1 miss can swap blocks with L2 (useful when L2 is only slightly larger than L1).

5) **Give reads priority over writes** (write buffering correctness + performance)  
   - Write buffers reduce write stall time, but introduce a hazard: a read miss could fetch stale data if a pending buffered write targets the same block.
   - Common solution: on a read miss, **check write buffer for conflicts**; if safe, allow read to proceed, otherwise wait / forward.

### C) Reduce **hit time**
6) **Avoid address translation in cache indexing** (virtually indexed caches)  
   Goal: allow cache lookup to start before (or in parallel with) TLB translation.

   Practical complications (why “pure virtual caches” are hard):
   - **Protection** checks are tied to translation.
   - Context switches: same virtual address maps to different physical pages → would require cache flush unless you add a **process identifier (PID/ASID)** tag.
   - **Synonyms/aliases**: two virtual addresses mapping to same physical address can create duplicated cache blocks with inconsistent values unless hardware “anti-aliasing” is used.

---

## B.4 Virtual memory (VM): concept + the 4 classic questions

### Why VM exists
VM lets each process believe it has a large private address space, while:
- providing **protection** (processes can’t corrupt each other),
- enabling **sharing** (shared code/data),
- allowing programs larger than physical DRAM (via disk/SSD backing),
- improving startup (demand paging).

### Terminology mapping (cache ↔ VM)
- cache “block” ↔ VM **page** (or **segment**)
- cache “miss” ↔ **page fault**
- translation ↔ address mapping (virtual → physical)

### Pages vs segments
- **Paging**: fixed-size blocks (commonly 4–8 KiB; sometimes multiple page sizes).
- **Segmentation**: variable-size blocks (needs segment number + offset; harder for replacement; mostly legacy/hybrid).

### The 4 memory-hierarchy questions (applied to VM)
1) **Where can a page be placed in physical memory?**  
   - VM miss penalty is huge (disk), so prefer flexibility that reduces page faults → fully associative placement is conceptually preferred.

2) **How is a page found?**  
   - Use **page tables** (or inverted tables) to map virtual page number → physical page frame number + protection bits.

3) **Which page is replaced on a miss?**  
   - OS tries to approximate **LRU** to minimize faults.
   - Hardware typically helps with **reference/use bits** (set on access, often via TLB behavior).

4) **What happens on a write?**  
   - VM systems use a **dirty bit** so pages are written to disk only if modified.

### The TLB (translation lookaside buffer)
Page tables are too big/slow to consult on every access, so translations are cached in a **TLB**:
- TLB tag: virtual page number (plus ASID/PID in many designs)
- TLB data: physical page frame number + protection + status bits

---

## B.5 Protection examples (why x86 got complicated)

This section contrasts:
- **IA‑32 (32-bit Intel x86)**: elaborate segmented protection scheme
- **AMD64 / Opteron-style 64-bit paging**: simpler, paging-centric protection like most modern OSes

### 1) IA‑32 segmentation (high-level idea)
Instead of segment registers containing bases directly, they contain selectors into **descriptor tables**.
A **segment descriptor** includes:
- present/valid
- base
- limit (bounds checking)
- accessed/use bit
- attributes (R/W, privilege level, etc.)

Advanced features discussed include **conforming code segments** and **call gates**:
- Call gates restrict where less-privileged code can enter privileged code (controlled entry point, safe parameter setup).
- This is powerful but complex; most modern OSes rely primarily on paging-level protection.

### 2) AMD64 / Opteron-style paging (mainstream model)
AMD64 in 64-bit mode largely abandons multi-segment complexity:
- segments assumed base=0; limits ignored (in 64-bit mode)
- page sizes include **4 KiB** and larger “huge pages” (e.g., 2 MiB / 4 MiB as noted)

Addressing:
- virtual address example in text: implementations often use **48-bit virtual**, **40-bit physical**
- “canonical form”: upper bits are sign-extension of lower 48 bits (for 48-bit VA implementations)

Page table structure:
- **multilevel hierarchical page tables** (example shown as 4 levels for 48-bit VA)
- each level indexed by a 9-bit field (in the example), then final PTE provides physical page frame number
- PTE bits include (conceptually):
  - present
  - read/write
  - user/supervisor
  - accessed
  - dirty
  - page size (for large pages)

TLB organization note:
- large systems reduce TLB misses with multi-level TLBs (e.g., separate L2 TLBs for I and D).

---

## B.6 Fallacies and pitfalls (exam-friendly)

### Pitfall: “not enough address bits”
The appendix calls this the **hardest-to-recover-from** design mistake:
- Address width limits maximum program + data footprint (`< 2^{address_bits}`).
- Changing address width later is painful because it touches everything: PC, registers, memory formats, arithmetic, instruction encodings.

(Example narrative: PDP‑11’s 16-bit address space was a fatal long-term limit even though it was otherwise successful.)

### Pitfall: believing in a single “typical program”
Cache and VM behavior varies a lot by workload; design must be robust across mixes.

### Pitfall: confusing local vs global miss rate (especially for L2)
- L2 “local” miss rate can look large because it sees only L1 misses.
- What matters for CPU stalls is the **global miss rate** seen by the CPU.

---

## B.7 Concluding takeaways

- **Locality** is the core justification for caches, TLBs, and VM working at all.
- Memory latency keeps growing in *cycles* as CPUs get faster; therefore:
  - programmers and compiler writers often must be aware of cache/TLB parameters for performance-critical code.
- The best “knobs” are still the classic ones:
  - reduce misses (miss rate), reduce penalties, reduce hit time — but improving one often hurts another.

---

## Flashcards (quick recall)

**Q1. AMAT formula?**  
A. `Hit time + Miss rate × Miss penalty`.

**Q2. Memory stall cycles per instruction?**  
A. `Misses/inst × Miss penalty = Miss rate × MemAccess/inst × Miss penalty`.

**Q3. 3C miss model?**  
A. Compulsory, Capacity, Conflict.

**Q4. Local vs global miss rate (L2)?**  
A. Local: misses/accesses to L2. Global: misses per CPU memory access = MissRate_L1 × MissRate_L2.

**Q5. Six basic cache optimizations?**  
A. Miss rate: larger blocks, larger cache, higher associativity.  
   Miss penalty: multilevel caches, read priority over writes.  
   Hit time: avoid translation in indexing (VIVT/VIPT ideas).

**Q6. Why are purely virtual caches difficult?**  
A. Protection checks, context switch flushing (unless ASID/PID tags), and alias/synonym problems.

**Q7. VM “miss” is called what?**  
A. Page fault.

**Q8. VM replacement goal?**  
A. Minimize page faults; approximate LRU with reference/use bits.

---

*End of Chapter 9 / Appendix B summary.*
