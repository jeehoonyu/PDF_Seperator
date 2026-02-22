# CH16 — Large-Scale Multiprocessors and Scientific Applications (Appendix I) (Summary)

> Source PDF: `ch16-appendix-i-large-scale-multiprocessors-and-scientific-applications.pdf`  
> Note: In this PDF set, “Chapter 16” corresponds to **Appendix I: Large-Scale Multiprocessors and Scientific Applications**.

---

## 0) What this appendix is really teaching you

Large-scale parallel machines (dozens → tens of thousands of nodes) are dominated by **communication** and **synchronization**, not raw FLOPS.

For scientific/technical computing (“true parallel computing”):
- tasks **collaborate** on one application,
- so interprocessor communication is unavoidable,
- and performance hinges on the cost of moving data and coordinating.

This appendix gives you:
- a communication-performance framework (latency/bandwidth/overhead/occupancy/latency hiding),
- characteristic scientific workload patterns (FFT, LU, Barnes-Hut, Ocean),
- synchronization scaling laws (why naïve locks/barriers collapse),
- and the architectural consequences (DSM caching/coherence, directory protocols, deadlock avoidance),
- plus a customized-cluster case study (**Blue Gene/L**).

---

## 1) I.1 Introduction: why this domain differs from WSCs

**True parallel computing**: cooperating threads/tasks on one job (scientific/technical).  
Contrast: commercial request-level workloads (web/transactions) have little intertask communication, so commodity clusters are often enough.

Key implication:
- for scientific workloads, **communication hardware support** is “vital” to performance.

---

## 2) I.2 Interprocessor communication: the critical issue

### 2.1 Five metrics you should always separate
The appendix emphasizes that “communication performance” is multi-dimensional:

1) **Latency** (time to send a message, no contention)  
2) **Bandwidth** (peak and sustained transfer rate)  
3) **Overhead** (CPU time spent doing communication work)  
4) **Occupancy** (time during which a node resource is tied up, limiting concurrent work)  
5) **Latency hiding** (ability to overlap communication with computation or other comm)

Latency is crucial because, unless hidden, it directly forces cores to wait or ties up resources. Overhead and occupancy are linked: overhead often consumes node resources, lowering bandwidth.

### 2.2 Message passing vs shared memory (trade-offs)
Two primary communication models:

**Shared memory advantages (as listed):**
- compatibility with centralized multiprocessors + standard **OpenMP**
- easier programming for complex/dynamic communication
- work mostly in a familiar model and optimize only critical parts
- lower overhead for small items (implicit comm; protection via hardware mapping)
- caching can reduce remote comm frequency (but introduces coherence complexity)

**Message passing advantages (as listed):**
- simpler hardware than scalable coherent shared memory
- explicit comm is easier to reason about
- forces programmer attention on communication cost
- fault isolation is simpler (looser coupling)
- very largest machines are clusters anyway; one model can reduce complexity

Important asymmetry:
- implementing message passing **on top of shared memory** is relatively easy (copy memory→memory).
- implementing shared memory efficiently **on top of message passing** is much harder (coherence + caching semantics).

---

## 3) I.3 Characteristics of scientific applications

The appendix uses four representative scientific kernels/apps and highlights their parallelism + communication structure.

### 3.1 FFT kernel (all-to-all communication tendency)
- 1D complex FFT, sequential time ~ \(n\log n\)
- uses high radix to reduce communication
- for large n, communication patterns can become global (bisection-heavy)

### 3.2 LU factorization (dense linear algebra)
- runtime ~ \(n^3\); parallelism ~ \(n^2\)
- blocked algorithm improves locality (inner loop dominated by dense matmul)
- common block sizes: 8×8 or 16×16
- data distribution: 2D block tiling (“cookie cutter”) across processors to reduce communication

### 3.3 Barnes-Hut (irregular, hierarchical)
- N-body approximation using an octree (cells aggregate masses)
- traversal is irregular; control and memory access patterns are much less regular than LU/FFT
- parallelism exists, but communication is dynamic and depends on spatial distribution

### 3.4 Ocean (PDE grid / multigrid style)
- structured grid; nearest-neighbor stencil work with boundary exchanges between subgrids
- problem decomposed into square subgrids, ideally mapped to local memories
- communication is primarily boundary (“halo”) traffic, but convergence/iteration behavior can complicate scaling

### 3.5 Computation vs communication scaling example (Ocean)
The appendix includes a key illustrative example:

- On 4 processors: 20% time in communication, 80% compute.
- Move to 32 processors with same problem size:
  - Compute time scales ~1/8 (ideal)
  - Communication time grows ~ \(\sqrt{8}\) (illustrative assumption for increased comm)
  - Total time becomes:
    \[
    T_{32} = 0.8T_4/8 + 0.2T_4\sqrt{8} \approx 0.1T_4 + 0.57T_4 = 0.67T_4
    \]
  - Speedup ≈ 1.49×, and comm fraction becomes ~85%.
Lesson: with fixed-size problems, adding processors can **make comm dominate** quickly.

---

## 4) I.4 Synchronization: scaling up (why naïve primitives fail)

### 4.1 Spin locks under contention can explode (quadratic traffic)
For n processes contending for a lock on a bus with LL/SC:
- each contender repeatedly does:
  - load-linked
  - store-conditional
- plus one store to release

Total bus transactions:
\[
\sum_{i=1}^{n} (2i + 1) = n^2 + 2n
\]

Example in text: n=10 → 120 bus transactions; if each transaction costs 100 cycles → 12,000 cycles per lock acquisition (catastrophic).

### 4.2 Barriers also serialize
Simple barrier implementations often create:
- atomic updates (exclusive access contention) in the “gather” stage
- broadcast-like reads in the “release” stage

An example barrier count in the appendix:
- n fetch-and-increment ops
- n cache misses to access count
- n cache misses for release
→ about **3n bus transactions** (linear, but still painful at scale).

### 4.3 Better approaches (software + hardware)
The appendix describes improvements:

**Software techniques**
- **Exponential backoff** for locks (delay grows when acquisition fails) to reduce bus storms.
- Array-based / queuing approaches can reduce contention at unlock time.

**Queueing locks (concept)**
- waiting processors form a queue; unlock wakes the next
- avoids “thundering herd” contention when lock becomes free
- can be implemented with:
  - a synchronization controller (directory/memory controller), or
  - software arrays (esp. bus-based machines)

**Combining tree barriers**
- hierarchical reduction-style barrier to reduce hot-spot serialization.

Takeaway: scalable synchronization is about **avoiding global hot spots**.

---

## 5) I.5 Performance of scientific apps on shared-memory multiprocessors

### 5.1 Miss decomposition matters (capacity vs coherence)
For studies across FFT/LU/Ocean/Barnes, the appendix decomposes cache misses into:
- “capacity-like” (including conflict/compulsory; compulsory is small here)
- **coherence misses** (including upgrade misses even when no other core shares; protocol simplification)

As processors increase (1 → 16), total cache increases:
- capacity misses often drop, but coherence misses can dominate eventually (Barnes is a striking example).

### 5.2 Block size trade-off in multiprocessors
Increasing cache block size can:
- reduce misses (spatial locality)
- but increase **false sharing** and reduce spatial locality for shared data
- and increase **bytes transferred per miss**, which can saturate the bus/network and slow down the system.

Appendix shows:
- miss rate trends vs block size (Barnes: miss rate drops then rises due to coherence/false sharing)
- bus traffic grows steadily with block size, hurting high-miss-rate codes (Ocean particularly sensitive).

### 5.3 DSM (directory-based) view: local vs remote misses
In directory-based multiprocessors, performance depends on:
- fraction of misses that are **local** vs **remote**
- remote misses consume global bandwidth and add latency.

A worked bandwidth example (FFT):
- if 0.7% of references are remote and per-node ref rate is 1 GB/s, remote demand ~448 MB/s per node
- bisection demand for 64 nodes becomes ~28.7 GB/s (orders beyond standard networking tech in that era).

The appendix gives a simple latency model (Figure I.16), e.g.:
- cache hit: 1 cycle
- local miss: 85 cycles
- remote home directory miss: 125–150 cycles
- three-hop miss (remote cache supplies data): 140–170 cycles

And it builds “average cycles per reference” plots showing how effective latency depends on both miss frequency and where misses are served.

---

## 6) I.6 Measuring parallel performance (the scaling controversy)

Core principle:
- measure **wall-clock time** (CPU time can lie due to idle processors being unavailable).

Scaling matters:
- Unscaled (“fixed problem size”) scaling can look pessimistic because comm fraction rises and parallelism saturates.
- Scaled (“bigger problem with more processors”) scaling may be more realistic for scientific users.

But scaling is tricky:
- increasing problem size can change convergence rates or iteration counts (e.g., PDE solvers), so runtime can scale worse than algorithmic big‑O would suggest (e.g., \(n\log n\) effects).

---

## 7) I.7 Implementing cache coherence at scale (directory focus)

### 7.1 Why broadcast can’t scale
Broadcast (snooping) naturally serializes competing writes and supports memory ordering, but does not scale beyond modest node counts.

Directory systems avoid broadcast but must solve:
- race resolution for exclusive ownership
- knowing when invalidations complete (requires explicit acknowledgments)
- limited buffering in large systems (deadlock risk)

### 7.2 Serialization in directory protocols
Exclusive requests are serialized at the **home directory** for that block:
- the directory can enforce “one request completes before the next begins”
- but requesters must be informed via explicit replies/acks
- losers may receive NAKs and retry.

### 7.3 Deadlock avoidance under limited buffers
A major practical problem: if routers/controllers can’t always buffer messages, coherence traffic can deadlock.

The appendix describes a safe set of constraints (high-level):
- ensure replies are never NAK’d
- ensure buffers are reserved for replies before requests are issued
- allow NAK + retry for requests when resources aren’t available
- enforce acceptance guarantees for replies so transactions can always complete

It also notes forwarding data directly from owner to requester (in addition to directory) can reduce directory outstanding-transaction burden and latency (but introduces other timing complexities).

---

## 8) I.8 Blue Gene/L: customized cluster approach (why it worked)

### 8.1 Core strategy
Blue Gene/L uses:
- commodity-style processor cores,
- but a **highly customized node** (single chip with most logic) plus DRAM,
to achieve:
- very high density,
- low power,
- and low-latency/high-bandwidth interconnects.

### 8.2 Scale
BG/L supports up to **64K nodes** (32 racks × 1K nodes/rack, as described).
High density means most interconnect wiring stays within a rack, reducing complexity and latency.

### 8.3 Networks
BG/L uses a 3D torus for main interconnect (details in Appendix F) plus additional networks:
- Gigabit Ethernet (I/O nodes)
- JTAG test network
- barrier network
- global collective network

### 8.4 Memory vs Amdahl rule
Appendix notes that per-node memory (256–512MB DDR) may look small by Amdahl’s “1 MB per 1 MIPS” rule, but for FP-intensive scientific workloads where compute needs can grow faster than memory, the chosen memory range can be reasonable.

---

## 9) I.9 Concluding remarks (macro trends)

The appendix connects to TOP500 trends:
- clusters became the majority due to lower development effort
- many clusters are commodity clusters (often user-assembled)
- the very top systems remain more diverse (custom clusters like Blue Gene/Cray, DSM, SMP, etc.)
- classic vector supercomputers largely disappeared from the list over time
- Blue Gene dominated top entries of its era, showing the value of customizing interconnect + node density while leveraging commodity-style cores.

---

## Practical checklists

### If you’re evaluating a scientific multiprocessor
- Characterize comm: latency, bandwidth, overhead, occupancy, and latency hiding.
- Compute bisection-heavy patterns (FFT/all-to-all) vs neighbor patterns (stencils).
- Measure miss breakdown: capacity vs coherence; local vs remote.
- Evaluate synchronization: lock/barrier hot spots; check for quadratic traffic patterns.
- Consider scaling methodology: fixed-size vs scaled-size; validate iteration scaling.

### If you’re optimizing scientific parallel code
- Increase computation/communication ratio: blocking, tiling, data distribution.
- Reduce synchronization frequency and hot spots: hierarchical barriers, backoff/queue locks.
- Keep locality: NUMA-aware allocation; minimize remote coherence misses.
- For FFT-like patterns: schedule communication phases carefully; reduce global phases if possible.

---

## Flashcards (quick recall)

**Q1. Five comm metrics?**  
A. Latency, bandwidth, overhead, occupancy, latency hiding.

**Q2. Shared memory vs message passing: key difference?**  
A. Shared memory is implicit and can be easier for complex/dynamic patterns; message passing is explicit and simpler to reason about (often simpler hardware).

**Q3. Why do naïve spin locks scale poorly?**  
A. Under contention, bus traffic can grow ~\(n^2\) due to repeated LL/SC attempts.

**Q4. Why do larger cache blocks hurt multiprocessors?**  
A. More bytes per miss (bandwidth contention) + more false sharing + lower spatial locality for shared data.

**Q5. Key scientific kernels?**  
A. FFT (global comm), LU (blocked dense LA), Barnes-Hut (irregular tree), Ocean (stencil/grid).

**Q6. In DSM, why separate local vs remote misses?**  
A. Remote misses cost more latency and consume global bandwidth; their fraction can dominate scaling.

**Q7. Why do directories scale better than snooping?**  
A. They avoid broadcast; coherence actions target sharers listed in directory (but require acknowledgments and deadlock-safe buffering rules).

**Q8. Why Blue Gene/L succeeded?**  
A. Customized low-power dense nodes + custom high-performance interconnects at massive scale.

---

*End of CH16 / Appendix I summary.*
