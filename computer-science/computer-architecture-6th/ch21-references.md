# CH21 — References (Bibliography) (Summary)

> Source PDF: `ch21-references.pdf`  
> In this PDF set, “Chapter 21” is **the consolidated reference list** for the entire book.

---

## What Chapter 21 contains

This chapter is **not instructional prose**. It is a **bibliography** (≈36 pages) containing **~643 citation entries**, listed in **alphabetical order by first author**.

You use it to:
- locate the original papers/standards behind each chapter’s claims,
- build a reading list by topic (caches, branch prediction, DNN accelerators, cloud/WSCs, coherence, networks, storage),
- and cite the primary sources in your own writeups.

---

## How to use it efficiently

### 1) Use PDF search with a stable key
Most entries can be found quickly by searching:
- `AuthorLastName,` (e.g., `Amdahl,`)
- or `Year` (e.g., `2004`)
- or a distinctive title token (e.g., `MapReduce`, `Roofline`, `TensorFlow`)

### 2) Treat it like a topic map
If you’re “studying by chapter,” it’s often faster to start from a few **anchor references** and then branch outward.

A quick keyword snapshot (counted across the reference text) suggests the heaviest clusters include:
- **network** (~62 occurrences),
- **cache** (~50),
- **memory** (~38),
- **multiprocessor** (~29),
- **branch / prediction** (~23 / ~18).

(These counts are just a rough navigation aid.)

---

## Landmark references (all present in this PDF)

Below are anchor references that align with major book themes.  
This is **not exhaustive**—it’s a curated starting set.

### Parallel performance limits
- Amdahl, G.M., 1967. Validity of the single processor approach to achieving large scalecomputing capabilities. In: Proceedings of AFIPS Spring Joint Computer Conference,April 18–20, 1967, Atlantic City, NJ, pp. 483–485.

### Classic ILP / dynamic scheduling roots
- Anderson, D.W., Sparacio, F.J., Tomasulo, R.M., 1967. The IBM 360 Model 91: processorphilosophy and instruction handling. IBM J. Res. Dev. 11 (1), 8–24.

### Memory consistency
- Adve, S.V., Gharachorloo, K., 1996. Shared memory consistency models: a tutorial. IEEEComput. 29 (12), 66–76.

### Warehouse-scale computing foundations
- Dean, J., Barroso, L.A., 2013. The tail at scale. Commun. ACM 56 (2), 74–80.
- Dean, J., Ghemawat, S., 2004. MapReduce: simplified data processing on large clusters.In: Proceedings of Operating Systems Design and Implementation (OSDI), December6–8, 2004, San Francisco, CA, pp. 137–150.
- Ghemawat, S., Gobioff, H., Leung, S.-T., 2003. The Google file system. In: Proceedings of19th ACM Symposium on Operating Systems Principles, October 19–22, 2003, BoltonLanding, NY.

### Storage reliability / RAID
- Chen, P.M., Lee, E.K., Gibson, G.A., Katz, R.H., Patterson, D.A., 1994. RAID: high-performance, reliable secondary storage. ACM Comput. Surv. 26 (2), 145–188.

### Performance modeling for DLP / multicore
- Williams, S., Waterman, A., Patterson, D., 2009. Roofline: an insightful visual performancemodel for multicore architectures. Commun. ACM 52 (4), 65–76.

### Modern ML systems (ties to Ch.7 DSAs and DNN workloads)
- Abadi, M., Barham, P., Chen, J., Chen, Z., Davis, A., Dean, J., Devin, M., Ghemawat, S.,Irving, G., Isard, M., Kudlur, M., 2016. TensorFlow: A System for Large-ScaleMachine Learning. In: OSDI (November), vol. 16, pp. 265–283.

### IEEE floating-point standard history pointer (IEEE 754 family)
Search within the PDF for:
- `IEEE standard for binary floating-point arithmetic` (IEEE, 1985)
- `IEEE 754-2008 Working Group` (draft/standard reference; DOI is included)

Example snippet (present in this bibliography):
- IEEE 754-2008 Working Group, 2006. DRAFT Standard for Floating-Point Arithmetic 754-2008, doi:10.1109/IEEESTD.2008.4610935.

---

## What I did not do here (by design)

Because Chapter 21 is a bibliography:
- there are **no concepts, diagrams, or derivations** to summarize the way Chapters 1–7 and Appendices A–K do,
- and it would not be useful (or readable) to rewrite all ~643 entries into Markdown.

Instead, the value-add is: **how to navigate** + **which anchors to start from**.

---

*End of Chapter 21 summary.*
