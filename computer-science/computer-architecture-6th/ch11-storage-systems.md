# CH11 — Storage Systems (Appendix D) (Summary)

> Source PDF: `ch11-appendix-d-storage-systems.pdf`  
> Note: In this PDF set, “Chapter 11” corresponds to **Appendix D: Storage Systems**.

---

## 0) What this appendix is really teaching you

Storage is “slow” in latency but enormous in capacity and revenue impact; at scale, storage design is mainly about:
- **dependability** (don’t lose data),
- **cost-performance** (IOPS/$, MB/s/$),
- and **tail behavior** under load (response time vs throughput trade-off).

The appendix builds a full mental model: device physics → arrays/RAID → real failure behavior → I/O performance metrics/benchmarks → queuing theory → full system case studies (Internet Archive cluster, NetApp filer) → pitfalls.

---

## D.1 Introduction: why storage matters

The appendix frames the modern shift:
- The Information Age is about **communication + storage**, not just compute.
- Users tolerate crashes far more than **data loss**, so storage is held to stricter dependability standards.

A key technological fact: there’s an enormous **access-time gap** between DRAM and disk (orders of magnitude). This gap has persisted despite repeated attempts to “fill” it. 【ch11-appendix-d-storage-systems.pdf†L??】 *(Gap discussed explicitly in D.1 / Figure D.1.)*

---

## D.2 Advanced topics in disk storage

### 1) Disk geometry model changed (sector–track–cylinder assumptions broke)
The old cylinder/track model became less accurate because disks:
- added internal microcontrollers and higher-level interfaces (ATA/SCSI),
- reorder logical blocks for better sequential performance (serpentine ordering),
- reduced platter count (so “cylinder locality” matters less).

### 2) Disk power is nontrivial
A representative 2011 ATA disk power draw:
- ~9 W idle, ~11 W read/write, ~13 W seek.

Disk motor power scaling formula (Gurumurthi et al. 2005):
\[
Power \propto Diameter^{4.6}\cdot RPM^{2.8}\cdot \#platters
\]
So: smaller diameter, lower RPM, fewer platters → lower motor power. (Most disk power is in the motor.)

---

## D.2 Disk arrays (RAID) — performance + dependability together

**Why arrays?**
- More disks → more arms → higher potential throughput.
- Striping spreads data across disks to exploit parallel access.

But: more devices → lower raw reliability (more components that can fail).  
So arrays add **redundancy** to tolerate failures, relying on MTTF vs MTTR:
- If MTTF is years and MTTR is hours, redundancy can yield very high effective reliability.

### Classic RAID levels (as described)
- **RAID 3**: data striped + dedicated parity disk; good for large sequential reads/writes.
- **RAID 4**: independent reads; parity on a dedicated disk; small writes need read-modify-write (4 disk ops).
- **RAID 5**: parity distributed across disks to remove RAID 4’s parity-disk bottleneck; supports large reads/writes and higher small-write bandwidth than RAID 4 (but controller is more complex).

### Double-failure protection: NetApp RAID-DP (row-diagonal parity)
Motivation: larger arrays + slower/larger ATA disks increase vulnerability to a second failure during rebuild.  
RAID-DP adds **two parity blocks per stripe** (row parity + diagonal parity) to tolerate two disk failures. Recovery iteratively reconstructs missing blocks using the parity constraints.

Related: IBM’s EVEN-ODD family and extensions for 3-failure protection.

---

## D.3 Real faults and failures (definitions + reality check)

### Fault → Error → Failure (the standard chain)
The appendix clarifies dependability terminology:

- **Fault**: the underlying defect/cause (bug, alpha particle, operator mistake).
- **Error**: the system’s incorrect internal state due to a fault (often latent until activated).
- **Failure**: the externally visible incorrect service caused by an effective error.

Key concept: **error latency** = time between error creation and when it causes a failure.

### Case study: Berkeley “Tertiary Disk” (2000)
A 20-PC cluster with **368 disks** (7 racks) serving an art image database (70,000 artworks).
Takeaway: “obvious” reliability assumptions can be wrong.
- With proper vibration/cooling, SCSI data disks were not the least reliable.
- Some passive components (backplanes/cables/Ethernet cables) failed at rates comparable to disks.
- Many failures first appeared as **transient** faults; operators had to decide when to “fire” components.

### Industry + gov studies: humans dominate over time
The appendix contrasts:
- early eras where hardware/OS dominated faults,
- later eras where **operator faults** become a dominant category in managed systems.
Also cites FCC outage-report-based studies that avoid self-reporting bias.

---

## D.4 I/O performance + reliability measures + benchmarks

### 1) Throughput vs response time is a trade-off
Producer–server model:
- **Throughput** increases as you keep the server busy (high utilization).
- **Response time** includes queueing delay, so it rises with load.

A key empirical curve (disk arrays): minimum latency occurs at low throughput; pushing to 100% throughput can increase response time by **multiple ×** (Figure D.9).

### 2) Transaction processing benchmarks (TPC)
TPC-C (OLTP) highlights:
- I/O rate (IOPS) is central; measured in **tpmC**.
- Includes price (hardware + software + maintenance), enabling price-performance.
- Dataset scales with throughput (trying to match “real systems”).
- Requires ability to tolerate a disk failure in practice → implies RAID.

### 3) SPEC system-level storage benchmarks
- **SPEC SFS**: NFS file server benchmark (mix of reads/writes/file ops).
- **SPECMail**: SMTP/POP3 mail server throughput + response time across huge user counts.
- **SPECWeb**: web server sessions under different workloads (banking/e-commerce/support).

### 4) “Availability benchmarking” (fault injection)
The appendix mentions studies injecting faults into software RAID systems and observing behavior:
- Linux tends to be “paranoid” (drops disks quickly on first error),
- Solaris/Windows more forgiving to transients.
Also highlights that some systems do not rebuild automatically without human intervention, increasing “window of vulnerability” for second failure.

---

## D.5 A little queuing theory (the part you must be able to use)

### 1) Little’s Law (always true in equilibrium)
\[
\textbf{Mean tasks in system} = (\text{Arrival rate})\cdot(\text{Mean response time})
\]
Applies to any stable system (no net task creation/destruction inside the box).
Common pitfall: mixing time units.

### 2) Core definitions
- \(Time_{server}\): mean service time
- \(Time_{queue}\): mean waiting time
- \(Time_{system} = Time_{queue} + Time_{server}\)
- Arrival rate \(\lambda\): tasks/sec
- Utilization \(\rho = \lambda \cdot Time_{server}\) (must be < 1 for stability)

### 3) M/M/1 key result (exponential arrivals + service)
For exponential service time distribution (variance equals mean²), the appendix derives:

\[
Time_{queue} = Time_{server}\cdot\frac{\rho}{1-\rho}
\]

This is the “queue explodes near 1” law: when utilization approaches 1, response time skyrockets.

Worked example in the appendix:
- 40 IOPS, 20 ms service time → \(\rho=0.8\)
- \(Time_{queue} = 20ms \cdot 0.8/(0.2)=80ms\)
- \(Time_{system}=100ms\)

### 4) M/M/m (multiple servers) intuition
Utilization drops roughly by number of servers, but calculating “probability of queueing” becomes more complex.
Key takeaway: adding servers can drastically reduce queueing delay when you’re near saturation.

---

## D.6 Cross-cutting issues: interconnects + storage “personality”

### 1) Point-to-point links replacing buses
As bandwidth demands rise and components get cheaper, bus-based I/O standards are replaced by point-to-point links + switches (higher bandwidth, fewer wires, scalable).

### 2) Block servers vs filers
- **Block storage** exports blocks (like a disk) and leaves file semantics to the server OS.
- **Filers** export files (NFS/CIFS), holding metadata and often caching/consistency responsibilities.

Important virtualization terms:
- Logical unit (LUN): “virtual disk” exported by array
- Physical volume: device file used by filesystem to access a LUN
- Logical volume: OS-level virtualization across physical volumes / striping

### 3) Asynchronous I/O
Allows multiple outstanding I/Os, increasing bandwidth by overlap—analogous to nonblocking caches and OoO behavior in CPUs.

---

## D.7 Case study: Internet Archive “TB-80” storage rack

The appendix walks through a full system evaluation method:
1) pick workloads + request sizes
2) compute per-link bottlenecks
3) estimate IOPS/MBps limits
4) evaluate cost/performance + MTTF

Example assumptions shown:
- A rack node uses a VIA processor, modest DRAM, four 7200 RPM PATA disks.
- Compute disk I/O time as seek + rotational delay + transfer time.
- Compare disk bottleneck vs controller vs network.

Key takeaway: the weakest link determines rack throughput; disks dominate for random I/O.

It then estimates **MTTF of a rack** using component MTTFs and independence assumptions, pointing out that low-cost designs may have no redundancy within the rack and instead depend on application-level replication across sites.

---

## D.8 Case study: NetApp FAS6000 filer

NetApp filers provide:
- file services (NFS/CIFS),
- RAID-DP (row-diagonal parity),
- optional block protocols (Fibre Channel, iSCSI).

Hardware snapshot (as described):
- based on AMD Opteron multiprocessors + HyperTransport links
- distributed DRAM per socket (NUMA-style)
- ECC (SEC/DED) DRAM

High-level lesson: commercial storage systems are full-stack designs: CPU + DRAM + interconnect + filesystem + RAID + networking.

---

## D.9 Fallacies & pitfalls (very exam-friendly)

1) **Fallacy: “components fail fast”**  
Reality: components may behave strangely for a long time; “failure” is often an operational decision (Tertiary Disk case). 【p. D-43 region】

2) **Fallacy: “five nines availability” is typical**  
Marketing “99.999%” often excludes dominant outage causes (operator/app/environment) and scheduled downtime.  
The appendix notes well-managed servers are typically **~99%–99.9%** availability, not five nines, in practice. 【p. D-44 region】

3) **Pitfall: where you implement a function affects reliability**  
Example: software RAID can be theoretically fine, but practically hard to keep reliable due to software complexity, patch levels, interactions.

4) **Pitfall: OS request reordering is always beneficial**  
Not necessarily; disk internal scheduling knows real geometry and can outperform naïve host LBA-order scheduling (Figure D.22 example).

5) **Fallacy: average seek equals seek of 1/3 cylinders (linear assumption)**  
Seek time is not linear in distance; acceleration/deceleration + settle time dominate.  
Workloads often have many distance-0 seeks (same cylinder), making the “1/3 rule” misleading (Figure D.24). 【pp. D-45–D-47 region】

---

## D.10 Concluding remarks (what to remember)

- Storage is “king” economically and practically.
- Key challenges are **reliability + maintainability**, not just raw performance.
- Response time matters to humans and systems; pushing utilization to 100% can destroy latency.
- Queuing theory provides strong intuition: avoid operating too close to saturation unless you accept tail latency.

---

## Flashcards (quick recall)

**Q1. Disk motor power scales with what?**  
A. Approximately \(Diameter^{4.6}\cdot RPM^{2.8}\cdot \#platters\).

**Q2. RAID 5 vs RAID 4 (small writes)?**  
A. RAID 5 distributes parity to remove the dedicated parity-disk bottleneck.

**Q3. Fault vs error vs failure?**  
A. Fault causes (latent) error; when error becomes effective and affects service → failure.

**Q4. Little’s Law?**  
A. \(L = \lambda W\) (tasks in system = arrival rate × response time).

**Q5. Utilization definition?**  
A. \(\rho = \lambda \cdot Time_{server}\), must be < 1 for stability.

**Q6. M/M/1 mean waiting time?**  
A. \(Time_{queue}=Time_{server}\cdot \rho/(1-\rho)\).

**Q7. Why does latency rise sharply near 100% throughput?**  
A. Queueing delay explodes as utilization approaches 1 (classic queuing behavior).

**Q8. Why “five nines” is misleading?**  
A. Excludes dominant outages (operator/app/environment) and scheduled downtime.

---

*End of CH11 / Appendix D summary.*
