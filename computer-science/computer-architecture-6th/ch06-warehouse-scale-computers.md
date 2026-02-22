# Chapter 6: Warehouse-Scale Computers to Exploit Request-Level and Data-Level Parallelism

**Source:** Hennessy & Patterson, *Computer Architecture: A Quantitative Approach*, 6th Edition  
**Chapter:** 6 (Pages 466–525)  
**Status:** draft  
**Confidence:** high

---

## 6.1 Introduction — What Is a Warehouse-Scale Computer?

A **Warehouse-Scale Computer (WSC)** is a single massive computational facility composed of 50,000–100,000 servers connected by a high-bandwidth internal network, running software infrastructure designed for scale. WSCs are the physical substrate of Internet services — search, social networking, video sharing, email, online shopping — serving billions of users daily. A single WSC costs hundreds of millions of dollars for the building, electrical/cooling infrastructure, servers, and networking.

### WSC vs. Traditional Data Center vs. HPC Cluster

| Dimension | WSC | Traditional Data Center | HPC Cluster |
|-----------|-----|------------------------|-------------|
| Hardware | Homogeneous, commodity | Heterogeneous, mixed vendors | High-end processors, low-latency interconnects |
| Operator | Single organization | Central IT for many departments | Research institution |
| Software | Custom-built (GFS, MapReduce, BigTable) | Third-party commercial | MPI, thread/data-parallel |
| Scale | 50,000–100,000 servers | Hundreds to low thousands | Hundreds to millions of processors |
| Parallelism | Request-level parallelism (RLP) | Consolidation, VMs | Thread-level / data-level parallelism |
| Utilization | 10–50% average | Low, varied | High, long-running jobs |
| Cost focus | Performance per dollar and per joule | Consolidation efficiency | Peak FLOPS |
| Failure handling | Software redundancy across servers | Hardware redundancy per server | Checkpoint-restart |

**Key architectural point:** WSCs share many goals with server architects — cost-performance, energy efficiency, dependability via redundancy, network I/O — but diverge on three critical characteristics:

1. **Ample parallelism** — Batch workloads have enormous data-level parallelism (billions of web pages). Interactive services have massive request-level parallelism (millions of independent users). Synchronization is rarely needed because reads/writes are typically independent.

2. **Operational costs matter as much as purchase price** — Unlike servers, WSCs have significant recurring electricity bills, cooling costs, and facility maintenance. Operational expenditures (OPEX) rival capital expenditures (CAPEX).

3. **Scale enables economy** — Purchasing 50,000 servers at a time yields massive volume discounts. But scale also means failures are constant: with MTTF of 25 years per server and 100,000 servers, expect ~5 server failures per day and ~1 disk failure per hour (at 4% annual disk failure rate).

### Failure Rates at WSC Scale (2400-Server Cluster, First Year)

| Event | Annual Frequency | Consequence |
|-------|-----------------|-------------|
| Power utility failures | 1–2 | Lose power to whole WSC; UPS + generators mask 99% |
| Cluster upgrades | 4 | Planned outage (9 planned per 1 unplanned) |
| Hard-drive failures | ~1000 | 2–10% annual disk failure rate |
| Slow disks | ~1000 | Operate at 10–20× reduced speed |
| Bad memories | ~1000 | One uncorrectable DRAM error per year per server |
| Misconfigured machines | ~1000 | 30% of service disruptions |
| Flaky machines | ~1000 | 1% of servers reboot more than once per week |
| Individual server crashes | ~5000 | Reboot takes ~5 min; software or hardware causes |

**Worked Example:** A service running on 2400 servers without software redundancy would have availability of only ~86% — down one day per week — far below the 99.99% WSC target. This demonstrates why **software-level fault tolerance is mandatory**, not optional, in WSC design.

$$\text{Availability} = \frac{8760 - 1192}{8760} = 86\%$$

where 1192 hours of outage come from hardware repairs (754 h) + software reboots (438 h).

---

## 6.2 Programming Models and Workloads

### MapReduce — The Canonical WSC Batch Processing Framework

MapReduce (Dean & Ghemawat, 2008) and its open-source counterpart Hadoop operate in two phases:

1. **Map:** A programmer-supplied function is applied independently to each logical input record. Runs on hundreds to thousands of servers. Produces intermediate (key, value) pairs.
2. **Reduce:** A combining function collects and collapses the intermediate outputs. If the Reduce function is commutative and associative, it can run in $O(\log N)$ time.

**Physical intuition:** MapReduce is a generalization of SIMD at datacenter scale — a function is passed to distributed data, followed by a reduction. The framework handles distribution, fault tolerance, and load balancing automatically.

**Google MapReduce Growth (2004–2016):**

| Month | Monthly Jobs | Avg Servers/Job | CPU Core-Years | Input Data (PB) |
|-------|-------------|-----------------|----------------|-----------------|
| Aug-04 | 29,000 | 157 | 217 | 3.2 |
| Sep-09 | 4,114,919 | 156 | 33,582 | 548 |
| Sep-12 | 15,662,118 | 142 | 60,987 | 2,171 |
| Sep-16 | 95,775,891 | 130 | 311,691 | 11,553 |

Over 12 years: 3300× growth in monthly jobs, 1450× growth in CPU core-years consumed.

**Tail Latency:** A single slow task can hold up completion of an entire MapReduce job. Dean & Barroso (2013) coined the term "tail latency" for this phenomenon. WSCs cope through backup executions: near job completion, start duplicate tasks on other nodes and use whichever finishes first. This increases resource usage by a few percent but reduces completion time by up to 30%.

**Dependability by design:** Each MapReduce node reports periodically to the master. If a node misses its deadline, it is assumed dead and its work is reassigned. This allows WSCs to deliver 99.99% availability despite frequent component failures.

### Supporting Infrastructure Software

- **Google File System (GFS) / Colossus** — Distributed file system providing files to any server. Uses cross-server data replication (3 copies) rather than within-server RAID for dependability.
- **BigTable** — Record storage system built on top of GFS/Colossus.
- **Amazon Dynamo** — Key-value storage system designed for 99.9th percentile latency targets.
- **Eventual consistency** — WSC storage relaxes ACID requirements. Multiple replicas need not agree at all times, only eventually. This makes storage systems much easier to scale, which is essential at WSC scale.

### Workload Characteristics

Server utilization in WSCs is typically 10–50%. Less than 0.5% of Google servers averaged 100% utilization over a 6-month measurement. Most servers operated between 10–50%. This has a profound design implication: **servers must perform well at low utilization, not just at peak**.

**SPECpower impact:** When the standard equal-weighting (each utilization level equally likely) is replaced with actual Google utilization frequencies, the SPECpower summary metric drops by 30% (3210 → 2454 ssj_ops/watt). The standard benchmark overstates real-world energy efficiency because it overweights high-utilization scenarios that rarely occur.

---

## 6.3 Computer Architecture of WSCs

### Network Hierarchy

WSCs use a hierarchical network analogous to the memory hierarchy:

1. **Top of Rack (ToR) switch** — Connects 40–80 servers within a rack. Highest bandwidth, lowest latency.
2. **Array switch** — Connects racks within an array (~30 racks). 10× bisection bandwidth of ToR switch but ~100× the cost. Cost scales as $O(n^2)$ for $n$ ports.
3. **Layer 3 routers** — Connect arrays to each other and to the Internet.

**Oversubscription:** ToR switches typically have 4–16 uplinks to the array switch, making the bandwidth leaving a rack 6–24× smaller than bandwidth within a rack. This oversubscription forces programmers to be aware of data placement — a key motivation for developing custom WSC switches.

### WSC Memory Hierarchy — Latency, Bandwidth, Capacity

| Level | DRAM Latency (μs) | Flash Latency (μs) | Disk Latency (μs) | DRAM BW (MB/s) | DRAM Capacity (GB) |
|-------|-------------------|--------------------|--------------------|----------------|---------------------|
| Local (1 server) | 0.1 | 100 | 10,000 | 20,000 | 16 |
| Rack (80 servers) | 300 | 400 | 11,000 | 100 | 1,024 |
| Array (30 racks) | 500 | 600 | 12,000 | 10 | 31,200 |

**Critical insight:** Network overhead dramatically increases latency for DRAM and Flash across servers but barely affects disk latency (already high). The network also collapses bandwidth differences: rack DRAM, rack Flash, and rack disk all have ~100 MB/s bandwidth; array-level storage all converges to ~10 MB/s.

**Worked Example — Average Memory Latency:**
With 90% local, 9% rack, 1% array accesses:

$$\bar{t} = 0.90 \times 0.1 + 0.09 \times 100 + 0.01 \times 300 = 0.09 + 9.0 + 3.0 = 12.09 \,\mu\text{s}$$

This is a **120× slowdown** versus 100% local accesses. Locality within a single server is vital.

**Worked Example — Block Transfer (1000 MB):**
For disk transfers: within server = 5 s, within rack = 10 s, within array = 100 s.  
For DRAM-to-DRAM: within server = 0.05 s, within rack = 10 s, within array = 100 s.  
**Conclusion:** For transfers outside a single server, it does not matter whether data is in memory or on disk — the network switch is the bottleneck.

### Storage Architecture

Early WSCs relied on local disks per server with GFS managing replication. Modern WSCs have more varied storage: some racks balanced (servers + disks), some without local disks, some disk-heavy racks. System software uses RAID-like error correction codes to reduce storage cost of redundancy.

**Sharding/Partitioning:** Applications exceeding a single array's capacity split datasets into independent pieces distributed across arrays. Operations are sent to servers hosting each piece, and results are coalesced by the client.

---

## 6.4 Efficiency and Cost of WSCs

### Power Usage Effectiveness (PUE)

$$\text{PUE} = \frac{\text{Total facility power}}{\text{IT equipment power}}$$

- **PUE ≥ 1.0** (ideal = 1.0, all power goes to computation)
- 2006 survey of 19 data centers: median PUE = 1.69 (cooling overhead = 0.55 of IT power)
- Google average PUE (2017): 1.11–1.12, down from ~1.22 in 2008
- Industry improvement driven by attention to PUE as a metric over the past decade

**Power breakdown inside IT equipment (Google WSC, 2012):**

| Component | % of Power |
|-----------|-----------|
| Processors | 42% |
| DRAM | 12% |
| Disks | 14% |
| Networking | 5% |
| Cooling overhead | 15% |
| Power overhead | 8% |
| Miscellaneous | 4% |

### The Economics of Latency

User satisfaction and revenue are directly tied to response time. Bing search experiments showed:

| Server Delay | Time to Next Click Impact | Revenue Impact |
|-------------|--------------------------|----------------|
| 200 ms | +500 ms | — |
| 500 ms | +1200 ms | −1.2% |
| 1000 ms | +1900 ms | −2.8% |
| 2000 ms | +3100 ms | −4.3% |

Google found these effects persisted 5 weeks after a 4-week experiment ended: 0.1% fewer searchers per day for users who experienced 200 ms delays, 0.2% fewer for 400 ms delays. Results were so negative the experiment was terminated early.

**Service Level Objectives (SLOs):** Performance goals specify a high percentile threshold rather than average. Example: 99% of requests must be below 100 ms. Amazon's Dynamo targets 99.9th percentile latency.

**Tail-tolerant systems** (Dean & Barroso, 2013): Rather than preventing variability, design systems to mask temporary latency spikes through techniques like fine-grained load balancing and hedged/tied requests.

### Total Cost of Ownership (TCO) — Hamilton's Case Study

**Capital Expenditures (CAPEX) for an 8-MW WSC:**

| Component | Cost |
|-----------|------|
| Facility (building, power, cooling) | $88,000,000 |
| Servers (45,978 × $1,450) | $66,700,000 |
| Networking equipment | $12,810,000 |
| **Total CAPEX** | **$167,510,000** |

**Amortization periods:** Facility = 10 years, Networking = 4 years, Servers = 3 years.

**Monthly Operational Expenditures (OPEX):**

| Component | Monthly Cost | % of Total |
|-----------|-------------|-----------|
| Amortized servers | $2,005,000 | 57% |
| Amortized networking | $297,000 | 8% |
| Amortized power + cooling infrastructure | $610,000 | 17% |
| Amortized other infrastructure | $134,000 | 4% |
| Electricity (at $0.07/kWh) | $415,000 | 12% |
| People (security + facilities) | $55,000 | 2% |
| **Total monthly OPEX** | **$3,516,000** | **100%** |

**Per-server cost:** $3,516,000 / (45,978 servers × 730 hours/month) ≈ **$0.105 per server per hour**.

**Sensitivity analysis:** The facility infrastructure cost per watt ranges from $9–$13/watt (Barroso et al., 2013). A 16-MW facility costs $144M–$208M before IT equipment. Over a decade, server costs (3.3 × $67M = $221M) exceed facility costs ($72M) by 3×, because servers are replaced every 3 years while the facility lasts 10+ years.

---

## 6.5 Cloud Computing — The Return of Utility Computing

### Economies of Scale: WSC vs. Small Data Center

Hamilton (2010) reported these cost advantages for a WSC over a 1000-server data center:

| Dimension | Cost Reduction Factor |
|-----------|---------------------|
| Storage costs | 5.7× ($4.6/GB/yr vs $26/GB/yr) |
| Administrative costs | 7.1× (1000+ servers/admin vs 140) |
| Networking costs | 7.3× ($13/Mbit/s/mo vs $95) |
| PUE improvement | ~1.5–2× (1.1–1.2 vs 2.0) |
| Server utilization | ~2–5× (statistical multiplexing raises to >50%) |

These economies of scale motivated large Internet companies to offer computing as a utility — cloud computing.

### Amazon Web Services (AWS) — Design Decisions

AWS launched with Amazon S3 and EC2 in 2006, making six key decisions:

1. **Virtual machines (Xen)** — Isolation between users, simplified software distribution, resource slicing for multiple price points, hardware identity hidden from customers.
2. **Very low cost** — $0.10/hour per instance at launch (2 instances per core, matching a 1.0–1.2 GHz 2006 Opteron/Xeon).
3. **Open source reliance** — No licensing fees (Linux, open-source databases).
4. **No initial SLO guarantee** — Best effort only; SLOs added later (99.95% for EC2, S3).
5. **No contract** — Credit card only required to start.
6. **Pay-as-you-go** — No upfront commitment; Spot Instances for flexible pricing (up to 75% discount).

**EC2 Instance Range (2017):** Over 50 instance types spanning general-purpose, compute-optimized, GPU, FPGA, memory-optimized, and storage-optimized. Fastest instance is 100× faster than slowest; largest has 2000× more memory than smallest. Cheapest instance: $50/year.

### Serverless Computing (AWS Lambda)

The next evolutionary step: no explicit server provisioning. Programs are event-driven functions ("Lambda functions") that scale automatically. Billing per 100 ms of execution (six orders of magnitude finer than EC2's per-hour billing). Zero cost when idle. At 1 GiB memory, cost is ~$0.000001667/100ms (~$6/hr during execution).

**Conceptual model:** A set of processes running in parallel across the entire WSC, sharing data through disaggregated storage (S3).

### Cost Associativity

$$1000 \text{ servers} \times 1 \text{ hour} = 1 \text{ server} \times 1000 \text{ hours (same cost)}$$

This property, combined with the illusion of infinite scalability, eliminates the risk of over-provisioning (wasted capital) and under-provisioning (lost customers). The FarmVille case study exemplifies this: grew from 0 to 28 million daily users in 270 days on AWS without infrastructure planning.

### Scale of AWS (2017)

- 16 regions worldwide, 42 availability zones (2–3 per region, 1–2 km apart)
- Each availability zone has 1+ WSCs; largest regions have 10+ WSCs
- Each WSC: at least 50,000 servers, some over 80,000
- Estimated total: 3–8.4 million servers across 84–126 WSCs
- Daily server capacity added equivalent to all of Amazon.com in 2004 ($7B revenue company)
- Hamilton (2017) estimates largest cloud providers will eventually need O(10⁵) WSCs — 1000× today's count

### Security Reversal

By 2017, the security argument has flipped. WSCs under constant attack build better defenses. Ransomware is unheard of inside WSCs but routine in enterprise data centers. Many CIOs now believe critical data is safer in the cloud than "on prem."

---

## 6.6 Cross-Cutting Issues

### Preventing the Network from Being a Bottleneck

Google's internal WSC network traffic grew 50× in 7 years (2008–2015), doubling every 12–15 months. Without custom networking, the WSC network becomes a performance and cost bottleneck.

**The solution:** Build custom switches from commodity switch chips with centralized control (SDN-like approach). Google eliminated unnecessary features of traditional datacenter switches (decentralized routing, support for arbitrary deployment scenarios) because WSC topology is planned in advance and has a single operator.

**Six Generations of Google WSC Switches:**

| Generation | Year | Host Speed | Fabric Speed | Bisection BW |
|-----------|------|------------|-------------|-------------|
| Four-Post CRs | 2004 | 1 Gbps | 10 Gbps | 2 Tbps |
| Firehose 1.0 | 2005 | 1 Gbps | 10 Gbps | 10 Tbps |
| Firehose 1.1 | 2006 | 1 Gbps | 10 Gbps | 10 Tbps |
| Watchtower | 2008 | n×1 Gbps | 10 Gbps | 82 Tbps |
| Saturn | 2009 | n×10 Gbps | 10 Gbps | 207 Tbps |
| Jupiter | 2012 | n×10/40 Gbps | 10/40 Gbps | 1,300 Tbps |

Result: 100× bandwidth scaling in a decade, reaching >1 Pbit/s bisection bandwidth (exceeding the entire Internet's estimated 0.2 Pbit/s bisection bandwidth).

### Energy Efficiency Inside the Server

In 2007, many server power supplies were only 60–80% efficient. Google deployed custom 94%+ efficient power supplies, recovering the 20+ percentage points of loss. The industry followed with the 80 Plus certification standard. By 2017, high-efficiency power supplies are standard.

---

## 6.7 Putting It All Together: A Google WSC

### Power Distribution Hierarchy

| Stage | Voltage | Failure Unit |
|-------|---------|-------------|
| Utility tower | >110,000 V | Whole site |
| On-site substation | 10,000–35,000 V | Multiple WSCs |
| Near-building transformer | 400–480 V | Single WSC |
| Copper bus ducts (in-row) | 400 V (3-phase) | Row of racks |
| Rack-top power converter | 240 V AC → 48 V DC | Single rack |
| Server board | 48 V DC → chip voltages | Single server |

Diesel generators provide backup power (takes tens of seconds to spin up). Rather than centralized UPS batteries (expensive, paid upfront), Google distributes small batteries to the bottom of each rack — incurred incrementally as racks are deployed, operating on the DC side (more efficient), and achieving 99.99% efficiency vs. 94% for traditional lead-acid UPS.

### Cooling Architecture

**Design philosophy:** Separate heat generation (racks) from heat rejection (cooling plant) with shared cooling across multiple rows.

1. **Hot aisle / cold aisle** — Servers oriented in opposite directions in alternating rows. Hot exhaust rises through ducts into ceiling. Cold air delivered through floor/wall plenums.
2. **Fan-coil units** at row ends — Hot air from racks delivered via horizontal plenum to fan-coils above cold aisle. Two rows share one pair of cooling coils, allowing shared cooling capacity to accommodate power variability between racks.
3. **Evaporative cooling towers** — Warm water sprayed inside towers, cooled by evaporation (water-side economization). Wet-bulb temperature determines effectiveness. An 8-MW facility uses 70,000–200,000 gallons of water/day.
4. **Mechanical chillers** — Backup for warm weather when evaporative cooling is insufficient.
5. **Google runs equipment at 80+°F (27+°C)** — Much warmer than traditional data centers, reducing cooling energy. Uses Computational Fluid Dynamics simulation for airflow design.

**Fan hierarchy:** Small server fans (MTBF 150,000 h, weakest component) work synergistically with large room fans. Room fans controlled by pressure differential between hot and cold aisles.

### Networking: Jupiter Clos Network

The Jupiter switch uses a **Clos network topology** (Clos, 1953) — a multistage network using low-radix commodity switch chips that provides fault tolerance and scalable bisection bandwidth by adding stages.

**Building blocks (commodity chip: 16×16 crossbar, 40 Gbps links):**

| Component | Configuration | Connectivity |
|-----------|--------------|-------------|
| ToR switch | 4 switch chips | 48×40G to servers, 16×40G uplinks (3:1 oversubscription) |
| Middle block | 16 switch chips | 256×10G down (ToR), 64×40G up (spine) |
| Aggregation block | 8 middle blocks | 512×40G to spine blocks |
| Spine block | 24 switch chips | 128×40G ports to aggregation blocks |
| Full fabric | 64 agg blocks + spine | **1.3 Pbit/s bisection bandwidth** |

Centralized routing control: every switch receives a consistent copy of the current network topology. Simplifies the complex routing of Clos networks. Custom design uses standard commodity switch chips with centralized control, eliminating expensive commercial datacenter switch features.

### Server Hardware (Google, ~2015)

- 2-socket Intel Haswell, 18 cores/socket, 2.3 GHz
- 256 GB DDR3-1600 DRAM (16 DIMMs)
- L1: 32 KiB I + 32 KiB D per core; L2: 256 KiB/core; L3: 2.5 MiB/core (45 MiB total)
- Local memory bandwidth: 44 GB/s, latency 70 ns
- Intersocket bandwidth: 31 GB/s, latency 140 ns
- 10 Gbit/s NIC (40 Gbit/s available)
- Custom disk controller for 12 hard drives per server tray

**Workload insight (Kanev et al., 2015):** L3 cache is barely needed for SPEC benchmarks but is useful for real WSC workloads — highlighting the gap between benchmark and production characteristics.

---

## 6.8 Fallacies and Pitfalls

### Fallacy: Facility costs dominate server costs for a WSC

Although the one-time facility CAPEX (~$88M) exceeds one-time server CAPEX (~$67M), the facility lasts 10–15 years while servers are replaced every 3–4 years. Over a decade: facility amortization = $72M; server amortization = 3.3 × $67M = $221M. **Server costs are 3× facility costs over the WSC lifetime.**

### Pitfall: Inactive low-power modes vs. active low-power modes

Since servers average 10–50% utilization (never truly idle), inactive modes (requiring full reactivation to access DRAM/disk) are impractical. Active low-power modes (DVFS, clock gating) work at the normal access rate at reduced power and transition in microseconds. They are also compatible with WSC monitoring infrastructure.

### Fallacy: ECC memory is unnecessary given software fault tolerance

Schroeder et al. (2009) measured Google's WSCs and found DRAM failure rates 15–25× higher than published. Over 8% of DIMMs were affected, with an average of 4000 correctable errors and 0.2 uncorrectable errors per DIMM per year. One-third of servers experienced DRAM errors annually. Without Chipkill ECC, uncorrectable error rates would be 4–10× higher. Without ECC at all, one-third of servers would spend ~20% of their time rebooting from parity errors, reducing WSC performance by ~6%.

**Historical anecdote:** In 2000, Google used non-ECC DRAM. During index testing, search started returning random documents due to a stuck-at-zero DRAM fault corrupting the index.

### Pitfall: Microsecond-scale latency gap

Modern systems handle nanosecond events (cache/DRAM via hardware coherence) and millisecond events (disk I/O via OS process switching) well, but lack good mechanisms for microsecond-scale events (Flash access, 100 Gbit/s network). New mechanisms are needed for this "microsecond gap."

### Fallacy: Turning off hardware during low activity improves TCO

The amortized power/cooling infrastructure cost is 50% higher than the entire monthly electricity bill. Even halving power usage would reduce monthly costs by only ~7%. Better approach: run valuable batch work (MapReduce, index building) during low-activity periods to recoup infrastructure investment. AWS Spot Instances serve the same purpose — up to 4× savings for flexible jobs.

---

## Key Equations and Metrics

### Power Usage Effectiveness
$$\text{PUE} = \frac{P_{\text{total facility}}}{P_{\text{IT equipment}}} \geq 1.0$$

- Google (2017): PUE ≈ 1.12
- Industry median (2006): PUE ≈ 1.69
- Lower is better; 1.0 is ideal

### Availability
$$\text{Availability} = \frac{\text{MTTF}}{\text{MTTF} + \text{MTTR}}$$

WSC target: ≥ 99.99% ("four nines") = < 1 hour downtime per year.

### Cost Per Server Hour
$$\text{Cost/server/hour} = \frac{\text{Monthly OPEX}}{\text{Servers} \times \text{Hours/month}}$$

Hamilton case study: ≈ $0.105/server/hour at $0.07/kWh electricity.

### Average Memory Access Time (WSC)
$$\bar{t} = f_{\text{local}} \times t_{\text{local}} + f_{\text{rack}} \times t_{\text{rack}} + f_{\text{array}} \times t_{\text{array}}$$

With 90/9/1% distribution: 12.09 μs (120× slowdown vs. all-local).

---

## Cross-References

- [[ch01-fundamentals]] — Amdahl's Law, dependability metrics, power/energy fundamentals
- [[ch02-memory-hierarchy-design]] — Cache hierarchy principles applied at WSC scale
- [[ch04-data-level-parallelism]] — SIMD/GPU parallelism; MapReduce as datacenter-scale SIMD
- [[ch05-thread-level-parallelism]] — From chip-level to facility-level parallelism
- [[ch07-domain-specific-architectures]] — TPUs deployed in WSCs; domain-specific processors as the path forward
- [[appendix-d-storage-systems]] — RAID, disk reliability fundamentals
- [[appendix-f-interconnection-networks]] — Clos network topology details

---

## Summary of Key Design Principles

1. **Software redundancy over hardware reliability** — Cheap commodity servers + software fault tolerance (replication, checkpoint-restart, automatic failover) is more cost-effective than gold-plated hardware. Factor of 20× price-performance advantage.

2. **Energy proportionality** — Servers should consume power proportional to load. At 10% utilization, ideal is 10% of peak power; reality is ~50%. Active low-power modes (DVFS) are practical; inactive modes are not.

3. **Tail latency matters more than average** — Design for 99th or 99.9th percentile latency, not average. Tail-tolerant techniques (hedged requests, fine-grained load balancing) mask variability.

4. **Network is the critical bottleneck** — Custom Clos-network switches from commodity chips with centralized SDN-like control. Google scaled WSC bisection bandwidth 100× in a decade to 1.3 Pbit/s.

5. **Economies of scale justify cloud computing** — 5–7× cost reductions across storage, administration, and networking. Cost associativity (1000 servers × 1 hour = 1 server × 1000 hours) eliminates provisioning risk.

6. **Operational costs compound** — Servers replaced every 3 years accumulate 3× the facility cost over a decade. Electricity is recurring. TCO analysis must span the full facility lifetime.
