# CH02 — Memory Hierarchy Design (Summary)

> Source: **ch02-memory-hierarchy-design.pdf** (Chapter Two).  
> Scope: Sections **2.1–2.9** + key figures, equations, and design trade-offs.

---

## 2.1 Introduction: Why memory hierarchies exist

### Core idea
A *memory hierarchy* is an economic + performance compromise: **small, fast, expensive memories close to the CPU** and **large, slower, cheaper memories farther away**. The hierarchy works because programs exhibit **locality**:
- **Temporal locality**: recently used items tend to be reused soon.
- **Spatial locality**: items near a referenced address tend to be referenced soon. 【turn10file6†ch02-memory-hierarchy-design.pdf†L41-L56】

### Inclusion property (typical but not universal)
Often, a lower level contains a **superset** of the next higher level (e.g., L3 includes L2 and L1). This *inclusion property* is required for the lowest level (main memory for cache hierarchies; disk/Flash for virtual memory). 【turn10file6†ch02-memory-hierarchy-design.pdf†L58-L66】

---

## 2.2 Memory Technology and Optimizations

### Key technologies in the hierarchy
- **SRAM**: used for caches (fast, higher cost/bit).
- **DRAM**: used for main memory (high density, slower).
- **Flash**: used for secondary storage, especially in PMDs and increasingly in desktops/servers. 【turn10file8†ch02-memory-hierarchy-design.pdf†L34-L68】

### Two latency numbers: access time vs cycle time
With burst-transfer memories, latency is quoted as:
- **Access time**: from read request to first word arrival.
- **Cycle time**: minimum time between *unrelated* requests. 【turn10file8†ch02-memory-hierarchy-design.pdf†L58-L62】

### SRAM notes (why it’s “static”)
- SRAM doesn’t need refresh; access time ≈ cycle time.
- Often **6 transistors/bit**; low standby power. 【turn10file11†ch02-memory-hierarchy-design.pdf†L1-L7】

**Cache SRAM organization**: tags stored in parallel with each block so a whole block can be read/written in a cycle (helpful on fills and writebacks). 【turn10file11†ch02-memory-hierarchy-design.pdf†L16-L20】

### DRAM internals (RAS/CAS, rows, banks, refresh)
**Row/column organization** (classic RAS/CAS terminology):
- DRAM is a matrix addressed by rows/columns.
- Opening a row loads it into a **row buffer**; subsequent column accesses can be faster. 【turn10file11†ch02-memory-hierarchy-design.pdf†L37-L51】

**Refresh**:
- Each row must be refreshed within a window (e.g., 64 ms); controllers schedule refresh, occasionally making memory temporarily unavailable. 【turn13file4†ch02-memory-hierarchy-design.pdf†L1-L10】

**Modern DRAM (SDRAM + DDR) optimizations**:
- **SDRAM** adds a clocked interface to reduce per-transfer overhead and enables burst transfer mode. 【turn13file7†ch02-memory-hierarchy-design.pdf†L18-L25】
- **DDR** transfers on both clock edges, doubling peak transfer rate. 【turn13file2†ch02-memory-hierarchy-design.pdf†L14-L16】
- **Banks** allow overlapping accesses; each bank has its own row buffer. 【turn13file2†ch02-memory-hierarchy-design.pdf†L18-L32】

**Bank commands (intuition)**:
1. **ACT** (activate): open bank+row → row buffer
2. **CAS**: select columns / deliver burst
3. **PRE** (precharge): close row, ready for new row 【turn13file4†ch02-memory-hierarchy-design.pdf†L24-L33】

### DRAM scaling trends: bandwidth vs latency
- DRAM capacity growth slowed (especially 2010–2016).
- DDR1→DDR3 improved access times ~3× (≈7%/yr); **DDR4 improves power/bandwidth but similar access latency to DDR3**. 【turn13file1†ch02-memory-hierarchy-design.pdf†L1-L8】

### Naming & bandwidth of DDR DIMMs (common confusion)
DIMMs are labeled by *peak bandwidth* (e.g., PC3200) rather than clock; chips often labeled by transfers/s (e.g., “DDR400” at 200 MHz clock). 【turn13file1†ch02-memory-hierarchy-design.pdf†L45-L55】

### Power trends
- DDR4 voltage dropped to ~1.2 V; more banks can reduce power by limiting active rows. 【turn13file0†ch02-memory-hierarchy-design.pdf†L1-L6】

### Graphics DRAM (GDDR)
GDDRs are tuned for GPU bandwidth with wider interfaces and higher data-pin rates; often soldered close to GPU. 【turn13file5†ch02-memory-hierarchy-design.pdf†L11-L26】

### Packaging innovation: stacked / embedded DRAM → “HBM”
Putting DRAM in the same package (2.5D interposer now; 3D stacking under development) can reduce latency and increase bandwidth; several producers call this **High Bandwidth Memory (HBM)**. 【turn13file5†ch02-memory-hierarchy-design.pdf†L78-L87】【turn13file6†ch02-memory-hierarchy-design.pdf†L22-L31】

HBM can serve as:
- main memory in some contexts (cost/thermal limits apply), or
- **an additional cache level** (discussed later as an optimization). 【turn13file6†ch02-memory-hierarchy-design.pdf†L1-L8】

### Flash memory (NAND): why it’s great for storage but not DRAM replacement
NAND Flash properties:
- Reads are **page-based** and sequential: long time to first byte (~25 μs), then page stream (~40 MiB/s).
- DRAM is orders faster: first byte ~40 ns; high burst bandwidth.  
Result: Flash can replace disks, **not** main memory. 【turn13file6†ch02-memory-hierarchy-design.pdf†L55-L65】

Writes:
- Must **erase before overwrite**; erase is block-based → expensive write amplification.
- Flash writes are ~1500× slower than SDRAM, but still 8–15× faster than disks. 【turn13file6†ch02-memory-hierarchy-design.pdf†L66-L71】

Endurance and controllers:
- Blocks have limited write cycles (e.g., ≥100,000); controllers use **wear leveling** (“write leveling”). 【turn13file15†ch02-memory-hierarchy-design.pdf†L5-L9】

### Phase-change memory (PCM / “3D XPoint” context)
- PCM changes a material phase (crystalline vs amorphous) to represent bits; also discussed under “memristor” terminology.
- 2017 Micron+Intel delivered XPoint chips believed PCM-based; expected better write durability, much faster writes vs NAND (no erase-before-write), and lower read latency. 【turn13file9†ch02-memory-hierarchy-design.pdf†L6-L27】

### Dependability in memory systems
- **Hard errors** (permanent faults) vs **soft errors** (transient faults). 【turn10file2†ch02-memory-hierarchy-design.pdf†L5-L13】
- Protection methods:
  - Parity (detect) — typically 1 parity bit per 8 data bits. 【turn10file2†ch02-memory-hierarchy-design.pdf†L22-L25】
  - ECC (detect 2, correct 1) — e.g., 8 overhead bits per 64 data bits. 【turn10file2†ch02-memory-hierarchy-design.pdf†L25-L26】
  - **Chipkill** (server-scale; tolerate a full chip failure by distributing data+ECC). 【turn10file2†ch02-memory-hierarchy-design.pdf†L29-L35】

---

## 2.3 Ten Advanced Optimizations of Cache Performance

### Baseline performance model(s)
**Single-level AMAT** (conceptual):
- **AMAT = Hit time + Miss rate × Miss penalty**

**Multilevel cache AMAT (explicit in text)**:
\[
\text{AMAT} = \text{HitTime}_{L1} + \text{MissRate}_{L1}\cdot \Big(\text{HitTime}_{L2} + \text{MissRate}_{L2}\cdot \text{MissPenalty}_{L2}\Big)
\]
【turn12file2†ch02-memory-hierarchy-design.pdf†L1-L7】

### The 10 techniques (with “what it targets”)
The chapter groups them by hit time, miss rate, miss penalty, bandwidth, and power; Figure 2.18 is the summary table. 【turn11file13†ch02-memory-hierarchy-design.pdf†L9-L97】

Below is the **named list** (matching Figure 2.18) with quick intent + main trade-off.

1) **Small & simple L1 caches**  
Goal: reduce hit time/power (smaller structures are faster; simpler hit path). 【turn10file5†ch02-memory-hierarchy-design.pdf†L22-L35】

2) **Way-predicting / way-selecting caches**  
Goal: reduce hit time (and potentially power with way selection).  
Way selection can save power substantially but increases average access time; best where power > performance. 【turn11file10†ch02-memory-hierarchy-design.pdf†L14-L41】

3) **Pipelined access + multibanked caches**  
Goal: increase bandwidth (more accesses per cycle), enable higher clock rate at cost of latency and (for I$) higher branch-mispredict penalty. 【turn11file14†ch02-memory-hierarchy-design.pdf†L1-L16】【turn11file10†ch02-memory-hierarchy-design.pdf†L43-L51】

4) **Nonblocking caches (hit-under-miss / miss-under-miss)**  
Goal: reduce *effective* miss penalty by letting hits proceed during a miss; more advanced forms overlap multiple misses. 【turn11file11†ch02-memory-hierarchy-design.pdf†L63-L73】

   Practical note: “miss penalty” becomes the *nonoverlapped stall time*—harder to model with simple AMAT. 【turn10file4†ch02-memory-hierarchy-design.pdf†L1-L8】

5) **Critical word first + early restart**  
Goal: reduce miss penalty by resuming once the needed word arrives rather than waiting for whole block. Benefits scale with block size and access patterns. 【turn11file12†ch02-memory-hierarchy-design.pdf†L18-L43】

6) **Merging write buffer (write combining)**  
Goal: reduce miss penalty and stalls by combining adjacent writes into fewer buffer entries; improves memory efficiency. 【turn11file9†ch02-memory-hierarchy-design.pdf†L33-L45】

7) **Compiler techniques to reduce cache misses**  
Goal: reduce miss rate (software-controlled locality improvements).  
(High-level note: success depends on compiler sophistication and workload structure; summarized in Figure 2.18.) 【turn11file13†ch02-memory-hierarchy-design.pdf†L57-L63】

8) **Hardware prefetching (I$ and D$)**  
Goal: reduce miss penalty or miss rate *if timely*; can backfire due to bandwidth contention or cache pollution.  
Example: Pentium 4 shows large speedups only for some workloads; many benchmarks <15% gain. 【turn11file2†ch02-memory-hierarchy-design.pdf†L1-L5】【turn11file2†ch02-memory-hierarchy-design.pdf†L86-L89】

9) **Compiler-controlled prefetching**  
Goal: reduce miss penalty/rate by inserting prefetch instructions early enough.  
Important: needs **nonblocking caches** so execution can proceed while prefetches are outstanding. 【turn11file2†ch02-memory-hierarchy-design.pdf†L128-L131】

10) **HBM as an additional cache level**  
Goal: boost bandwidth / alter miss behavior using stacked memory; effects depend heavily on achieved hit-rate improvements and packaging constraints. 【turn11file13†ch02-memory-hierarchy-design.pdf†L84-L90】

### Figure 2.18 — “One-glance” summary
If you only memorize one thing from 2.3, memorize the 10 names + their “target”: hit time, bandwidth, miss penalty, miss rate, power, and complexity rating. 【turn11file13†ch02-memory-hierarchy-design.pdf†L11-L97】

---

## 2.4 Virtual Memory and Virtual Machines

### What the architecture must provide (minimum)
To safely share hardware among processes, the ISA + OS need:
1) **At least two modes** (user vs supervisor/kernel).  
2) Protected state (mode bit, exception enable/disable, protection info).  
3) Controlled mode transitions (system call into supervisor; return restores mode).  
4) Memory protection mechanisms per process without swapping on every context switch. 【turn12file12†ch02-memory-hierarchy-design.pdf†L1-L25】

### Paging & the TLB
- Virtual memory uses fixed-size pages (often 4 KiB, 16 KiB, or larger), mapped via **page tables** with protection bits in each PTE. 【turn12file12†ch02-memory-hierarchy-design.pdf†L26-L33】
- Naively, every access would require two memory references (translate + data), which is too slow.
- Solution: rely on locality and cache translations in a **TLB**. 【turn12file12†ch02-memory-hierarchy-design.pdf†L41-L47】

A TLB entry stores:
- virtual tag → physical page address,
- protection,
- valid (often use + dirty bits).  
OS updates page table bits and invalidates the TLB entry so a reload copies the correct metadata. 【turn12file12†ch02-memory-hierarchy-design.pdf†L49-L54】

### Virtual machines: page tables, TLBs, and I/O virtualization
- A VMM can maintain a **shadow page table** mapping guest virtual → real physical addresses, trapping guest page-table modifications. 【turn12file3†ch02-memory-hierarchy-design.pdf†L1-L16】
- Alternative: **nested page tables** (IBM 370 did this earlier; AMD implemented similar), reducing need for shadow tables. 【turn12file3†ch02-memory-hierarchy-design.pdf†L18-L22】
- TLB virtualization: trap TLB-access instructions; process-ID tags can reduce TLB flushes on VM switches. 【turn12file3†ch02-memory-hierarchy-design.pdf†L23-L28】
- I/O virtualization is often the hardest due to device diversity + driver complexity; VMM may present generic virtual devices and handle real device interactions. 【turn12file3†ch02-memory-hierarchy-design.pdf†L31-L38】

---

## 2.5 Cross-Cutting Issues: The Design of Memory Hierarchies

The chapter highlights that “memory hierarchy design” is not isolated—it interacts with:

### Protection, virtualization, and ISA quirks
Example: x86 **POPF** historically behaved differently in user mode vs system mode for an interrupt-enable flag, which breaks expectations for guest OSes; ISA extensions for virtualization address this. 【turn12file6†ch02-memory-hierarchy-design.pdf†L20-L26】

### Autonomous instruction fetch units
When fetch units read full cache blocks (and may prefetch), raw miss-rate comparisons become tricky: extra fetch/prefetch may *increase misses* but reduce overall miss penalty. 【turn12file6†ch02-memory-hierarchy-design.pdf†L46-L57】

### Speculation and memory access
Speculation can generate memory references that are later discarded; systems must avoid raising exceptions for speculative references that never “commit.” 【turn12file6†ch02-memory-hierarchy-design.pdf†L61-L74】

---

## 2.6 Putting It All Together: ARM Cortex-A53 vs Intel Core i7 6700

### ARM Cortex-A53 (memory hierarchy highlights)
- Configurable ARMv8-A IP core, energy-focused. 【turn14file6†ch02-memory-hierarchy-design.pdf†L48-L57】【turn14file11†ch02-memory-hierarchy-design.pdf†L7-L10】
- Dual-issue, clock rates up to ~1.3 GHz. 【turn14file11†ch02-memory-hierarchy-design.pdf†L23-L24】
- Two-level TLB + two-level cache; **critical term returned first** so CPU can continue while miss completes. Supports up to four banks. 【turn14file11†ch02-memory-hierarchy-design.pdf†L24-L27】

**A53 memory hierarchy summary (Figure 2.19)**: 【turn14file11†ch02-memory-hierarchy-design.pdf†L23-L55】
- Instruction MicroTLB: 10 entries, fully associative, ~2-cycle miss penalty
- Data MicroTLB: 10 entries, fully associative, ~2-cycle miss penalty
- L2 Unified TLB: 512 entries, 4-way, ~20-cycle miss penalty
- L1 I$: 8–64 KiB, 2-way, 64B blocks, ~13-cycle miss penalty (to next level)
- L1 D$: 8–64 KiB, 2-way, 64B blocks, ~13-cycle miss penalty
- L2 unified cache: 128 KiB–2 MiB, 16-way, LRU, ~124-cycle miss penalty

**Address aliasing note**: with 32 KiB D$ and 4 KiB pages, a physical page could map to two cache addresses; A53 avoids aliases via hardware detection on a miss. 【turn14file11†ch02-memory-hierarchy-design.pdf†L27-L29】

### Intel Core i7 6700 (memory hierarchy highlights)
- x86-64, 4-core, out-of-order; focus here is single-core memory behavior. 【turn14file5†ch02-memory-hierarchy-design.pdf†L19-L23】
- Can execute up to 4 x86 instructions per cycle; supports SMT (2 threads/core).  
Peak: 4.0 GHz Turbo → 16B inst/s per core (peak). 【turn14file5†ch02-memory-hierarchy-design.pdf†L25-L31】
- Up to 3 memory channels; with DDR3-1066 (PC8500) peak bandwidth just over 25 GB/s. 【turn14file5†ch02-memory-hierarchy-design.pdf†L35-L37】

**Address + TLB details**:
- i7 uses 48-bit virtual, 36-bit physical addresses (max physical memory 36 GiB in this description). 【turn14file5†ch02-memory-hierarchy-design.pdf†L140-L142】
- Example walk: an I-TLB miss goes to L2 TLB (1536 PTEs, 12-way); L1 refill from L2 costs 8 cycles → 9-cycle miss penalty including initial access. If L2 TLB misses, hardware walks page tables. 【turn12file5†ch02-memory-hierarchy-design.pdf†L1-L6】

**Cache access step-through (Figure 2.25 context)**:
- L1 I$ is virtually addressed, physically tagged; pipelined hit latency 4 cycles. 【turn12file5†ch02-memory-hierarchy-design.pdf†L13-L20】
- L2 indexing uses:
\[
2^{\text{Index}}=\frac{\text{Cache size}}{\text{Block size}\times\text{Associativity}}
\]
Example shown: 256 KiB / (64B × 4-way) = 1024 = 2¹⁰. 【turn12file5†ch02-memory-hierarchy-design.pdf†L27-L34】
- L3 example: 8 MiB / (64B × 16-way) = 8192 = 2¹³; L3 hit returns block after ~42 cycles, 16 B per cycle. 【turn12file5†ch02-memory-hierarchy-design.pdf†L45-L59】

**Hierarchy structure notes**:
- Caches are nonblocking; L1 uses merging write buffer; L3 is inclusive of L1+L2; L1 write misses do **not** allocate on write in this example. 【turn12file10†ch02-memory-hierarchy-design.pdf†L1-L7】【turn12file10†ch02-memory-hierarchy-design.pdf†L277-L279】

---

## 2.7 Fallacies and Pitfalls (selected)

### Pitfall: virtualizing an ISA not designed to be virtualizable
If sensitive instructions fail to trap properly (especially on older ISAs), VMMs become complex and slow. The chapter highlights classic 80x86 issues (e.g., user-mode instructions that reveal privileged state or silently fail). 【turn12file0†ch02-memory-hierarchy-design.pdf†L59-L79】

Modern fixes:
- Intel **VT-x** adds a new execution mode + VM state structures + instructions to swap VM state; AMD provides similar (SVM) and nested page tables. 【turn12file8†ch02-memory-hierarchy-design.pdf†L23-L42】

---

## 2.8 Concluding remarks: “memory wall” and where things are heading

- The “memory wall” term is credited to Wulf & McKee (1994). 【turn13file10†ch02-memory-hierarchy-design.pdf†L1-L6】
- DRAM density/access-time improvements have slowed; access time improvement between DDR3 and DDR4 is “almost vanished,” pushing focus to packaging (e.g., stacked memory) for bandwidth/latency improvements. 【turn13file10†ch02-memory-hierarchy-design.pdf†L19-L28】
- Multi-level caches (2→4), refill/prefetch sophistication, and software awareness of locality have helped keep the wall “at bay.” 【turn13file10†ch02-memory-hierarchy-design.pdf†L47-L53】

---

## Practical “carry-forward” checklist (what to remember for later chapters)

### Performance knobs (always ask these)
- What’s the **hit time**, **miss rate**, **miss penalty**, and **bandwidth** at each level?
- Are caches **blocking** or **nonblocking**? If nonblocking, AMAT isn’t enough—think “stall overlap.” 【turn10file4†ch02-memory-hierarchy-design.pdf†L1-L8】
- Is the hierarchy **inclusive** (common) or exclusive? (Inclusion mentioned as typical property.) 【turn10file6†ch02-memory-hierarchy-design.pdf†L63-L66】

### Technology knobs (often overlooked)
- DRAM: bank count, row-buffer hit rate, controller scheduling, refresh overhead. 【turn13file2†ch02-memory-hierarchy-design.pdf†L25-L32】【turn13file4†ch02-memory-hierarchy-design.pdf†L8-L10】
- Flash: page size, erase block size, wear leveling, write amplification. 【turn13file6†ch02-memory-hierarchy-design.pdf†L66-L71】【turn13file15†ch02-memory-hierarchy-design.pdf†L5-L9】
- Reliability: parity vs ECC vs Chipkill (scale dictates choice). 【turn10file2†ch02-memory-hierarchy-design.pdf†L42-L53】【turn10file2†ch02-memory-hierarchy-design.pdf†L29-L35】

### OS/ISA knobs
- TLB design + page size + virtualization support can dominate real performance. 【turn12file12†ch02-memory-hierarchy-design.pdf†L26-L47】【turn12file3†ch02-memory-hierarchy-design.pdf†L23-L29】

---

## File info
- Generated: 2026-02-21 (America/Vancouver)
- Intended use: personal “library notes” for quick recall + future prompting
