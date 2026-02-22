# CH07 — Domain-Specific Architectures (DSAs) (Summary)

> Source: `ch07-domain-specific-architectures.pdf`  
> Big idea: with Dennard scaling over and power budgets flat, **general-purpose “do-everything” microarchitectural tricks** (big caches, aggressive OoO, deep speculation) are often the wrong use of transistors for many workloads.  
> DSAs recycle that silicon into **domain-tailored compute + memory**, yielding **much higher performance/W** (often the primary goal).

---

## 0) What is a DSA?

A **Domain-Specific Architecture (DSA)** is a special-purpose processor optimized for a *narrow domain*, relying on CPUs/GPUs for everything else.  
Typical DSA targets in this chapter:
- **DNN inference** (Google TPU)
- **DNN training** (Intel Crest / Lake Crest)
- **Ranking / networking / CNN acceleration** via **reconfigurable** FPGA (Microsoft Catapult)
- **Image/vision processing** in mobile devices (Pixel Visual Core “IPU”)

---

## 1) 7.2 — Five guidelines for designing DSAs (high-yield)

These are the chapter’s “rules of thumb” that the four case studies follow.

1) **Use dedicated memories** (software-managed scratchpads / buffers)  
   - Minimize data movement distance.  
   - Example fact: a 2-way set-associative cache can use **~2.5×** the energy of an equivalent software-controlled scratchpad.

2) **Spend saved resources on more compute units or bigger on-chip memories**  
   - Dropping advanced microarchitectural optimizations frees area/power for what the domain *actually* needs.

3) **Use the easiest parallelism that matches the domain**  
   - If SIMD fits, prefer it over MIMD for simplicity/efficiency.  
   - If VLIW can expose ILP, it can be smaller/more energy-efficient than OoO.

4) **Reduce data size/type to the simplest that works**  
   - Many domains are memory-bound → narrower types increase effective bandwidth and allow more compute per mm².

5) **Use a domain-specific programming language/framework**  
   - Don’t assume people will rewrite code “just for your chip.”  
   - Examples: **TensorFlow** (DNN), **Halide** (vision).

Bonus effects called out:
- simpler designs → lower NRE
- more deterministic performance → better for **p99 response-time** constraints than time-varying CPU/GPU optimizations.

---

## 2) 7.3 — Example domain: Deep Neural Networks (DNNs)

### 2.1 Training vs inference
- **Training**: iterative weight updates via **backpropagation** (can take very long; the chapter notes month-scale training is plausible).  
- **Inference**: production-time forward pass; often **latency-bound** (p99/p99.9), not just throughput-bound.

### 2.2 Three dominant DNN families (chapter framing, ~2017)
1) **MLP (multilayer perceptron)**
2) **CNN (convolutional neural network)**
3) **RNN**, especially **LSTM**

### 2.3 Why “operations per weight” matters (DNN roofline)
The chapter uses a DNN-tailored operational intensity: **operations per weight fetched**, because weights are often huge and don’t fit on-chip.

#### MLP layer model
- Weights: `Dim[i-1] * Dim[i]`
- Ops (mul+add counted separately): `2 * weights`
- **Ops/weight ≈ 2**  → often **memory-bound**

#### CNN layer model (2D stencil intuition)
- CNNs reuse weights across spatial positions → **very high Ops/weight**
- Example given yields **Ops/weight = 392** for one CNN layer configuration → often **compute-bound**

#### LSTM cell model (high-level)
- LSTMs include multiple vector–matrix multiplies per cell; despite more structure, the chapter’s example ends up with **Ops/weight ≈ 2.0003**, again similar to MLP → typically **memory-bound**

### 2.4 Batching
A major performance trick: process inputs in **batches/minibatches** so weights fetched from memory can be reused across many inputs, boosting effective operational intensity.

---

## 3) 7.4 — Google TPU (Inference data center accelerator)

### 3.1 Why TPU exists
- Domain: **DNN inference** in WSCs  
- Deployed in Google data centers in **2015**
- Designed for **deterministic, single-threaded execution**, which matches **p99 response-time** needs for user-facing inference.

### 3.2 TPU core architecture
- **Matrix Multiply Unit (MMU):** **65,536 = 256×256** 8-bit multiply-add ALUs (64K MAC)  
- **Accumulators:** **4 MiB** of 32-bit accumulators (e.g., 4K×256×32b)  
- **On-chip Unified Buffer:** **24 MiB** SRAM (e.g., 96K×256×8b) for activations/intermediates  
- **Weight memory:** **8 GiB DRAM** off-chip (read-only for inference); staged through an on-chip **Weight FIFO**
- Supports 8-bit weights/activations primarily; mixed 8/16-bit runs at reduced speed; accumulates in 32-bit.

### 3.3 Systolic execution (why it’s energy-efficient)
The MMU uses **systolic dataflow** to reduce expensive SRAM reads/writes of the Unified Buffer: data streams through a 2D array of MAC units, each computing partial results and passing data downstream.

### 3.4 TPU ISA style
- Host-controlled execution over PCIe
- CISC-like commands with repeats; **no program counter** and **no branches**
- Typical CISC instruction CPI: **~10–20 cycles**
- Key command families: read host memory → Unified Buffer; read weights → FIFO; matrix multiply/convolution; etc.

### 3.5 TPU microarchitecture “what mattered most”
Performance modeling + counters showed:
- Increasing **weight-memory bandwidth** had the biggest performance effect.
- Increasing clock alone helped little if memory bandwidth didn’t improve.
- A hypothetical redesign using GDDR5 for weight memory could raise performance substantially (the chapter reports ~3.2× average improvement in one what-if).

---

## 4) 7.5 — Microsoft Catapult (Flexible data center accelerator via FPGA)

### 4.1 What Catapult is
Catapult uses an FPGA as an accelerator platform. Key advantage: **reconfigurability** → “many DSAs on one device.”

### 4.2 V1 hardware snapshot (numbers worth memorizing)
- Board power/cooling target: **25 W**
- FPGA: **28 nm Altera Stratix V D5**
- Off-chip memory: **8 GiB DDR3-1600** (two banks)
- On-chip resources: **3926 18-bit ALUs**, **5 MiB on-chip memory**
- DDR3 bandwidth: **~11 GB/s**
- Additional flash: **32 MiB**

### 4.3 Scale-out network (V1)
- 1 Catapult board per server; **48 servers** (half rack) connected by a separate low-latency **20 Gbit/s** FPGA network
- Topology: **6×8 torus**
- Designed to tolerate failures (reconfigurable) and avoid single points of failure
- SECDED on memories outside the FPGA

### 4.4 Example applications
- **Configurable CNN accelerator:** runtime configurable (layers, sizes, precision), uses buffering + 2D PE arrays; systolic-like PE design.
- **Bing ranking accelerator:** pipelined design with latency constraints (user-facing). Uses unusual parallelism patterns, including many independent instruction streams over a document (MISD-style framing in the text).

### 4.5 Catapult V2: “bump-on-a-wire”
V1’s separate FPGA network couldn’t process standard Ethernet/IP traffic, limiting use in network acceleration.  
V2 places FPGA **between CPU and NIC**, so all traffic passes through FPGA — enabling both Bing + Azure networking use cases and simplifying deployment.

---

## 5) 7.6 — Intel Crest / Lake Crest (Training accelerator)

Crest is aimed at **DNN training**, with a public goal statement of **100× training acceleration** over a few years.

Key architectural points (as described in the chapter):
- Operates on **blocks of 32×32 matrices**
- Uses **flex point** numeric format:
  - 32×32 matrices of **16-bit data share one 5-bit exponent** (scaled fixed-point representation)
- Uses **12 processing clusters**, each with:
  - large SRAM
  - a “big” linear algebra processing unit
  - routing logic (on-/off-chip)
- Memory: **four 8 GiB HBM2 modules**
- Reported memory bandwidth: **~1 TB/s** (supports very high roofline potential)

---

## 6) 7.7 — Pixel Visual Core (mobile Image Processing Unit, “IPU”)

### 6.1 Why IPUs exist
An **ISP** (image signal processor) is common in PMDs, but is often fixed-function. As demand for better image quality grows, fixed pipelines become too inflexible and underutilized outside camera workloads.

Pixel Visual Core is positioned as a programmable IPU: analyze/transform input images (inverse of GPU “render output images”).

### 6.2 Energy reality in mobile
The chapter emphasizes huge energy gaps:
- An **8-bit DRAM access** can cost as much energy as **12,500 8-bit adds** (order-of-magnitude message: move/DRAM is expensive).

### 6.3 Core compute model (2D SIMD + halo)
- Core contains a **16×16** array of independent **processing elements (PEs)** plus a surrounding **halo** region to support stencils efficiently.
- Each PE includes:
  - **2× 16-bit ALUs**
  - **1× 16-bit MAC**
  - **10× 16-bit registers**
  - **10× 1-bit predicate registers**
- Each PE has compiler-managed scratchpad memory:
  - logical size: **128 entries × 16-bit = 256 bytes**
  - implemented by grouping PE memories into shared SRAM blocks for efficiency

Halo overhead:
- For a 16×16 array with halo, the chapter notes ~**20% area** overhead for halo support, and gives throughput ratios for stencils (e.g., 5×5 vs 3×3) illustrating “bigger arrays reduce halo fraction.”

### 6.4 Memory system (line buffers + sheet generator)
- Includes a load/store unit called **Sheet Generator (SHG)** that moves rectangular blocks (“sheets”) of pixels.
- Uses **line buffers** as multi-reader 2D FIFO abstractions implemented in SRAM (the chapter cites **128 KiB per instance**).
- Includes DMA engines that can convert image layouts and support sequential/strided/gather-like reads.

### 6.5 Programming model
- Programmed via **Halide** (vision) and TensorFlow (CNNs).
- Two-step compilation (virtual ISA → physical ISA).  
- VLIW-style “pISA” with short kernels; instruction memory example: **2048 pISA instructions (~28.5 KiB)**.

### 6.6 Claimed impact (in chapter)
For CNNs, Pixel Visual Core performance per watt is described as **~25–100× better** than CPUs/GPUs (context: domain-specific design + narrow integer arithmetic + local memories).

---

## 7) 7.8 Cross-cutting issues

### 7.8.1 Integration vs I/O-bus accelerators (Amdahl for data movement)
If data must constantly cross the host↔accelerator boundary, the speedup is limited.  
Hence push toward **SoC integration** and **IP blocks** (portable design blocks integrated into SoCs).

### 7.8.2 IP blocks dominate modern SoCs
The chapter cites evidence from Apple SoCs:
- number of IP blocks roughly **tripled in 4 years**
- CPU+GPU may occupy only **~1/3 of SoC area**, with IP blocks taking the rest

### 7.8.3 Open ISA matters: RISC‑V
Choosing a CPU ISA for an SoC used to mean licensing a proprietary ISA or building your own RISC + toolchain.  
**RISC‑V** is highlighted as a viable open ISA with opcode space for domain extensions, lowering integration cost and friction.

---

## 8) 7.9 Putting it together: CPUs vs GPUs vs DNN accelerators

### 8.1 Benchmarks + latency constraints
The chapter compares six DNNs (two each of MLP/CNN/LSTM), representing **95% of TPU inference workload in Google data centers in 2016**.  
Inference workloads are typically part of user-facing services → **hard latency bounds**.

### 8.2 TPU vs CPU vs GPU (selected measured data from Figures 7.42–7.43)

**Chip-level snapshot (per die):**
- **Intel Haswell:** 22 nm, 2300 MHz, 662 mm², 145 W TDP; measured idle/busy ~41/145 W; measured TOPS (8b/FP) shown as 2.6 / 1.3; memory BW 51 GB/s; on-chip mem 51 MiB.
- **NVIDIA K80:** 28 nm, 560 MHz, 561 mm², 150 W TDP; measured idle/busy ~25/98 W; measured TOPS shown as “– / 2.8”; memory BW 160 GB/s; on-chip mem 8 MiB.
- **TPU:** 28 nm, 700 MHz, die size <331 mm² (stated < half of Haswell), 75 W TDP; measured idle/busy ~28/40 W; measured TOPS (8b/FP) shown as 92 / 34; on-chip mem 28 MiB.

**Server-level snapshot (benchmarked systems):**
- Haswell server: 2 dies, 256 GiB DRAM, 504 W TDP; measured idle/busy ~159/455 W.
- K80 server: 8 GPU dies + host DRAM (256 GiB) + 12 GiB per GPU die; 1838 W TDP; measured idle/busy ~357/991 W.
- TPU server: 4 TPU dies + host DRAM (256 GiB) + **8 GiB DRAM per TPU** as weight memory; 861 W TDP; measured idle/busy ~290/384 W.

### 8.3 Roofline + “why latency matters”
The chapter shows that many models hit the TPU roofline ceiling (CNNs compute-bound; MLP/LSTM memory-bound), but **response-time limits** keep CPU/GPU implementations further below their ceilings.  
Inference cares about throughput **only while maintaining latency bounds**.

### 8.4 Bottom-line comparisons (chapter’s reported results)
- Using the measured mix of workloads:
  - TPU is reported **~29.2× faster than CPU per die** and **~15.3× faster than GPU per die** (host overhead included for accelerators).
- Performance/W (proxy for TCO):
  - TPU server: **~34×** better total perf/W than Haswell; **~16×** perf/W vs K80 server.
  - Incremental perf/W (excluding host CPU power): TPU reported **~83×** vs Haswell baseline; **~29×** vs GPU.

### 8.5 Catapult and Pixel Visual Core (brief comparison snippets)
- Catapult V1 CNN acceleration: **~2.3×** faster than a 2.1 GHz 16-core dual-socket server; later FPGAs (Arria 10, 14 nm) can raise performance substantially while power rises less than ~1.2× (as described).
- Pixel Visual Core: CNN perf/W described as **25–100×** better than CPUs/GPUs.

---

## 9) 7.10 Fallacies & pitfalls (very exam-friendly)

### Fallacy: “A custom chip costs $100M”
The chapter cites a breakdown showing a **$50M** custom ASIC cost estimate (not $100M), with a major portion being salaries.

Cost breakdown (Figure 7.51):
- Software: **$15.75M**
- Hardware engineering: **$13.5M**
- EDA tools: **$9.0M**
- Fabrication: **$5.0M**
- IP: **$5.0M**
- Sales + management: **$4.5M**

Also noted:
- For small chips, multi-project reticles can reduce mask/fab burden; an example claim: **$30k for 100 untested 28 nm parts** (small-chip context).

### Pitfall: “GPUs/CPUs optimized for average throughput automatically satisfy p99 latency”
User-facing inference often needs predictable p99 response time. DSAs with simpler, deterministic execution can match that better than time-varying cache/OoO/SMT behavior.

---

## 10) 7.11 Concluding remarks (what to remember)

The chapter’s synthesis for why TPU-style DSAs succeed:
- large matrix unit + substantial software-controlled on-chip memory
- ability to run most inference without heavy host dependence
- deterministic single-threaded model suited to p99 deadlines
- omitting general-purpose features → smaller, lower power
- enough flexibility to track evolving DNNs

It also offers a “Cornucopia Corollary” framing: **a huge, cheap resource can be valuable even at low utilization** (because the resource is cheap and the workload mix is massive).

---

## One-page carryover (low-context)

- DSAs = recycle “general CPU tricks” into domain-tailored compute/memory for performance/W.  
- 5 guidelines: dedicated memories; reallocate area to compute/mem; simplest matching parallelism; narrow types; domain-specific languages.  
- DNNs: MLP/LSTM often memory-bound (ops/weight ~2); CNN often compute-bound (ops/weight high); batching boosts weight reuse.  
- TPU: 256×256 8-bit systolic MMU (64K MAC), 24 MiB UB, 4 MiB accum, 8 GiB weight DRAM, deterministic host-driven ISA.  
- Catapult: FPGA platform (25 W) + torus interconnect; V2 bump-on-a-wire enables networking use cases.  
- Crest/Lake Crest: training accelerator with 32×32 matrix ops, “flex point”, 12 clusters, HBM2 (~1 TB/s).  
- Pixel Visual Core: mobile IPU, 2D SIMD PEs + halo + scratchpads/line buffers; Halide/TensorFlow programming; strong perf/W for CNNs.  
- Costs: custom chip isn’t automatically $100M; $50M breakdown highlights software and hardware engineering as dominant.

---

*End of Chapter 7 summary.*
