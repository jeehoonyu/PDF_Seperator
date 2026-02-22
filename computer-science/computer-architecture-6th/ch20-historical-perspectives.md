# CH20 — Historical Perspectives and References (Appendix M) (Summary)

> Source PDF: `ch20-appendix-m-historical-perspectives-and-references.pdf`  
> Note: In this PDF set, “Chapter 20” corresponds to **Appendix M: Historical Perspectives and References**.

---

## 0) What Appendix M is

Appendix M is a **guided history** of the major ideas from the book (Ch.1–7 + appendices). It does two things:
1) traces how the core architectural ideas emerged through *machines, projects, and people*, and  
2) provides reading lists for deeper study.

It is structured as topical mini-histories:

- **M.2** Early computers + performance measures (Chapter 1)  
- **M.3** Memory hierarchy + protection (Chapter 2 + Appendix B)  
- **M.4** Instruction sets (Appendices A, J, K)  
- **M.5** Pipelining + ILP (Chapter 3 + Appendices C, H)  
- **M.6** DLP history: SIMD, vectors, multimedia SIMD, GPUs (Chapter 4)  
- **M.7** Multiprocessors + parallel processing history (Chapter 5 + Appendices F, G, I)  
- **M.8** Clusters (Chapter 6)  
- **M.10** Storage + RAID + I/O buses (Appendix D)  
(Plus **M.9** references section.)

---

## 1) M.1 Introduction: why history is included

The appendix explicitly frames history as a way to understand how:
- “obvious” ideas were not obvious at the time,
- trade-offs change as technology changes,
- and today’s “best practices” came from repeated failures and redesigns.

It maps each M.* section to the corresponding chapter/appendix in the book.

---

## 2) M.2 Early development of computers (and how performance measurement evolved)

### 2.1 Stored-program concept and the “von Neumann computer” controversy
The appendix describes ENIAC-era programming as manual (cables + switches), and notes John von Neumann’s EDVAC memo that helped crystallize the **stored-program** idea. It also notes controversy: giving too much credit to von Neumann vs engineers Eckert & Mauchly; the authors’ view is that all three were key.

### 2.2 Key early projects and inventions
It highlights major early efforts and contributions, including:
- Cambridge **EDSAC** (Wilkes) after Wilkes attended Moore School lectures,
- MIT **Whirlwind** (1947) whose “overwhelming innovation” was **magnetic core memory**, and that cores dominated main memory for nearly 30 years,
- special-purpose wartime machines (code-breaking) and their influence.

### 2.3 Performance metrics: from operation time → MIPS → real benchmarks
A major thread is that each generation of computers obsoleted the previous generation’s evaluation method:
- early metric: time per basic operation (e.g., add)
- then: average instruction time → MIPS (easy to explain but often misleading)
- then: synthetic benchmarks (e.g., Whetstone)
- then: benchmark suites such as SPEC (SPEC89 onward) for more realistic evaluation

A famous anecdote described: the VAX‑11/780 being marketed as “1 MIPS,” which later proved misleading under real time-sharing loads; this helped drive confusion between “native” vs “relative” MIPS.

---

## 3) M.3 Memory hierarchy and protection (high-level development)

This section collects the historical path to:
- caches as a response to the widening CPU–DRAM gap,
- TLBs and address translation to make virtual memory practical,
- and protection models as systems moved to time-sharing and multi-programming.

The appendix is heavy on references here, tying to Chapter 2 + Appendix B.

---

## 4) M.4 Evolution of instruction sets (why RISC happened)

This section places the RISC movement in context and revisits older ISA debates:
- stack architectures vs register architectures,
- code density vs pipeline/decode simplicity,
- and how compilers and microarchitecture shifted the balance.

It cites early influential ISA papers (IBM 360, PDP‑11) and summarizes why stack ISAs were criticized by those designers.

---

## 5) M.5 Pipelining and ILP: key machines and “lost then rediscovered” ideas

### 5.1 IBM 360/91 as a landmark
The appendix emphasizes IBM 360 Model 91 for introducing:
- register renaming (Tomasulo),
- dynamic memory hazard detection,
- generalized forwarding,
- and early branch prediction ideas.

It also notes the historical irony: many of these ideas faded for ~25 years and then reappeared broadly in the 1990s.

### 5.2 CDC 6600 and Cray influence
CDC 6600’s simplicity and performance, plus Cray’s continued emphasis on “keep it simple,” are positioned as early foundations for later RISC thinking and compiler scheduling.

---

## 6) M.6 Data-level parallelism history: SIMD → vectors → multimedia SIMD → GPUs

This section is explicitly narrative and memorable:
- starts with **ILLIAC IV** as the infamous early SIMD array processor
- moves to **Cray‑1** as the famous vector supercomputer
- then multimedia SIMD extensions (with the “Bunny People” ad-campaign anecdote)
- finishes with the rise of **GPUs**.

Key conceptual arc:
- early SIMD arrays centralize control to reduce cost,
- vectors pipeline operations with high memory bandwidth,
- commodity CPUs adopt short-vector multimedia extensions,
- GPUs become massively parallel SIMD/SIMT engines for graphics and later general compute.

---

## 7) M.7 Multiprocessors and parallel processing (plus interconnect history)

This section covers multiprocessor concepts and the parallel-programming ecosystem:
- shared-memory multiprocessors, directory coherence, and synchronization primitives
- interconnect and network evolution (Appendix F references)
- scientific parallelism vs commercial workloads

It includes references to many classic papers and surveys (including early parallel algorithm framing and studies that debunk simplistic “GPU vs CPU” claims).

---

## 8) M.8 Development of clusters (the path to WSCs and cloud)

The appendix connects academic cluster work to industry-scale computing:

- Berkeley **Network of Workstations (NOW)** is highlighted as foundational cluster research.
- It describes the path from NOW to the **Inktomi** search engine (and company), and how cluster-based search systems displaced large SMP-based approaches (e.g., AltaVista’s strategy), with Google following the cluster model.
- It also notes cluster popularity in scientific computing because of low cost and scalability.

The broader claim: clusters became the default substrate for Internet services and for much HPC, with custom designs surviving mainly at the top end.

---

## 9) M.10 Magnetic storage, RAID, and I/O buses

This section traces:
- early magnetic disk developments (IBM milestones),
- the emergence of **interrupts** for I/O events and DMA for block transfers,
- IBM 360’s I/O architecture (channels, I/O programs),
- the invention and evolution of **RAID** as disk arrays grew (and the need for redundancy increased),
- and the evolution of I/O buses/controllers as system bandwidth demands rose.

---

## 10) Carry-forward takeaways (what to remember)

- Architectural ideas often **recur** when the technology and economics become favorable again (e.g., ILP ideas reappearing after 25 years).
- Performance metrics “age out”; you must match the metric to the era’s bottleneck (MIPS → benchmarks → suite-level metrics).
- Memory and communication constraints repeatedly shape architecture (core memory, caches, clusters, interconnects).
- Compatibility and ecosystem can outweigh elegance (x86, benchmark standards, dominant platforms).

---

## Flashcards (quick recall)

**Q1. What is the “stored-program computer” idea?**  
A. Programs stored as data in memory, enabling flexible software-controlled execution (EDVAC memo popularized the idea).

**Q2. Whirlwind’s “overwhelming innovation”?**  
A. Magnetic core memory; served as main memory tech for ~30 years.

**Q3. Why is MIPS a problematic metric historically?**  
A. Assumes uniform instruction time; breaks with caches/pipelining and can be gamed; “relative MIPS” caused confusion.

**Q4. Why is IBM 360/91 historically important?**  
A. Introduced Tomasulo-like renaming and dynamic hazard handling; ideas resurfaced decades later.

**Q5. What arc does the DLP history follow in M.6?**  
A. ILLIAC IV (SIMD arrays) → Cray‑1 (vectors) → multimedia SIMD → GPUs.

**Q6. What cluster research is tied to early Internet services?**  
A. Berkeley NOW project and the Inktomi search engine; influences modern WSCs/cloud.

---

*End of CH20 / Appendix M summary.*
