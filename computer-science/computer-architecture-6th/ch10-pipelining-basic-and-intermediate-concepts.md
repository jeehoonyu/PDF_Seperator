# CH10 — Pipelining: Basic and Intermediate Concepts (Appendix C) (Summary)

> Source PDF: `ch10-appendix-c-pipelining-basic-and-intermediate-concepts.pdf`  
> Scope: Appendix **C.1–C.9** + key equations, mechanisms, and case study (MIPS R4000).

---

## 0) What this appendix is really teaching you

Pipelining is the core trick that makes CPUs fast: **overlap the execution of multiple instructions** so you complete ~1 instruction per cycle in the ideal case.

But the real engineering is not “draw the 5 stages.” It’s:
- quantifying **speedup limits** (stage imbalance + pipeline overhead),
- handling **hazards** (structural / data / control),
- and maintaining correct behavior under **exceptions/interrupts** while keeping performance high.

---

## 1) C.1 — Pipelining fundamentals

### 1.1 Throughput vs latency
- **Latency**: how long one instruction takes from start to finish.
- **Throughput**: how many instructions complete per unit time.

Pipelining mostly improves **throughput** (one completes each cycle ideally), while single-instruction latency may stay similar or even increase (more stages).

### 1.2 Pipeline depth, stage balance, and overhead
Two practical limits reduce pipelining gains:
- **Imbalance**: cycle time is set by the slowest stage.
- **Overhead**: pipeline registers add setup/propagation delay; clock skew also eats cycle time.

**Example from the appendix** (numbers worth remembering):
- Unpipelined: 4 GHz (0.5 ns cycle). ALU/branch take 4 cycles; memory ops take 5 cycles; frequencies 40% / 20% / 40%.
- Average unpipelined time:
  - Avg CPI = (0.40+0.20)·4 + 0.40·5 = 4.4 cycles
  - Avg time = 0.5 ns · 4.4 = **2.2 ns**
- Pipelined overhead adds **0.1 ns** → cycle becomes 0.5 + 0.1 = **0.6 ns**
- Speedup = 2.2 / 0.6 = **3.7×**  
  → overhead alone can cap achievable speedup.

### 1.3 Classic 5-stage RISC pipeline intuition
The appendix uses a simple RISC pipeline (RISC‑V subset) with stages:
- **IF** instruction fetch
- **ID** decode + register read
- **EX** execute / address calc
- **MEM** data memory access
- **WB** register write-back

To avoid conflict in the register file:
- do **write** in first half of cycle and **read** in second half (also helps some RAW cases).

---

## 2) C.2 — Pipeline hazards (the “major hurdle”)

Hazards force **stalls** (bubbles), raising CPI above 1.

### 2.1 Structural hazards (resource conflicts)
Hardware can’t support all combinations of overlapped instructions.
- In modern CPUs, structural hazards mostly show up in **rare special units** (e.g., long-latency divide).

### 2.2 Data hazards (dependences exposed by overlap)
Most important is **RAW** (read-after-write).  
Classic example:
- `add x1, x2, x3`
- `sub x4, x1, x5`  → needs x1 before it’s written back

#### Forwarding / bypassing (eliminate many stalls)
Forward results from pipeline registers directly into later stages instead of waiting for WB.
- You often need forwarding to **either ALU input**, and sometimes to memory inputs too.

#### Load-use hazard (stall required)
A load produces data at end of MEM stage; an immediately following ALU op needs it at beginning of EX.
- No “backwards-in-time forwarding” exists.
- Solution: **pipeline interlock** inserts a 1-cycle bubble so the consumer executes later.

### 2.3 Control hazards (branches)
Branches break the “PC+4 always” assumption.

The appendix walks through several branch-handling schemes:

1) **Freeze/flush** (stall until branch resolved)  
   - simplest, fixed penalty

2) **Predict not taken**  
   - fetch fall-through path immediately  
   - if taken, flush wrong-path work

3) **Predict taken**  
   - start fetching from target earlier (target known before condition is fully evaluated)

4) **Delayed branch** (classic early RISC technique)  
   - next instruction (delay slot) always executes, whether branch is taken or not

**Performance framing for branch penalties** (ideal CPI=1):
\[
\text{Pipeline speedup}=\frac{\text{Pipeline depth}}{1 + \text{Branch frequency}\times \text{Branch penalty}}
\]

Key takeaway: deeper pipelines increase branch penalty (in cycles), so **branch prediction becomes mandatory** beyond modest depths.

---

## 3) C.3 — How pipelining is implemented (RISC‑V 5-stage example)

### 3.1 Unpipelined → pipelined: pipeline registers carry data + control
The appendix starts with an unpipelined RISC‑V subset where each instruction fits in ≤5 cycles, then pipelines it by inserting **pipeline registers**:
- IF/ID, ID/EX, EX/MEM, MEM/WB

These registers must carry:
- data values (register operands, ALU results, load data),
- instruction fields (e.g., `rs1`, `rs2`, `rd`),
- and control info (what muxes and writes should happen later).

### 3.2 Interlocks (stall insertion)
For the load-use case:
- detect hazard when **load is in EX** and consumer is in **ID**
- stall IF and ID; inject a “bubble” into ID/EX control so no state update occurs.

### 3.3 Forwarding logic (comparators + mux expansion)
Forwarding is implemented by comparing:
- destination register numbers in EX/MEM and MEM/WB
against
- source register numbers in ID/EX (and sometimes EX/MEM for stores/branches).

Then select forwarded data through enlarged muxes at ALU inputs (and possibly store-data inputs / compare inputs).

### 3.4 Branch target / condition placement trade-off
The appendix shows a more aggressive pipeline variant:
- compute target earlier (e.g., with an adder in ID),
- but condition evaluation still needs ALU resources.
As pipelines deepen (split fetch/decode), branch delay grows, pushing designs toward dynamic prediction.

---

## 4) C.4 — What makes pipelining hard: exceptions and “precise state”

### 4.1 What counts as an exception?
The appendix uses “exception” broadly (includes interrupts/faults), e.g.:
- I/O request, syscall, breakpoints
- arithmetic overflow / FP anomaly
- page fault, misaligned access, protection fault
- illegal instruction, hardware malfunction, power failure

### 4.2 Five axes that characterize exceptions
Exceptions differ in implementation difficulty along dimensions like:
- synchronous vs asynchronous,
- user-request vs coerced,
- whether they occur between vs within instructions,
- resume vs terminate, etc.

The hardest ones:
- occur **within** an instruction (EX/MEM time),
- and must be **restartable** (e.g., page faults under demand paging).

### 4.3 Precise exceptions (the key pipeline requirement)
A **precise exception** means the machine state appears as if:
- all earlier instructions completed,
- the faulting instruction did not complete,
- no later instructions changed state.

Pipelines complicate this because many instructions are in flight, and exceptions can be detected **out of order** (a later instruction’s IF fault may occur before an earlier instruction’s MEM fault). To keep state precise, hardware must prioritize the earliest fault in **program order**.

Some FP pipelines historically offered a “fast mode” with imprecise FP exceptions; precise mode can reduce overlap.

---

## 5) C.5 — Multicycle / floating-point operations in a pipelined machine

The appendix explains why multicycle ops are “thorny”:
- different ops take radically different cycles,
- and complex ISAs (x86 example) can have irregular memory behavior inside one instruction.

For FP in RISC‑V-style pipelines:
- EX may repeat multiple cycles depending on operation latency,
- multiple functional units may exist.

An example organization uses four units:
1) Integer unit (ALU, branches, address calc)
2) FP/integer multiplier
3) FP adder
4) FP/integer divider

The appendix uses the standard terms:
- **Latency**: cycles from issue to result availability
- **Initiation interval**: how often you can start a new op in that unit

(Example table shown includes values like FP add latency 3, initiation 1; FP multiply latency 6, initiation 1; divide has longer/variable latency.)

**Measured insight (SPEC89 FP):**
Stalls per instruction in the simple FP pipeline are dominated by **FP result stalls**, not by divide structural hazards, except for specific divide-heavy codes.

---

## 6) C.6 — Putting it together: the MIPS R4000 pipeline

### 6.1 R4000 8-stage integer pipeline
Stages:
- **IF** (first half of I$ access + PC select)
- **IS** (second half of I$ access)
- **RF** (decode, reg fetch, hazard checks, I$ hit detection)
- **EX** (ALU, address calc, branch target + condition eval)
- **DF** (first half of D$ access)
- **DS** (second half of D$ access; data available end of DS)
- **TC** (tag check: confirm hit)
- **WB** (write back)

Implications:
- **Load delay is 2 cycles** (data arrives end of DS).
- **Branch delay is 3 cycles** (condition computed in EX).
- Many more forwarding sources exist: EX/DF, DF/DS, DS/TC, TC/WB.
- After R4000, MIPS implementations adopted **dynamic branch prediction**.

### 6.2 R4000 FP pipeline overview
R4000 FP unit has three main functional units:
- FP divide
- FP multiply
- FP add  
(Adder logic also used in the final steps of mult/div.)

FP ops vary widely (the appendix notes double-precision can be as low as 2 cycles for negate up to 112 cycles for sqrt), and initiation rates differ, so structural conflicts depend heavily on operation mixes.

### 6.3 CPI breakdown (SPEC92, perfect cache assumption)
The appendix reports CPI contributions for the R4000 pipeline:

| Benchmark | Pipeline CPI | Load stalls | Branch stalls | FP result stalls | FP structural stalls |
| --- | ---:| ---:| ---:| ---:| ---:|
| compress | 1.20 | 0.14 | 0.06 | 0.00 | 0.00 |
| eqntott | 1.88 | 0.27 | 0.61 | 0.00 | 0.00 |
| espresso | 1.42 | 0.07 | 0.35 | 0.00 | 0.00 |
| gcc | 1.56 | 0.13 | 0.43 | 0.00 | 0.00 |
| li | 1.64 | 0.18 | 0.46 | 0.00 | 0.00 |
| **integer avg** | **1.54** | **0.16** | **0.38** | **0.00** | **0.00** |
| doduc | 2.84 | 0.01 | 0.22 | 1.39 | 0.22 |
| mdljdp2 | 2.66 | 0.01 | 0.31 | 1.20 | 0.15 |
| ear | 2.17 | 0.00 | 0.46 | 0.59 | 0.12 |
| hydro2d | 2.53 | 0.00 | 0.62 | 0.75 | 0.17 |
| su2cor | 2.18 | 0.02 | 0.07 | 0.84 | 0.26 |
| **FP avg** | **2.48** | **0.01** | **0.33** | **0.95** | **0.18** |
| **overall avg** | **2.00** | **0.10** | **0.36** | **0.46** | **0.09** |

Two blunt takeaways:
- Integer CPI is dominated by **branch stalls**.
- FP CPI is dominated by **FP result stalls** (data latency), more than pure structural hazards.

---

## 7) C.7 Cross-cutting issues: why RISC helps, and why scoreboarding appears

### 7.1 RISC ISAs make pipelines easier and easier to schedule
Even if a CISC ISA could do “add two memory operands” in one instruction, a RISC ISA breaks it into:
- load, load, add, store  
This creates more instruction-level scheduling opportunities (compiler or hardware), and avoids unpredictable multi-memory-access instructions in the core pipeline.

### 7.2 Scoreboarding (toward out-of-order execution)
To let later independent instructions proceed while an earlier one waits:
- split decode/issue into:
  1) **Issue**: check structural hazards + prevent WAW
  2) **Read operands**: wait for RAW to clear

A **scoreboard** tracks which functional units and registers are busy and controls issue/execution so that independent instructions can start as soon as operands are available—enabling out-of-order execution/completion (predecessor of Tomasulo/OoO ideas in Chapter 3).

---

## 8) C.8 Fallacies and pitfalls (the “don’t get fooled” list)

- **“Deeper pipeline always wins.”**  
  False: deeper pipelines increase branch penalties and forwarding complexity; overhead and imbalance can erase gains.

- **“Branch handling is a detail.”**  
  False: once pipelines are ~8+ stages, branch penalty dominates unless prediction is strong.

- **“Structural hazards are the main limiter.”**  
  Often false: real performance is usually limited by **data dependences** (load-use, FP result latency) and **control**.

- **“Precise exceptions are automatic.”**  
  False: they require careful control of when state is committed and how in-flight instructions are handled on faults.

---

## 9) Flashcards (quick recall)

**Q1. Ideal CPI of a scalar pipeline (no hazards)?**  
A. ~1 instruction per cycle (CPI ≈ 1).

**Q2. Three hazard types?**  
A. Structural, data, control.

**Q3. Why does load-use require a stall even with forwarding?**  
A. Load data arrives at end of MEM; consumer needs it at start of EX (too early).

**Q4. Pipeline speedup with branch stalls (ideal CPI=1)?**  
A. `Depth / (1 + branch_frequency × branch_penalty)`.

**Q5. What makes exceptions hard in pipelines?**  
A. Multiple in-flight instructions; exceptions can be detected out of order; need precise state + restartability.

**Q6. R4000 stage names?**  
A. IF, IS, RF, EX, DF, DS, TC, WB.

**Q7. R4000 load delay and branch delay (as described)?**  
A. Load delay ≈ 2 cycles; branch delay ≈ 3 cycles.

**Q8. What does a scoreboard buy you?**  
A. Allows later independent instructions to proceed while earlier ones wait, enabling out-of-order execution/completion under hazard control.

---

## 10) One-page carryover (low-context)

- Pipelining boosts throughput; limited by stage imbalance + register/clock overhead (example: 3.7× not 5×).  
- Hazards: structural (resource), data (RAW), control (branches).  
- Forwarding fixes many RAWs; load-use still needs an interlock stall.  
- Branch schemes: flush/freeze, predict NT, predict T, delayed branch; deeper pipelines → larger penalties → dynamic prediction becomes necessary.  
- Implementation: pipeline registers carry data+control; hazard detection inserts bubbles; forwarding compares rd vs rs fields.  
- Exceptions: need restartability + **precise** state; order can differ from detection order.  
- Multicycle FP ops: latency + initiation interval matter; stalls often dominated by result latency.  
- R4000: 8-stage pipeline; longer load/branch delays; CPI dominated by branches (int) and FP result stalls (FP).  
- Scoreboarding introduces out-of-order start while preserving correctness.

---

*End of CH10 / Appendix C summary.*
