# CH05 — Thread-Level Parallelism (Summary)

> Source: **ch05-thread-level-parallelism.pdf** (Chapter Five, © 2019 Elsevier Inc.)  
> Generated: 2026-02-21 (America/Vancouver)  
> Focus: **Multiprocessors/multicores**, cache coherence (snooping + directory), synchronization, memory consistency, multithreading, and limits to scaling.

---

## 0) What this chapter is really teaching you

Thread-Level Parallelism (TLP) is how modern systems keep improving performance when **single-core ILP improvements hit diminishing returns** and power limits. The chapter frames the “modern multicore era” as a shift of responsibility:

- Hardware used to chase **ILP**; now it increasingly relies on **TLP**.
- Two big performance enemies in multiprocessors:
  1) **Insufficient parallelism** (Amdahl’s Law + workload structure)
  2) **Long-latency remote communication** (especially when memory is distributed)  
  The chapter repeatedly returns to “make more accesses local” and “hide/tolerate remote latency”.

---

## 1) Section map (use this as your roadmap)

- **5.1** Introduction  
- **5.2** Centralized Shared-Memory Architectures  
- **5.3** Performance of Symmetric Shared-Memory Multiprocessors  
- **5.4** Distributed Shared-Memory & Directory-Based Coherence  
- **5.5** Synchronization: The Basics  
- **5.6** Models of Memory Consistency (Intro)  
- **5.7** Cross-Cutting Issues  
- **5.8** Putting It All Together: Multicore Processors & Performance  
- **5.9** Fallacies & Pitfalls  
- **5.10** The Future of Multicore Scaling  
- **5.11** Concluding Remarks  

---

## 2) 5.1 Introduction: why multiprocessors dominate now

### 2.1 Two software models for TLP
The chapter treats “multiprocessors” as shared-address-space systems controlled by one OS and highlights two common TLP models:

1) **Parallel processing**: many threads collaborate on one task.
2) **Request-level / multiprogramming**: many relatively independent processes/requests run concurrently.

### 2.2 Remote communication can dominate fast
A key “feel the pain” example: a 32-processor machine with **100 ns remote memory delay** at **4 GHz**.

- Cycle time = 0.25 ns  
- Remote access cost ≈ 100 ns / 0.25 ns = **400 cycles**
- If base CPI = 0.5 and **0.2%** of instructions are remote references:

\[
CPI = BaseCPI + (Remote\_rate)	imes(Remote\_cost\_cycles)
     = 0.5 + 0.002	imes 400 = 1.3
\]

So the “no communication” case is **2.6× faster** (1.3 / 0.5).  
This is the chapter’s recurring warning: **tiny remote fractions can be huge**.

### 2.3 How the chapter attacks the problem
- **5.2–5.4**: reduce remote access frequency using **caching + coherence**
- **5.5**: synchronization (necessary, but a major bottleneck risk)
- **5.6**: **latency hiding** + **consistency models**
- **5.8**: real multicore case studies + measured performance

---

## 3) 5.2 Centralized shared-memory: snooping coherence (the “classic SMP”)

### 3.1 Central idea
With a shared bus (or shared last-level cache), **all caches “snoop”** coherence transactions. An invalidate-based protocol is the baseline.

### 3.2 Invalidations + cache-block states
Invalidate protocols are easiest to reason about as **per-cache-block state machines**:
- *Local* events (processor read/write) move the block through states.
- *External* events (bus transactions) force state changes to preserve coherence.

A simple baseline is MSI-like:
- **M**odified: dirty, this cache “owns” newest data
- **S**hared: clean, can exist in multiple caches
- **I**nvalid: not present

Many real protocols add:
- **E** (exclusive clean) state, to avoid an upgrade miss when only one sharer exists.
- **O** (owned) state, to allow dirty sharing patterns without immediate writeback.

### 3.3 Why centralized snooping stops scaling
Snooping’s advantage is simplicity (no centralized directory structure).  
Its weakness is scalability: **every miss (especially writes) tends to involve everyone**, so broadcast traffic explodes as core count grows.

---

## 4) 5.3 SMP performance: miss taxonomy + coherence misses

### 4.1 Total miss rate = uniprocessor misses + coherence misses
The chapter emphasizes separating:
- **3C misses** (compulsory, conflict, capacity) — the “uniprocessor” view
- **Coherence misses** — extra misses caused by sharing and invalidations

### 4.2 Coherence misses split into True Sharing vs False Sharing

**True sharing misses** (real communication):
- First write to a shared block triggers invalidations to gain ownership
- Later reads of modified data by other cores miss and trigger transfers  
These are “fundamental” to shared-memory communication.

**False sharing misses** (pure overhead):
- Happens because coherence is tracked per **cache block** (one valid bit/line),
  so an update to one word invalidates other words in the same line.
- The line “looks shared”, but no word is actually shared; the miss disappears if the line were a word.

The chapter gives a concrete classification example with two words in the same block: writes to z1 can invalidate z2 and cause z2 misses that are *false sharing*.

### 4.3 Cache size / processor count / block size trade-offs (the real story)
Key observation: as you add cores, **memory access cycles grow**, often mainly due to increased **true sharing** traffic. When you change block size:
- Bigger blocks can reduce compulsory misses and sometimes reduce true sharing misses (if sharing is spatially clustered),
- But bigger blocks can **increase false sharing** and increase **bytes transferred** per miss.

One key data point for OLTP-like workloads:
- Increasing L3 block size lowers misses per 1000 instructions and can make a case for at least ~128B blocks.
- However, measured breakdown notes:
  - compulsory miss rate decreases
  - capacity/conflict decreases slightly
  - **false sharing nearly doubles** (even if small in absolute terms)
  - instruction spatial locality can be surprisingly poor for some commercial/OS-heavy code

The big design warning: improvements for one core can be erased by **increased traffic and contention** when many cores share memory resources.

### 4.4 OS & multiprogrammed workloads are brutal
The chapter’s multiprogrammed “compile + OS activity” case study highlights:
- OS behavior can be more memory demanding than the user workload.
- Block size changes can reduce misses, but may still increase traffic.
- Systems may need the OS/compiler/programmer to communicate “this memory will be overwritten; don’t preserve it” to reduce unnecessary coherence work.

---

## 5) 5.4 DSM & directory-based coherence (scale beyond snooping)

### 5.1 Why directories are needed
Snooping requires contacting “everyone” on misses; this is cheap for small systems but becomes the **Achilles’ heel** at scale.

Modern designs also require more bandwidth than a single shared memory system can provide; thus systems distribute memory across nodes/sockets. Distributing memory helps only if we also avoid global broadcasts on coherence.

### 5.2 Directory concept (minimum mental model)
A **directory** is metadata (often at the home node / LLC slice) that tracks:
- which caches have the block (sharers)
- which cache has ownership (modified/exclusive)
- the block’s state (uncached/shared/modified)

Then coherence actions become targeted:
- On a write miss: invalidate only the sharers listed in the directory.
- On a read miss to modified data: forward data from the owner (or force writeback), directed by the directory.

This converts “broadcast per miss” into “messages proportional to sharers”.

---

## 6) 5.5 Synchronization: the basics (and why it’s unavoidable)

### 6.1 Why synchronization is everywhere
The chapter bluntly states: **most programs are synchronized**; without synchronization, races can make behavior unpredictable and reasoning difficult even under strong models.

Most programmers therefore use **standard synchronization libraries**, because rolling your own is tricky, bug-prone, and may not be architecturally portable across generations.

### 6.2 Atomic primitives: EXCH / CAS / LL-SC
Synchronization is built on an atomic read-modify-write primitive, such as:
- **Exchange (EXCH)**: atomically swap register value with memory
- (Modern systems also use CAS or LL/SC variants)

### 6.3 Spin locks: “simple” vs “optimized”
The chapter’s canonical RISC-V-like pseudocode:

**Simple spin lock (hammering EXCH):**
```text
addi x2, x0, #1
lockit: EXCH x2, 0(x1)
bnez x2, lockit
```

**Optimized spin lock (test-and-test-and-set):**
```text
lockit: ld x2, 0(x1)
bnez x2, lockit
addi x2, x0, #1
EXCH x2,0(x1)
bnez x2, lockit
```

Why optimized helps:
- Threads spin on a **shared read** (cacheable) rather than repeatedly generating atomic RMW traffic.
- Dramatically reduces coherence/invalidations during contention.

### 6.4 Scaling warning (implicit takeaway)
Spin locks can become a bottleneck; as contention grows, you need more scalable primitives (queue locks, backoff, hierarchical locks, etc.) and careful placement to avoid false sharing in lock variables.

---

## 7) 5.6 Memory consistency models: “what order is legal?”

Coherence tells you “all cores see a single value per location (eventually)”.  
**Consistency** tells you “what order of reads/writes can be observed across locations”.

### 7.1 Sequential consistency (SC)
SC requires maintaining all four orderings:
- **R→W**, **R→R**, **W→R**, **W→W**

A practical impact: simple SC implementations often stall reads behind writes (no aggressive write buffering / bypassing).

### 7.2 Relaxed models (why they exist)
Relaxed consistency allows reads/writes to complete out-of-order for performance, but requires synchronization operations to enforce the needed ordering so **synchronized programs behave as-if SC**.

The chapter classifies relaxed models by which of the four SC orderings they relax:

1) **TSO / processor consistency**: relax **W→R** only  
   - Writes stay ordered; many SC-style programs keep working with little change.

2) **PSO**: relax **W→R** and **W→W**

3) **Weak / PowerPC / Release Consistency (RC)** (and RISC-V’s model): relax all four orderings, relying heavily on synchronization.

### 7.3 Release Consistency (RC) in one paragraph
RC distinguishes synchronization operations:
- **SA (acquire)**: take access to a shared object/critical section
- **SR (release)**: publish updates and let others acquire

RC is based on a disciplined programming property:
- acquire must come **before** using shared data
- release must come **after** updates and before the next acquire

RC can therefore allow:
- reads/writes **before** an acquire to not necessarily complete before the acquire
- reads/writes **after** a release to not necessarily wait for the release

This enables optimizations like **write buffers** and even **read bypass** of buffered writes (allowed in RC but not in strict SC implementations).

The chapter explicitly notes that **RISC-V, ARMv8, and the C/C++ language standards chose release consistency** because of the performance advantages and because synchronized programs can still be made to appear SC.

---

## 8) 5.7 Cross-cutting issue: inclusion + directories in real chips

A concrete hardware example: inclusive cache hierarchies can simplify coherence.
- Many designers implement **inclusion**, often by using one block size across cache levels.
- Example: Intel i7 uses inclusion for L3 — L3 includes all of L2 and L1.
  - This supports a straightforward directory at L3 and reduces unnecessary snoop interference.
- AMD Opteron example: L2 inclusive of L1, but L3 not necessarily inclusive; snoops can be targeted differently.

---

## 9) 5.8 Putting it all together: multicore + SMT measurements

### 9.1 SMT in the wild: IBM Power5
Power5 is dual-core with **SMT**. Measurements on an 8-processor Power5 system (1 core active per chip) showed:
- **SPECintRate ≈ 1.23×** average speedup with SMT
- **SPECfpRate ≈ 1.16×** average speedup with SMT
- Some FP benchmarks slightly *slow down* under SMT, consistent with memory-system limits being stressed under extra thread pressure.

### 9.2 General SMT intuition you should remember
SMT helps when:
- the pipeline frequently stalls (e.g., cache misses), and a second thread can fill bubbles

SMT hurts when:
- both threads contend for the same scarce resources (L1/L2 bandwidth, memory bandwidth, issue width), so interference dominates.

---

## 10) 5.9 Fallacies & pitfalls (exam-friendly)

### Pitfall: judging multiprocessors by “linear speedup curves”
Speedup is not a direct measure of performance:
- 100 low-power cores scaling perfectly can be slower than 8 high-performance cores.
- Comparing speedups across systems can be misleading.

Key vocabulary:
- **relative speedup**: same program on different core counts
- **true speedup**: best algorithm/program on each machine (the fair comparison)

### Pitfall: “superlinear speedup” means magic
Superlinear speedup often indicates an unfair comparison or cache-capacity effects (critical data fits only when aggregate cache grows).

### Fallacy: “Amdahl’s Law doesn’t apply”
Amdahl still applies; serial/less-parallel portions still cap speedup. Claims of “breaking Amdahl” usually mean the serial fraction changed (e.g., algorithm improvements), not that the law vanished.

---

## 11) 5.10 The future of multicore scaling (and why it’s hard)

### 11.1 Multicore doesn’t automatically solve power
The chapter emphasizes:
- Multicore increases transistor count and the number of switching transistors.
- Dennard scaling failure makes power constraints harsher.
- Power gating + turbo enables trade-offs: fewer active cores at higher frequency vs more cores at lower frequency.

### 11.2 Amdahl + power constraints can kill “more cores”
A concrete example in the chapter compares a “96-core future processor” (but only ~54 cores busy on average due to varying parallelism) against a “24-core version”. The analysis shows:
- The 96-core version achieves only **<2×** speedup over the 24-core version under the given usage fractions.
- Clock-rate increases can rival core-count scaling gains.

### 11.3 Burden shifts to software
Multicore shifts “keeping the machine busy” to the programmer/application via TLP. Workloads that naturally avoid Amdahl effects (multiprogrammed, request-level parallel) benefit most.

### 11.4 Speculative threading isn’t paying off (so far)
Thread-level speculation ideas (speculative threads, run-ahead) have not become mainstream because the performance gains tend to be modest while energy costs rise—similar to the limits of aggressive ILP speculation.

### 11.5 The implied path forward
The chapter points to:
- **SIMD/data parallelism** (Chapter 4) as an energy-efficient form of parallelism,
- **warehouse-scale / cloud** (Chapter 6) where tasks are independent and Amdahl matters far less,
- and **domain-specific architectures** (Chapter 7).

---

## 12) Practical checklists (what to do as an engineer)

### 12.1 Avoiding false sharing (high ROI)
- Pad/align per-thread counters so two threads don’t update different words in the same cache line.
- Use per-thread local accumulation + final reduction (minimize shared writes).
- Keep locks/flags on their own cache lines (cache-line alignment).

### 12.2 Reducing remote communication
- Place data so threads mostly hit local memory (NUMA-aware allocation).
- Increase reuse: cache-friendly layouts, blocking/tiling, avoid pointer chasing in shared hot paths.
- Use read-mostly sharing patterns when possible.

### 12.3 Synchronization hygiene
- Use standard primitives/libraries (mutex, RW lock, barriers) unless you *must* implement custom.
- Prefer test-and-test-and-set style spinning over “hammering atomics”.
- Reduce lock hold time; avoid global locks in hot paths.

### 12.4 Consistency model hygiene
- Don’t assume SC unless your ISA guarantees it (many don’t).
- Use acquire/release primitives correctly; it’s the portable way to get SC-like behavior for synchronized code.

---

## 13) Flashcards (fast recall)

**Q1. Two biggest multiprocessor performance challenges?**  
A. Insufficient parallelism (Amdahl) and long-latency remote communication.

**Q2. True sharing vs false sharing?**  
A. True sharing is real data communication; false sharing is extra misses from block-granularity invalidations when different words in the same block are used by different cores.

**Q3. Why does snooping scale poorly?**  
A. Broadcast-like traffic on every miss/write; everyone must observe coherence events.

**Q4. What’s a directory’s job?**  
A. Track sharers/owner per block so coherence actions target only relevant caches.

**Q5. Why is test-and-test-and-set better than pure exchange spinning?**  
A. It spins on shared reads and performs atomics only when lock might be free, reducing coherence storms.

**Q6. What orderings does SC enforce?**  
A. R→W, R→R, W→R, W→W.

**Q7. TSO relaxes which ordering?**  
A. W→R.

**Q8. Why is release consistency popular?**  
A. Enables performance optimizations while ensuring synchronized programs can behave as-if SC when acquires/releases are used correctly.

**Q9. Typical SMT outcome?**  
A. Helps hide stalls, but may hurt if memory bandwidth or cache contention dominates.

---

*End of Chapter 5 summary.*
