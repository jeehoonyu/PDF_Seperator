# Chapter 4 — Data-Level Parallelism in Vector, SIMD, and GPU Architectures (Summary)

According to a document (© 2019 Elsevier Inc.), Chapter 4 explains **data-level parallelism (DLP)** and three major SIMD-style implementations: **vector processors**, **multimedia SIMD ISA extensions**, and **GPUs**.【291:6†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L18-L59】

---

## 0) What this chapter is really teaching you

**DLP = doing the same operation over many data elements at once.**  
Hillis & Steele’s framing: data-parallel algorithms get speedup from *simultaneous operations across large data sets* rather than from multiple control threads.【291:6†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L23-L26】

The chapter’s core claim:
- SIMD can be **more energy-efficient** than MIMD because *one instruction can launch many data operations*.【291:6†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L51-L53】
- SIMD also reduces mental overhead: programmers still “think sequentially” but get speedup via parallel data ops.【291:6†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L54-L56】

---

## 1) Chapter map (sections)

- 4.1 Introduction  
- 4.2 Vector Architecture  
- 4.3 SIMD Instruction Set Extensions for Multimedia  
- 4.4 Graphics Processing Units  
- 4.5 Detecting and Enhancing Loop-Level Parallelism  
- 4.6 Cross-Cutting Issues  
- 4.7 Putting It All Together (Embedded vs Server GPUs; Tesla vs Core i7)  
- 4.8 Fallacies and Pitfalls  
- 4.9 Concluding Remarks【291:6†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L1-L11】

---

## 2) SIMD “variations” and why they exist (4.1)

Chapter 4 covers **three variations of SIMD**【291:6†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L58-L59】:

1) **Vector architectures** (older, classic supercomputer style)  
   - Easier to understand/compile to than later SIMD forms.  
   - Historically “too expensive for microprocessors” due to transistor cost and especially the need for **lots of DRAM bandwidth**, since conventional micros relied heavily on caches for memory performance.【291:6†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L61-L67】

2) **Multimedia SIMD ISA extensions** (MMX → SSE → AVX on x86)  
   - SIMD extensions began with MMX (1996), followed by SSEs and modern AVX, and are often required to hit peak compute (especially FP) on x86 systems.【291:6†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L69-L76】

3) **GPUs** (massively multithreaded SIMD/SIMT)  
   - Implement DLP using many SIMD processors (“streaming multiprocessors” in vendor jargon) plus heavy multithreading to hide latency.

---

## 3) Vector architecture essentials (4.2)

### 3.1 RV64V design choices you should remember
The chapter uses an RV64V-style example to highlight **dynamic register typing** and configuration:

- Register *type/width* determined by configuring vector registers, not by separate opcodes for every type/width combo.  
- Benefit: avoids “several pages” of instruction variants and can make conversions implicit via configuration.【291:3†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L31-L53】

**Maximum vector length (MVL / mvl):**
- With a fixed vector register storage (example: 1024 bytes), enabling fewer vector registers gives each one more storage → larger max vector length (mvl).  
- Example: enable 4 vector registers, type 64-bit FP → 256 bytes/register → 32 elements (256/8).【291:3†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L36-L42】

**Context switch cost mitigation:**
- Vector state is large; dynamic typing lets programs **disable unused vector regs**, so they don’t need saving/restoring on context switch.【291:3†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L43-L48】

### 3.2 Strip mining (handle “n not a multiple of MVL”)
Strip mining processes an arbitrary-length loop in blocks:
- first block may be shorter: \(m = n \bmod MVL\)
- remaining blocks use full MVL for high throughput.【291:2†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L85-L87】

### 3.3 Predicate (mask) registers for IF statements in vector loops
Problem: IF inside a loop introduces control dependences, blocking normal vectorization.【291:2†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L3-L16】

Solution: **vector-mask control** via predicate registers:
- predicate register holds a Boolean mask controlling per-element execution.  
- Elements with mask 0 are left unchanged (for the destination).  
- Enabling a predicate reg initializes it to all 1s (execute all elements).【291:2†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L28-L39】

**Key performance cost:** masked vector instructions still take the same time even when many mask bits are 0; GFLOPS drop with masking.【291:9†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L68-L83】

### 3.4 Memory banks and bank conflicts (bandwidth limits)
Vector load/store bandwidth comes from **interleaved memory banks**.  
Example in the text:
- 8 banks, bank busy time 6 cycles, total memory latency 12 cycles, vector load length 64  
- stride 1: 76 cycles total (12 + 64) ≈ 1.2 cycles/element  
- stride 32 (multiple of #banks): collisions → 391 cycles total, ≈ 6.1 cycles/element (≈5× slower).【287:2†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L3-L14】

### 3.5 Gather-scatter (sparse / indirect accesses)
Sparse computations need indirect addressing:
- gather loads use an index vector to fetch elements at base+offset[i]
- scatter stores write them back with the same index vector.  
This is widely supported in modern vectors (example RV64V indexed load/store).【287:2†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L31-L47】

---

## 4) Multimedia SIMD ISA extensions (4.3)

### 4.1 Why SIMD extensions “won” in commodity CPUs
The chapter summarizes several historical reasons:
- Vector processors need lots of memory bandwidth (hard in typical systems).  
- SIMD avoids some VM/page-fault complications by requiring aligned transfers that don’t cross page boundaries in early designs.  
- Fixed short vectors made it easier to add “media-friendly” ops like permutations/shuffles.  
- Backward binary compatibility locks ecosystems into the SIMD extension path.【291:1†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L1-L15】

### 4.2 Practical rule: alignment matters
Compilers can increasingly auto-generate SIMD, but you must align data to SIMD width or the compiler may fall back to scalar code (or generate slower unaligned paths).【287:4†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L1-L7】

### 4.3 Example: AVX instruction “shape”
AVX 256-bit “packed double” = 4× 64-bit FP operands in parallel. The chapter lists representative ops (add/sub/mul/div, fused multiply-add, compare, aligned moves, broadcast).【291:1†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L25-L49】

---

## 5) Roofline model: the unifying performance picture (4.3)

Roofline ties together:
- peak compute throughput,
- peak memory bandwidth (delivered, e.g., via STREAM),
- arithmetic intensity = FLOPs per DRAM byte accessed.【287:0†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L1-L21】【287:4†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L21-L33】

**Upper bound formula:**
\[
\text{Attainable GFLOPs/s}=\min\big(\text{Peak Memory BW}\times \text{Arithmetic Intensity},\ \text{Peak FP Perf}\big)
\]
【287:0†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L60-L71】

Interpretation:
- If your arithmetic intensity “pole” hits the **flat roof** → compute-bound.
- If it hits the **slanted roof** → memory-bandwidth-bound.
- The **ridge point** location tells you how hard it is to reach peak compute (far-right ridge = only very high-intensity kernels can hit peak).【287:0†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L67-L80】

Concrete example comparison (Core i7 920 vs NVIDIA GTX 280 rooflines, including peak GFLOPs and memory BW) is shown in Figure 4.28.【287:1†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L200-L210】

---

## 6) GPUs are “multithreaded SIMD processors” (4.4)

### 6.1 Key mental model
Chapter’s “unmasked truth”: GPUs are essentially **many multithreaded SIMD processors**, with:
- more SIMD processors,
- more lanes per processor,
- more multithreading hardware than typical multicore CPUs.【291:4†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L41-L50】

The CUDA programming model wraps this into “CUDA threads,” but hardware executes them in groups:
- threads are organized into blocks and executed **32 at a time** (warp size), and you want adjacent addresses for good memory performance.【291:4†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L53-L59】

### 6.2 SIMD processor microarchitecture (Pascal example)
A simplified multithreaded SIMD processor:
- has many SIMD lanes, a warp scheduler, and large register files per lane.【291:14†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L55-L57】
- In Pascal example: a **32-wide thread** of SIMD instructions maps to **16 physical lanes**, so each SIMD instruction takes **2 cycles** (vector length 32, “chime” 2).【291:14†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L63-L69】
- The thread scheduler uses a **scoreboard** to track readiness across up to ~64 SIMD threads and schedule whichever is ready, hiding variable memory latency (cache/TLB effects).【291:14†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L76-L87】

### 6.3 GPU memory hierarchy (the three spaces you must distinguish)
The chapter explicitly distinguishes:

1) **GPU (global) memory** (off-chip DRAM shared by whole GPU)  
2) **Local memory** (on-chip scratchpad per SIMD processor, shared within a thread block; typically ~48 KiB)  
3) **Private memory** (per-thread region in off-chip DRAM; used for stack, spills, and private vars; cached in L1/L2)【291:0†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L13-L44】

Figure 4.18 summarizes these relationships and host access (host can read/write global memory, not local/private).【291:0†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L39-L76】

### 6.4 Control flow and divergence (why “1024 chickens” can lose)
GPU lane control uses masks:
- all lanes are either executing the same instruction or idle.
- performance depends heavily on how often branches diverge.  
Example: a deep-branch eigenvalue code still ran efficiently because most cycles had 29–32 of 32 mask bits active.【291:0†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L1-L6】

The chapter warns that the abstraction “each CUDA thread is independent” can be correct but **slow**, like using huge virtual memory on small physical memory: legal, but can be painfully inefficient.【291:11†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L11-L15】

### 6.5 Terminology: SIMD vs SIMT and why jargon is confusing
Figure 4.25 maps the chapter’s descriptive terms to NVIDIA/AMD/OpenCL jargon:
- streaming multiprocessor (SM) ≈ multithreaded SIMD/SIMT processor executing warps (32 threads)  
- “shared memory” (NVIDIA) corresponds to what this chapter calls **local memory** (OpenCL term), which is not shared between SIMD processors  
- NVIDIA prefers **SIMT** because per-thread branching/control flow differs from classical SIMD.【291:5†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L1-L130】

---

## 7) GPU vs multicore+SIMD: the practical differences (4.4 / 4.7)

Key structural differences and an important omission:
- On CPUs, scalar core + SIMD extensions are tightly integrated; GPUs are separated by an I/O bus and often have separate main memory.  
- Historically, multimedia SIMD lacked gather-scatter, which the chapter calls a significant omission (later sections cover it).【291:4†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L1-L9】

Figure 4.23 compares typical ranges (SIMD processors, lanes, HW thread support, cache sizes, memory capacity, coherence, etc.).【291:4†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L11-L35】

---

## 8) Fallacies & pitfalls worth remembering (4.8)

### Pitfall 1: “GPU threads are independent, so control flow doesn’t matter”
Reality: lanes share control. Worst case: only 1 lane active while others idle; performance collapses.【291:12†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L53-L60】

### Pitfall 2: “Masks make IF statements free”
Masks avoid branches/control dependences, but **do not reduce execution time** for masked-off lanes; throughput drops when masks are sparse.【291:9†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L68-L83】

### Pitfall 3: “All memory accesses are equal”
Stride/bank-conflict behavior can dominate (5× slowdowns in a simple example).【287:2†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L8-L14】

### Pitfall 4: “Peak GFLOPs tells me performance”
Roofline: for low arithmetic intensity, you’re capped by memory BW regardless of peak compute.【287:0†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L67-L75】

---

## 9) Practical checklists (what to do when writing/optimizing)

### 9.1 Vector / SIMD checklist
- Confirm loop has no loop-carried dependences (then vectorize).
- Ensure **alignment** to SIMD width (to avoid scalar fallback / slow paths).【287:4†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L1-L7】
- Use strip mining for arbitrary lengths (handle tail).【291:2†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L85-L87】
- Watch stride patterns to avoid bank conflicts.【287:2†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L8-L14】
- For sparse/indirect patterns, use gather-scatter if available.【287:2†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L31-L45】

### 9.2 GPU checklist
- Use **many thread blocks** so the scheduler can hide DRAM latency with multithreading.【291:14†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L84-L87】
- Keep warps **non-diverged**; if branches exist, prefer uniform conditions (all lanes agree).【291:12†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L45-L51】
- Use **local/shared memory** (~48 KiB) for reuse within a thread block; avoid spilling to private memory when possible.【291:0†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L22-L37】
- Coalesce accesses: adjacent threads → adjacent addresses (explicitly called out in the chapter summary).【291:4†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L56-L59】

---

## 10) Flashcards (quick recall)

**Q1. What is DLP?**  
A. Parallelism from doing simultaneous operations across large data sets (data-parallel algorithms).【291:6†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L23-L26】

**Q2. Why can SIMD be more energy-efficient than MIMD?**  
A. One instruction can launch many data ops, reducing instruction fetch/issue overhead per operation.【291:6†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L51-L53】

**Q3. What are the 3 SIMD variations in Chapter 4?**  
A. Vector architectures, multimedia SIMD ISA extensions, GPUs.【291:6†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L58-L59】

**Q4. What is strip mining?**  
A. Processing an arbitrary-length vector loop in chunks of size MVL, with a short “remainder” chunk first if needed.【291:2†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L85-L87】

**Q5. Why do masks hurt throughput?**  
A. Vector instructions still take the same time even when mask bits are 0; masked-off lanes do no useful work → lower GFLOPS.【291:9†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L68-L83】

**Q6. Roofline bound formula?**  
A. \(\min(\text{BW}\times\text{AI},\ \text{Peak FP})\).【287:0†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L60-L71】

**Q7. In Pascal example, how does a 32-wide thread map to lanes?**  
A. A 32-wide thread maps to 16 lanes → 2 cycles per SIMD instruction (vector length 32, chime 2).【291:14†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L63-L69】

**Q8. Name the three GPU memory spaces (chapter terms).**  
A. Global GPU memory (DRAM shared), local memory (on-chip per-SIMD-processor scratchpad shared within a thread block), private memory (per-thread DRAM region, cached).【291:0†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L13-L44】

---

## 11) One-page compact carryover (for low-context continuation)

- DLP = same op over many elements; SIMD can be energy-efficient and programmer-friendly.【291:6†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L51-L56】  
- Vector: MVL, strip mining, predicate masks; avoid stride bank conflicts; gather/scatter for sparse.【291:2†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L85-L87】【287:2†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L8-L14】【287:2†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L31-L45】  
- SIMD ISA (MMX/SSE/AVX): alignment matters; fixed short vectors + compatibility drove adoption.【291:1†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L1-L15】【287:4†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L1-L7】  
- Roofline: performance upper bound = min(BW×AI, Peak FP).【287:0†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L60-L71】  
- GPU: many multithreaded SIMD processors; warps of 32; divergence = wasted lanes; use shared/local memory + coalesced accesses.【291:4†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L53-L59】【291:0†ch04-data-level-parallelism-in-vector-simd-and-gpu-architectures.pdf†L22-L37】

---

*End of Chapter 4 summary.*
