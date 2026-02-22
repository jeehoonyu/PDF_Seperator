# CH18 — Survey of Instruction Set Architectures (Appendix K) (Summary)

> Source PDF: `ch18-appendix-k-survey-of-instruction-set-architectures.pdf`  
> Note: In this PDF set, “Chapter 18” corresponds to **Appendix K: Survey of Instruction Set Architectures**.  
> What’s included in this PDF: **K.1–K.4** (RISC survey, Intel 80x86, VAX) + concluding/fallacies. *(The TOC mentions IBM 360/370, but I did not find the full K.5/K.6 content in this file.)*

---

## 0) What this appendix is really teaching you

This appendix is about **ISA “fashion cycles”** and the engineering forces behind them:

- **RISC convergence (post-1985):** desktop/server/mobile ISAs became remarkably similar.
- **Compatibility inertia:** x86’s “golden handcuffs” show how backwards compatibility shapes an ISA for decades.
- **Code density vs implementation simplicity:** VAX represents the “code density + high-level machine language” era; modern pipelines made that style expensive.

---

## 1) K.1 Introduction: the 10-ISA scope and why it’s here

The appendix surveys multiple ISAs:
- modern RISCs (desktop/server/PMD) using **RISC‑V as a comparison baseline**
- embedded RISCs (16-bit compressed subsets)
- Intel **80x86**
- **VAX** (historical CISC representative)

Stated motivation: keep both living and retired ISAs to show how ISA design priorities changed over time.

---

## 2) K.2 Survey of RISC architectures (desktop/server/PMD + embedded)

### 2.1 The “big five” RISCs (desktop/server/PMD)
The appendix compares recent versions of:
- **ARMv8 AArch64 (64-bit)**
- **MIPS64 (v6)**
- **Power ISA v3.0**
- **RISC‑V RV64G**
- **SPARCv9**

**Headline claim:** these architectures are *remarkably similar* (Figure K.1 style comparison).

#### Why they converge
Across all five, common traits dominate:
- load-store design
- fixed instruction widths (32-bit base)
- small set of addressing modes (mostly reg + immediate/displacement)
- PC-relative control transfers
- similar instruction format families (reg-reg, reg-imm, branch, jump/call)

### 2.2 Embedded RISC “compressed” subsets (16-bit focus)
Three embedded-oriented 16-bit instruction modes are compared:
- **Thumb‑2** (ARM family)
- **microMIPS64** (MIPS family)
- **RISC‑V compressed (C) extension** (RV64GC context)

Key pattern: 16-bit subsets improve **code density** by:
- limiting which registers are addressable (often only 8 “core” registers for most ops),
- shrinking immediate fields,
- increasing the number of formats even though the total ISA is smaller.

**Important design difference:**  
RISC‑V planned 16-bit support from the beginning, so branch/jump alignment and encodings are naturally compatible. microMIPS alters branch/jump interpretation to 16-bit alignment. Thumb‑2’s 32-bit subset is not “just ARMv7”; it’s a related but distinct ISA subset.

---

## 3) Addressing modes and instruction formats (RISC side)

### 3.1 Simplified addressing is the RISC signature
Desktop/server RISCs largely rely on:
- displacement (base + immediate offset)
- register indirect (offset = 0)
- PC-relative for branches
- register-indirect jumps for returns/function pointers

A typical “zero register” makes limited absolute addressing easy:
- use x0 (or equivalent) as base in displacement addressing.

Embedded 16-bit modes restrict both:
- register choices for address calculation,
- displacement sizes.

### 3.2 Instruction formats: the “four core shapes”
Across the big five RISCs, **four primary formats** cover ~90–98% of instructions (Figure K.6 style):
1) register-register ALU
2) register-immediate (also loads/stores for some ISAs)
3) conditional branch
4) jump/call

The formats are not identical in bit placement, but the “family resemblance” is strong.

---

## 4) K.3 The Intel 80x86 (x86 / IA‑32 / x86‑64): compatibility-driven evolution

### 4.1 Why x86 is “messy”
The appendix explicitly frames x86 as:
- evolved by many groups over ~20+ years,
- extended repeatedly without breaking old software,
- “adding new features to the original instruction set” under compatibility pressure.

### 4.2 Milestones (high-yield timeline)
- **1978 — 8086:** 16-bit, extension of 8080; “extended accumulator” flavor (many registers have dedicated roles).  
- **1980 — 8087:** floating-point coprocessor, described as an “extended stack” style FP architecture.  
- **1982 — 80286:** 24-bit addressing + complex protection/mapping model; “real mode” preserved 8086 compatibility.  
- **1985 — 80386:** 32-bit registers + 32-bit addressing; added new modes and paging on top of segmentation; still runs 8086 programs via compatibility mode.  
- **2003 — AMD64:** 64-bit addressing (“long mode”), widens registers, increases GPR count to 16, adds 16×128b XMM registers; implemented via prefixes and a new mode rather than redesigning the whole ISA. Intel later followed with near-identical changes for compatibility.

### 4.3 Architectural “flavor”
- Variable-length instruction encoding (many prefixes, multiple formats).
- Historically heavy use of **register-memory** operations (ALU ops can use memory operands).
- Legacy segmentation + protection complexities (later mostly deemphasized in 64-bit mode).

### 4.4 Register set evolution (how to read x86 registers)
The appendix shows the evolution from:
- AX/BX/CX/DX (16-bit) with split high/low byte access (AH/AL etc.)
to
- EAX… (32-bit)
to
- 64-bit extensions (not fully shown in the diagram, but described in text)
and x87 FP registers (stack-like) plus SSE/AVX-era vector registers.

---

## 5) K.4 The VAX architecture: “code density + rich addressing modes”

VAX is used as a canonical example of 1970s CISC values:
- reduce code size,
- provide high-level machine language features,
- support many data types and addressing modes,
- accept more complex decode/implementation.

### 5.1 VAX register model
- 16 architected 32-bit registers, but several are effectively special:
  - r14 = stack pointer (sp)
  - r15 = program counter (pc)
  - r12 = argument pointer (ap)
  - r13 = frame pointer (fp)

### 5.2 Addressing modes: “operand specifiers are separate”
VAX’s core design pattern:
- opcode specifies operation + number of operands
- **each operand has its own addressing-mode specifier**
- addressing mode is separated from operation → extremely flexible operand sourcing.

Examples of VAX addressing richness:
- register and immediate
- displacement (base+offset)
- PC-relative
- register deferred (pointer)
- **indexed addressing** that scales indices automatically (“scaled addressing”), so array indexing does not require explicit multiply-by-element-size in code.

### 5.3 Why this matters: code density
VAX reduces redundant operand fields:
- `addl2 src, dst` uses dst as both source and destination (2-operand form)
- `addl3 src1, src2, dst` for full 3-operand form
This often shrinks instruction bytes compared to fixed 3-operand RISC encodings.

### 5.4 Condition codes + branches
VAX uses classic condition codes:
- N (negative), Z (zero), V (overflow), C (carry)
Most arithmetic sets them as a side effect; branches read them.
The appendix highlights how this can eliminate explicit compare instructions in some loop patterns (because loop update sets codes).

### 5.5 Procedure calls: CALLS/RET with register-save masks
VAX includes call/return instructions that:
- save/restore registers based on a **register mask** in the callee’s code
- allow compact calling sequences compared to explicit push/pop sequences.

The appendix demonstrates this using code-generation examples (`swap` and `sort`):
- VAX uses fewer assembly lines than MIPS for the same high-level code due to:
  - scaled indexed addressing
  - CALLS/RET register save/restore machinery
but it also warns: fewer instructions **does not automatically mean faster** (decode complexity and memory traffic matter).

---

## 6) Concluding remarks: RISC homogeneity vs older diversity

The appendix explicitly notes:
- covering 8 RISCs in a few pages is possible because they are so similar
- it would not be feasible to do this for 1970s-era architectures due to higher diversity
- this era represents an unusually broad consensus in ISA design since RISC emerged in the 1980s

---

## 7) Fallacies and pitfalls (exam-friendly)

### Pitfall: “It is possible to design a flawless architecture.”
ISA design is a set of trade-offs under current technology constraints.
Technology changes (pipelines, caches, memory latency, fabrication limits) can make past “correct” decisions look wrong later.

Example given: VAX designers heavily optimized code density and underestimated how important decode/pipelining would become later.

### Pitfall: Instruction count = performance
The appendix’s MIPS vs VAX examples emphasize:
- fewer instructions can mean more complex instructions, more memory traffic, slower decode, or lower clock
- performance depends on CPI, cache behavior, pipeline compatibility, and implementation quality.

---

## Practical carry-forward checklist

When you compare ISAs, ask:
1) Operand location model: stack / accumulator / register-memory / load-store  
2) Addressing modes: how many, and how expensive to implement?  
3) Encoding: fixed vs variable; are there compressed subsets?  
4) Control flow: PC-relative branches? register-indirect jumps? predication?  
5) Compatibility constraints: can the ISA change freely, or is it “handcuffed”?  
6) Compiler friendliness: regular formats and simple addressing usually win long-term.

---

## Flashcards (quick recall)

**Q1. Why do modern RISCs look similar?**  
A. Shared design goals: pipeline-friendly fixed formats, load-store model, limited addressing modes, compiler-centered design.

**Q2. What’s the key purpose of 16-bit “compressed” ISA subsets?**  
A. Improve code density (smaller binaries → fewer I-cache misses and memory bandwidth use), at cost of more formats and restricted register/immediate access.

**Q3. Why is x86 hard to summarize cleanly?**  
A. Incremental extensions over decades under strict backward compatibility; variable-length encoding + legacy features.

**Q4. What is VAX’s distinctive operand encoding idea?**  
A. Each operand has its own addressing-mode specifier, independent of opcode → very flexible but decode/implementation heavy.

**Q5. Why can VAX use fewer instructions than MIPS for some code?**  
A. Memory-to-memory operations, scaled indexed addressing, and CALLS/RET register-save machinery reduce explicit instruction count.

---

*End of CH18 / Appendix K summary.*
