# CH12 — Embedded Systems (Appendix E) (Summary)

> Source PDF: `ch12-appendix-e-embedded-systems.pdf`  
> Note: In this PDF set, “Chapter 12” corresponds to **Appendix E: Embedded Systems**.

---

## 0) What this appendix is really teaching you

Embedded systems are **computers hidden inside products**, and their design constraints differ sharply from desktops/servers:

- **Cost and power dominate** (often more than raw performance).
- **Code size and memory size** matter (many systems must fit entirely in on-chip memory or small off-chip Flash/DRAM).
- Many applications are **real-time**, so engineers care about **worst-case execution time (WCET)** and predictability, not just average speed.
- Increasingly, embedded systems are **SoCs (“core + ASIC”)**: a programmable core plus dedicated hardware engines.

---

## E.1 Introduction: what makes embedded “different”

### Embedded market breadth
Embedded devices range from:
- low-end 8/16-bit controllers in appliances,
- to high-end phones, set-top boxes, cameras, consoles, network switches.

Many embedded products run one “fixed” application:
- programming occurs mainly at initial load or later firmware updates,
- sometimes with small hand-tuned assembly loops, but time-to-market limits extensive assembly.

### Real-time: why caches/speculation can be “the enemy”
Hard real-time systems need provable deadlines.
- Branch speculation, caches, and other adaptive mechanisms introduce **execution-time uncertainty**.
- WCET analysis that assumes “all branches mispredict and all caches miss” can be overly pessimistic, forcing expensive overdesign.

Key tension:
- general-purpose tricks boost average performance,
- embedded often needs **predictable** performance.

---

## E.2 Digital Signal Processors (DSPs): the embedded “math engine”

### 2.1 DSP kernel: MAC dominates
Many signal-processing algorithms (FIR/IIR filtering, convolution, FFT/DCT, FEC encodings) reduce to repeated multiply–accumulate:

- DSP MAC semantics:
  \[
  A \leftarrow A + B\cdot C
  \]

Because MAC throughput can determine system viability, DSP selection is sometimes driven almost entirely by MAC performance.

### 2.2 Fixed-point arithmetic and “blocked floating point”
DSPs often use **fixed-point** arithmetic for cost/power efficiency:
- Think of fixed-point as “cheap floating point” without per-number exponents.
- The exponent is tracked separately by the program; a block of values share one exponent:
  - hence “blocked floating point.”

DSPs therefore provide:
- **wide accumulators / guard bits** to reduce round-off error.
- Word sizes not necessarily powers of two (DSP designers aren’t constrained like general CPUs).

### 2.3 DSP instruction semantics: saturation and compare-select
Because many DSP tasks are real-time, exceptions on overflow are unacceptable.
- DSPs often use **saturating arithmetic**: clamp overflow to max/min representable value rather than wrap around (two’s complement wrap can be disastrous in signal loops).

For FEC (e.g., Viterbi decoding), DSPs include **compare-select** style operations.

---

## E.2 DSP case studies: Texas Instruments C55 vs C6x

### 2.4 TI TMS320C55 — low-power DSP
- Designed for battery-powered embedded applications.
- Seven-stage pipelined CPU (fetch, decode, address, etc.).
- Hazard detection and stalls on RAW/WAR.
- Instruction cache (~24 KiB) configurable:
  - 2-way set associative, direct-mapped, or “ramset”.
  - “ramset” mode supports hard real-time by **preventing replacement**.

**Power management:** “idle domains”
- hardware blocks grouped into domains (CPU, DMA, peripherals, clock generator, I-cache, external memory interface).
- an IDLE instruction + control register can place selected domains into low-power state.

### 2.5 TI VelociTI C6x (e.g., C64x) — high-performance VLIW DSP
- Powerful **eight-issue VLIW** family.
- Example pipeline depth: ~11 stages (fetch, decode, execute).
- Execution units split into two sides (“1” and “2”), each with its own register file.
  - Cross-side register access costs ~1 cycle.

**Key compiler features:**
- software pipelining is central but struggles with control flow → C6x supports **predication**:
  - instruction executes, but writes results only if predicate register is true.
  - helps convert if-then(-else) into straight-line code for software pipelining.

---

## E.2 Media extensions: SIMD “middle ground”
Media extensions add DSP-like vector ops to general microcontrollers/CPUs at low cost:
- narrow data lanes (bytes/halfwords) for audio/video/pixels.
- operations include packed add/sub, saturating add/sub, multiply, compare, permute/shuffle, etc.

DSP variants differ from desktop SIMD:
- saturating arithmetic is common (avoid exceptions, preserve real-time correctness).

---

## E.3 Embedded benchmarks

### Why Dhrystone is bad here
Embedded workloads vary too much; one benchmark is misleading.
Historically many vendors used Dhrystone anyway, despite it being discredited in general-purpose computing.

### EEMBC (“embassy”)
EEMBC is positioned as a better standardized kernel benchmark suite.
It has six major classes (“subcommittees”):
- automotive/industrial
- consumer
- telecommunications
- digital entertainment
- networking (v2)
- office automation (v2)

### Energy as a first-class metric: EnergyBench
Embedded selection often prioritizes power/energy.
EEMBC **EnergyBench** / “Energymark” provides energy consumption while running performance benchmarks (optional certified metric).

---

## E.4 Embedded multiprocessors (SoCs)

Why embedded adopts multiprocessors more easily:
1) Binary compatibility constraints are weaker; code is often rewritten/tuned per product.
2) Applications often have “natural parallelism” (graphics pipelines, telecom streams, set-top boxes, phones).

Common pattern:
- a general-purpose core/DSP + multiple fixed-function engines / stream processors.
- Communication is often regimented (channels/DMAs), but correctness is still challenging.

---

## E.5 Case study: Sony PlayStation 2 “Emotion Engine”

### System architecture (what to remember)
The PS2 is an embedded multiprocessor with heavy DMA orchestration.

Key elements (as described):
- Main memory: **32 MiB DRDRAM** via two channels, peak ~**3.2 GB/s**
- Two major chips:
  1) **Graphics Synthesizer** with embedded DRAM for extreme pixel bandwidth (2048-bit interface).
  2) **Emotion Engine**:
     - superscalar MIPS CPU core with **128-bit SIMD**
     - Vector Unit 0 (VPU0), tightly coupled as MIPS coprocessor instructions
     - Vector Unit 1 (VPU1), more autonomous for building display lists
     - **10-channel DMA** controlling transfers among many small memories/units

### Embedded design lesson
Rather than coherent caches, PS2 uses:
- multiple dedicated memories + DMAs,
- double-buffering (input/output buffers),
- explicit programmer-managed dataflow to meet real-time frame deadlines (e.g., ~15 fps target mentioned).

This reflects a core embedded pattern: **specialized local memories + explicit movement** instead of large coherent caches.

---

## E.6 Case study: Sanyo VPC‑SX500 digital camera

End-to-end pipeline:
1) Boot diagnostics → LCD display.
2) Half-press shutter → light reading.
3) CCD captures RGB pixels (1/2-inch, 1360×1024 progressive scan).
4) Image processing: white balance, color correction, aliasing correction.
5) Store in a **4 MiB frame buffer**.
6) Compress to JPEG (fine/normal; compression ratio ~10–20×).
7) Save to removable Flash.

Concrete storage example:
- 512 MiB Flash stores ~1200 “fine” or ~2000 “normal” images (as described).

---

## E.7 Case study: inside a cell phone

### Why phones are embedded “leaders”
Handsets are sold at massive volumes, driving aggressive engineering per cubic inch.
Battery efficiency is critical (standby + talk time).

### Typical handset split: microcontroller + DSP
- **DSP**: signal processing (compression/decompression, coding/decoding).
- **Microcontroller**: UI, control, base-station coordination, system management.

### Wireless basics (high-level)
- Radio waves are modulated; frequency allocation is regulated (FCC in US example).
- Wireless BER is far worse than wired; power is limited by batteries and propagation loss.
- Two architectures:
  - **base station** (cellular)
  - **peer-to-peer** (multi-hop)

### Call setup behavior (example)
- Phone scans bands for strongest signal, repeats periodically (e.g., every 7 seconds).
- Selects an unused channel; network registers device; assigns voice channel.
- Handoff occurs as signal drops and the phone moves.

### Standards evolution (examples)
Second-generation digital standards mentioned include:
- **CDMA**, **TDMA**, **GSM**
CDMA uses spread-spectrum ideas: calls share a wide channel with pseudorandom codes; base station separates streams.

---

## E.8 Concluding remarks (what to carry forward)

- Embedded architectures strongly diverge from desktop/server designs due to:
  - cost, power, area, and real-time constraints
- DSPs and media extensions exist because signal processing is ubiquitous.
- Many embedded systems are SoCs combining programmable cores with specialized engines.
- Programmers/compilers often carry more responsibility for parallelism and data movement than in general-purpose systems.

---

## Flashcards (quick recall)

**Q1. What makes embedded systems different from desktops?**  
A. Wider cost/power range; strong code-size/memory constraints; real-time predictability; SoC integration with ASIC blocks.

**Q2. DSP “kernel operation”?**  
A. Multiply-accumulate (MAC): \(A \leftarrow A + B\cdot C\).

**Q3. What is blocked floating point?**  
A. Fixed-point style where a block of values shares one exponent tracked separately.

**Q4. Why do DSPs use saturating arithmetic?**  
A. Real-time systems can’t afford overflow exceptions; clamping avoids wraparound artifacts.

**Q5. What’s “ramset” cache mode (C55)?**  
A. Cache blocks cannot be replaced → helps hard real-time predictability.

**Q6. Why is VLIW popular in embedded?**  
A. High ILP with less complex hardware; binary compatibility pressure is lower.

**Q7. How does C6x handle control flow for software pipelining?**  
A. Predication: execute but conditionally commit results.

**Q8. PS2 key embedded lesson?**  
A. Multiple dedicated memories + DMA + explicit dataflow instead of cache coherence.

---

*End of CH12 / Appendix E summary.*
