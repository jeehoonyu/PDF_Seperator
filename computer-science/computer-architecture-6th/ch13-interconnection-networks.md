# CH13 — Interconnection Networks (Appendix F) (Summary)

> Source PDF: `ch13-appendix-f-interconnection-networks.pdf`  
> Note: In this PDF set, “Chapter 13” corresponds to **Appendix F: Interconnection Networks**.

---

## 0) What this appendix is really teaching you

Interconnection networks are the “nervous system” of modern computing: they connect **cores ↔ caches ↔ memory**, **servers ↔ storage**, and **machines ↔ the Internet**.

This appendix gives you a reusable engineering framework:

1) **Define the domain** (on-chip vs SAN vs LAN vs WAN) because the “right” design choices differ.
2) Model performance with a small set of terms (**latency** and **effective bandwidth**) and learn what dominates where.
3) Understand how design choices (topology, routing, arbitration, switching, buffering, flow control) interact with *contention*, *deadlock*, and *fault tolerance*.
4) See real systems (NoCs, Blue Gene, InfiniBand, Ethernet, ATM, TCP/IP) and learn the practical trade-offs.

---

## 1) F.1 — Domains: where networks live

The appendix groups networks into four major domains:

1) **On-chip networks (OCNs / NoCs)**  
   Interconnect functional units, caches, tiles, cores, IP blocks within a chip/module.  
   Scale: tens–hundreds of endpoints, centimeters.

2) **System/storage area networks (SANs)**  
   Interconnect processors/memory/storage inside servers, clusters, and data centers (tens to thousands of nodes).  
   Example: **InfiniBand** supports up to **120 Gbps** over ~300 m (as described).

3) **Local area networks (LANs)**  
   Connect autonomous systems within buildings/campuses.

4) **Wide area networks (WANs)**  
   Connect systems across cities/countries/continents (Internet-scale).

**Key recurring point:** Short-distance networks (OCN, many SANs) can be **lossless** (flow control); long-distance networks (LAN/WAN) often tolerate **loss** (drop + retransmit) because flow-control feedback delay is large.

---

## 2) F.2 — Interconnecting two devices: the “end-node contract”

### 2.1 Messages, packets, headers/trailers
- Applications send **messages**.
- Networks often cap transfer size via an **MTU**. Larger messages are split into **packets** (datagrams) and reassembled at the receiver.
- Packets include:
  - **payload**
  - **control bits** in **header/trailer** (type, destination, etc.)
  - often a **checksum** for error detection.

### 2.2 What the network interface (NI / channel adapter) does
End nodes (NI + DMA + software) handle:
- message composition/segmentation
- checksum generation/verification
- acknowledgments + timeouts + retransmission (if required)
- per-process protection (e.g., port numbers so the right process receives data)

### 2.3 Flow control (lossless vs lossy)
Two popular lossless flow-control styles:

- **Xon/Xoff (Stop & Go)**: receiver tells sender to stop/start.
  - Needs enough buffering to avoid overflow before “stop” arrives.

- **Credit-based flow control**: sender can transmit only if it has credits.
  - Prevents overflow by construction (sender runs out of credits).

**Lossless vs lossy:**
- **Lossless** networks (with flow control) avoid dropping packets, improving efficiency and simplifying certain designs.
- **Lossy** networks drop packets under congestion and rely on higher layers to recover.

### 2.4 Latency model (the core equation you reuse)
For a single packet:

\[
\textbf{Latency} = \text{Sending overhead} + \text{Time of flight} + \frac{\text{Packet size}}{\text{Bandwidth}} + \text{Receiving overhead}
\]

Key definitions used:
- **Bandwidth**: maximum transfer rate including header+payload+trailer.
- **Time of flight**: propagation + device delays until the first bit arrives.
- **Transmission time**: time from first-bit arrival to last-bit arrival.

**Worked example in the appendix (8 Gbps, 100-byte packets):**
- LAN-scale (5 km) total latency computed as **~32.11 μs**
- WAN-scale (5000 km) total latency computed as **~25.07 ms**
The lesson: time-of-flight dominates at WAN distances; overheads and protocols become heavier too.

---

## 3) F.3 — More than two devices: shared media vs switched media

### 3.1 Shared-media networks (buses)
Classic example: early Ethernet and classic I/O buses.
- Only one transmitter at a time (shared resource).
- Need arbitration:
  - **central arbiter** (short distances), or
  - **distributed arbitration** (carrier sense + collision detect + exponential backoff, Ethernet-style).

**High-load behavior:** performance can degrade sharply as collisions/backoff rise.

### 3.2 Switched-media (point-to-point) networks
A set of switches connects nodes via point-to-point links.
- Many nodes can transmit simultaneously.
- Requires 3 additional core functions:
  1) **Topology**: what paths exist?
  2) **Routing**: which paths are allowed/selected?
  3) **Arbitration**: who wins conflicts for resources?
  4) **Switching**: how/when resources are connected for a packet?

**Why switched networks “won”:**
- Switches shrank drastically with VLSI.
- Demand for communication bandwidth rose.
- Many buses are being replaced by switched fabrics (e.g., PCIe replacing PCI-X).

### 3.3 Expanded “black box” latency/bandwidth terms (switched)
For multi-hop switched networks, latency lower bound includes:
- link propagation across hops
- per-hop routing/arbitration/switching delays
- serialization (packet size/bandwidth)

Effective bandwidth (end-to-end) is limited by:
- **injection bandwidth** (source links + sending overhead),
- **network bandwidth** (contention + bisection effects),
- **reception bandwidth** (destination links + receiving overhead).

---

## 4) F.4 — Topology: the shape of the network

### 4.1 Centralized switched networks
- **Crossbar**: nonblocking, but crosspoints scale ~quadratically with ports.
- **Multistage interconnection networks (MINs)** (e.g., Omega/perfect-shuffle):
  - reduce switch cost vs crossbar
  - introduce blocking/contending paths.

**Fat trees** are widely used in commercial HPC and cluster fabrics.

### 4.2 Distributed switched networks (“direct networks”)
Switches are distributed; nodes are also network routers.
Common topologies:
- **Ring**
- **Mesh (grid)**
- **Torus** (wrap-around mesh)
- **Hypercube** (n-cube, where n = log₂N)
These are k-ary n-cubes: k nodes per dimension, n dimensions.

**Implementation constraints:** pin-out and achievable wiring density often matter more than abstract bisection bandwidth.

### 4.3 Bisection bandwidth (performance measure)
Bisection BW is computed by dividing network into two halves and summing link BW crossing the cut.  
For nonsymmetric networks, take the minimum over all equal halves.

The appendix defines an “upper bound” model using a **bisection traffic fraction** γ:

\[
BW_{Network} \approx \frac{BW_{Bisection}}{\gamma}
\]

Interpretation:
- If only a fraction γ of traffic must cross the bisection, the effective “pipe” looks wider.

---

## 5) F.5 — Routing, arbitration, switching (the three knobs that shape contention)

### 5.1 Routing: correctness hazards (livelock, deadlock)
- **Livelock**: packet keeps moving but never reaches destination.
- **Deadlock**: packets block forever holding resources in a cycle.

**Deterministic routing:** always same path for a source-destination pair.  
Example: **dimension-order routing (DOR)** (XY routing, e-cube) on mesh/hypercube.

For tori (wrap-around), avoiding deadlock often needs:
- **virtual channels** (separate logical buffers), or
- constraints such as bubbles / restricted turns.

**Adaptive routing:** chooses among allowed paths based on congestion to improve utilization and throughput.

### 5.2 Arbitration: matching requests to outputs
A common switch arbitration model:
- **request**: input queues request output ports
- **grant**: each output arbiter selects one request (e.g., round-robin)

This can waste bandwidth when multiple inputs contend for the same output. Improvements include:
- allowing multiple requests per input (e.g., via multiple VCs or adaptive options),
- adding an acknowledge phase (request–grant–ack) to improve matching.

### 5.3 Switching: how resources are “held”
Three classic techniques:

1) **Circuit switching**: reserve a circuit before sending.
2) **Store-and-forward**: buffer whole packet at each hop before forwarding.
3) **Cut-through**: forward after header arrives (pipeline across hops).

Cut-through variants:
- **Virtual cut-through**: packet-level flow control.
- **Wormhole**: flit-level flow control; reduces buffer requirement but can spread blocked packets across many switches, risking early saturation unless mitigated.

### 5.4 Performance models include efficiency factors
The appendix introduces an efficiency factor ρ (0–1) capturing how well routing/arbitration/switching use topology resources:

\[
BW_{Network} = \rho \cdot \frac{BW_{Bisection}}{\gamma}
\]

Saturation curves are typical:
- latency is flat at low load
- rises sharply near saturation
- throughput rises linearly then plateaus/drops near saturation (HOL blocking and congestion effects)

---

## 6) F.6 — Switch microarchitecture (what’s inside a router/switch)

### 6.1 Core blocks
A basic switch includes:
- link controllers (serdes/physical interface)
- input buffers/queues (often per-VC)
- routing unit (logic-based or table-based)
- arbitration unit
- crossbar + control
- output buffers (sometimes)

### 6.2 Buffer placement trade-offs
- **Output-buffered**: high throughput but needs internal speedup (faster internal fabric).
- **Input-buffered**: no speedup needed, but suffers **head-of-line (HOL) blocking**.
  - With uniform traffic, HOL can cap utilization below ~60% (as noted in the appendix).
  - **Virtual channels** mitigate but don’t eliminate HOL.
  - **Virtual output queues (VOQs)** eliminate HOL inside a switch by having one queue per output, but VOQ count scales ~quadratically with ports.

### 6.3 Logic-based vs table-based routing
- **Logic-based**: fast, small, low power, but topology-specific.
- **Table-based**: flexible and supports irregular topologies, but can be area/power heavy and scale poorly (worst case ~N tables × N entries).

The appendix highlights LBDR (Logic-Based Distributed Routing) as a compact approach for irregular topologies using connectivity + routing bits.

### 6.4 Pipelining switches
Switch pipelines resemble vector pipelines:
- header drives control of subsequent flits/phits through pipeline stages.
Example pipeline stages:
1) receive header + buffer input
2) route lookup
3) arbitration
4) crossbar config
5) output buffering / launch

---

## 7) F.7 — Practical issues in commercial networks

Key practical topics:
- **Connectivity and where the NI attaches** (memory fabric vs I/O fabric like PCIe/HyperTransport).
- **Cache coherence support** can add overhead (cache flushes on send/receive if not coherent).
- **Standards vs proprietary**: standards improve ecosystem and reduce risk but can be slow/committee-driven.
- **Congestion management**:
  - packet discarding (lossy)
  - flow control (lossless)
  - choke packets (feedback-based throttling; can oscillate if feedback delay is long)
- **Fault tolerance**:
  - spare resources (switch-in spares)
  - bypass/disable faulty components (degraded mode)
  - fault-tolerant routing exploiting multipath
- **Online expansion / hot swapping** needs dynamic reconfiguration; tricky in lossless networks due to deadlock-free routing during table updates.

---

## 8) F.8 — Examples (what to remember)

### 8.1 OCN example: Intel Single-Chip Cloud Computer (SCC)
- 2D mesh of routers/tiles
- credit-based flow control
- virtual cut-through switching
- XY dimension-order routing
- uses multiple virtual channels (noted: 8 VCs; some for deadlock handling)

### 8.2 SAN example: IBM Blue Gene/L 3D torus
- large-scale torus network with adaptive routing + virtual cut-through + multiple VCs (as described)
- fault tolerance via bypassing midplane components and checkpoint/restart

### 8.3 SAN standard: InfiniBand
Two user-level mechanisms:
- **send/receive** (receiver posts receive buffer)
- **RDMA** (sender DMA directly into receiver memory)

Example overhead numbers given (Mellanox card + Xeon host, nominal 4B packet):
- send/receive: send ~0.946 μs, receive ~1.423 μs
- RDMA: send ~0.910 μs, receive ~0.323 μs

Appendix highlights that many apps send *many small messages* (requests/acks) → overhead dominates.

### 8.4 LAN: Ethernet
- IEEE 802.3
- originally shared-media; modern >=1 Gbps uses point-to-point + switches
- link speeds listed as 10/100/10,000/100,000 Mbit/s (2011 context in appendix)
- no “real” standardized flow control in base Ethernet; early arbitration was carrier sense + exponential backoff.

### 8.5 WAN: ATM
- fiber-based WAN standard
- scalable bandwidth in multiples (155 Mbps upward)
- small fixed payload cell: **48 bytes**
- uses virtual connections; emphasizes quality of service and predictability
- uses credit-based flow control (contrast with IP routers)

---

## 9) F.9 — Internetworking: TCP/IP as the archetype

Internetworking connects networks-of-networks.
TCP/IP uses a **layered protocol stack**:
- each layer adds its own header/trailer
- receiver peels them off in reverse (protocol stack)

Benefit: modularity and standardization.  
Cost: extra overhead/latency and complexity (implementation matters).

Appendix includes a representative IP + TCP header example (20-byte base headers, optional extensions).

---

## 10) F.10 Cross-cutting issues (why networks change CPU/system design)

Selected themes:
- data center collocation rewards **density-optimized** designs (space/power/network cost), not just SPEC peak.
- **Smart switches vs smart NICs** (intelligence placement trade-off):
  - Ethernet: cheap NICs, smarter switches at scale.
  - Myrinet: dumb switches, smarter NICs.
  - InfiniBand: hybrid (different adapter classes).
- **Protection + user-level access**: reducing OS involvement can cut overhead, but safety must be preserved.
- memory hierarchies can inadvertently **increase network/I/O access latency** (multiple cache levels + write buffers in front of I/O).
- rule-of-thumb cited: ~1 MHz CPU per 1 Mbit/s TCP/IP bandwidth → 1 Gbit/s can saturate ~1 GHz-class CPU (context: software stack overhead).

---

## 11) F.11 Fallacies and pitfalls (exam-friendly)

- **Fallacy:** bisection bandwidth is an accurate *cost* constraint.  
  It’s more a performance measure; **pin-out** is often the real cost limiter.

- **Pitfall:** insufficient **reception** bandwidth (many-to-one patterns cause destination congestion).

- **Pitfall:** forgetting the **I/O subsystem** between NIC and host (PCI/PCI-X/PCIe bandwidth can bottleneck).

- **Fallacy:** “zero-copy” means no copying anywhere (practical implementations still copy/fragment/align for safety and performance).

- **Pitfall:** ignoring **software overhead** (Amdahl’s Law for networks; software often dominates hardware latency).

- **Fallacy:** wormhole switching is inherently faster than other pipelined switching.  
  Wormhole enabled on-chip buffering at the time; modern virtual cut-through can match no-load latency and often improve throughput when buffers are feasible.

- **Fallacy:** adding a few virtual channels always increases throughput.  
  VCs help only if they’re used to reduce deadlock/congestion/HOL appropriately; otherwise overhead can dominate.

- **Pitfall:** implementing features “in the network” that only work **end-to-end** (Saltzer-Reed-Clark end-to-end argument; hop-by-hop checksums alone don’t guarantee application correctness).

---

## 12) One-page carryover

- Latency model: overhead + flight + serialization + overhead.  
- Effective bandwidth is min(injection, network, reception).  
- Shared media → arbitration limits; switched media → topology/routing/arbitration/switching dominate.  
- Topology: crossbar/MIN/fat-tree vs ring/mesh/torus/hypercube; bisection BW matters for performance, pin-out for cost.  
- Correct routing must avoid livelock/deadlock; DOR (XY) is common; tori often need virtual channels.  
- Switching: circuit vs store-and-forward vs cut-through; wormhole is flit-level cut-through.  
- Switch microarchitecture: buffer placement, HOL blocking, VOQs, pipelining.  
- Real systems: SCC NoC, Blue Gene torus, InfiniBand RDMA/OS bypass, Ethernet, ATM; internetworking via TCP/IP layering.

---

*End of CH13 / Appendix F summary.*
