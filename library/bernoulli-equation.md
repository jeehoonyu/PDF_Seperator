---
title: "Bernoulli Equation"
tags: [fluid-mechanics, energy-methods, incompressible-flow, pressure]
domain: fluid-mechanics
prerequisites:
  - "[[conservation-of-energy]]"
  - "[[euler-equations-fluid]]"
  - "[[incompressible-flow]]"
sources:
  - book: "Fundamentals of Fluid Mechanics"
    edition: "8th"
    chapters: [3.4, 3.5]
    pages: [112-119]
status: draft
created: 2026-02-21
last_reviewed: null
confidence: high
---

## One-Sentence Summary

Bernoulli's equation is conservation of mechanical energy per unit volume along a streamline in steady, incompressible, inviscid flow.

## Physical / Conceptual Intuition

Consider a fluid particle traveling along a streamline. In the absence of viscous losses (no friction) and with no energy added or removed (no pumps, no heat transfer), the particle's total mechanical energy must remain constant — this is just the first law of thermodynamics applied to a moving fluid element.

The equation tracks three forms of energy per unit volume: pressure energy (the work the surrounding fluid does on the particle), kinetic energy (from the particle's velocity), and gravitational potential energy (from its elevation). If the particle speeds up, something must pay for that kinetic energy — and it comes from a drop in pressure or elevation or both.

This is why airplane wings generate lift (faster flow on top → lower pressure), why a garden hose sprays faster when you pinch it (smaller area → higher velocity → lower pressure upstream), and why tall water towers work (elevation → pressure at ground level).

## Formal Statement

Along a single streamline in steady, incompressible, inviscid flow with no shaft work or heat transfer:

$$
P + \frac{1}{2}\rho v^2 + \rho g z = \text{constant along a streamline}
$$

Equivalently, between two points 1 and 2 on the same streamline:

$$
P_1 + \frac{1}{2}\rho v_1^2 + \rho g z_1 = P_2 + \frac{1}{2}\rho v_2^2 + \rho g z_2
$$

**Head form** (divide through by $\rho g$):

$$
\frac{P}{\rho g} + \frac{v^2}{2g} + z = \text{constant}
$$

| Variable | Meaning | SI Unit |
|----------|---------|---------|
| $P$ | Static pressure (absolute, not gauge) | Pa (N/m²) |
| $\rho$ | Fluid density | kg/m³ |
| $v$ | Flow velocity (local, along streamline) | m/s |
| $g$ | Gravitational acceleration | m/s² |
| $z$ | Elevation above a chosen datum | m |

## Key Assumptions

1. **Steady flow** — The velocity field does not change with time at any fixed point. If violated: use the unsteady Bernoulli equation, which includes a $\partial \phi / \partial t$ term.

2. **Incompressible flow** — Density $\rho$ is constant. If violated (Mach > ~0.3): use compressible energy equation or isentropic flow relations.

3. **Inviscid flow** — No viscous (frictional) losses. If violated: add a head loss term $h_L$ to get the extended Bernoulli (energy equation): $P_1/\rho g + v_1^2/2g + z_1 = P_2/\rho g + v_2^2/2g + z_2 + h_L$.

4. **Along a single streamline** — The constant is generally different on different streamlines unless the flow is also irrotational. If violated: Bernoulli applies across streamlines only if vorticity is zero everywhere.

5. **No shaft work, no heat transfer** — No pumps, turbines, or significant thermal effects between the two points. If violated: add pump/turbine head terms ($h_p$, $h_t$) to the energy equation.

## Derivation Sketch

Start from Euler's equation (Newton's second law for inviscid fluid). For steady flow along a streamline, integrate the momentum equation from point 1 to point 2. The pressure gradient term integrates to $P_2 - P_1$, the inertial term gives $\frac{1}{2}\rho(v_2^2 - v_1^2)$, and the body force (gravity) gives $\rho g(z_2 - z_1)$. Rearranging yields Bernoulli.

Alternatively: apply the first law of thermodynamics to a control volume along a streamline with no viscous work, shaft work, or heat transfer. The result is identical.

See source pp. 112–114 for the full streamline-coordinate derivation.

## Validity and Limitations

| Condition | Failure Mode | Use Instead |
|-----------|-------------|-------------|
| Compressible flow (Ma > 0.3) | Underestimates pressure changes; density is not constant | Compressible isentropic relations or full energy equation |
| Viscous flow (low Re, long pipes, boundary layers) | Overpredicts velocity / underpredicts pressure drop (ignores friction losses) | Extended Bernoulli with head loss term, or Navier-Stokes |
| Unsteady flow | Misses time-dependent pressure fluctuations | Unsteady Bernoulli equation |
| Across streamlines in rotational flow | The constant differs per streamline; applying across gives wrong answer | Crocco's theorem or full Euler equations |
| Across shocks | Energy is dissipated at the shock; Bernoulli is invalid across it | Normal/oblique shock relations |
| Flow with pumps or turbines | Ignores energy input/extraction | Extended energy equation with $h_p$, $h_t$ terms |

## Worked Example

**Problem:** Water flows through a horizontal pipe that narrows from a diameter of 10 cm to 5 cm. The pressure in the wide section is 200 kPa (gauge). The flow rate is 5 L/s. Find the pressure in the narrow section. Assume water density = 998 kg/m³.

**Solution:**

Step 1 — Compute velocities from continuity ($Q = Av$):

$A_1 = \pi (0.05)^2 = 7.854 \times 10^{-3}$ m², so $v_1 = 0.005 / 7.854 \times 10^{-3} = 0.637$ m/s

$A_2 = \pi (0.025)^2 = 1.963 \times 10^{-3}$ m², so $v_2 = 0.005 / 1.963 \times 10^{-3} = 2.547$ m/s

Step 2 — Horizontal pipe → $z_1 = z_2$, so elevation terms cancel.

Step 3 — Apply Bernoulli:

$$
P_2 = P_1 + \frac{1}{2}\rho(v_1^2 - v_2^2)
$$

$$
P_2 = 200{,}000 + \frac{1}{2}(998)(0.637^2 - 2.547^2)
$$

$$
P_2 = 200{,}000 + 499(-6.083) = 200{,}000 - 3{,}035 \approx 197{,}000 \text{ Pa}
$$

$P_2 \approx 197$ kPa (gauge).

The pressure drops by about 3 kPa as the fluid accelerates through the constriction. This makes physical sense: kinetic energy increases, so pressure energy must decrease.

[Constructed example]

## Common Mistakes

**Using gauge pressure inconsistently.** Bernoulli works with either absolute or gauge pressure, but you must be consistent. Mixing gauge at one point and absolute at another produces errors equal to atmospheric pressure (~101 kPa). This is tempting because manufacturers often report gauge pressure.

**Applying across a shock.** Bernoulli is an energy conservation equation for reversible processes. Shocks are irreversible — entropy increases, total pressure drops. Using Bernoulli across a shock will overpredict downstream pressure recovery.

**Forgetting "along a streamline."** Students often apply Bernoulli between two arbitrary points in a flow field. This is valid only if the flow is irrotational everywhere between those points. In general, the Bernoulli constant differs from one streamline to another.

**Ignoring viscous losses in long pipes.** For pipe flow at engineering lengths, friction losses dominate. Using bare Bernoulli (without head loss) in a 100-meter pipe will give wildly wrong pressure predictions. Use the extended energy equation with Darcy-Weisbach or Moody friction factor.

## Dimensional / Sanity Check

Each term in $P + \frac{1}{2}\rho v^2 + \rho g z$ has dimensions of pressure:
- $P$: Pa = N/m² ✓
- $\frac{1}{2}\rho v^2$: (kg/m³)(m/s)² = kg/(m·s²) = N/m² = Pa ✓
- $\rho g z$: (kg/m³)(m/s²)(m) = kg/(m·s²) = Pa ✓

Limiting behavior:
- As $v \to 0$ (stagnant fluid): reduces to hydrostatic equation $P + \rho g z = \text{const}$ ✓
- As $z_1 = z_2$ (horizontal flow): pressure drops where velocity increases ✓
- As $\rho \to 0$: all terms vanish, which is consistent (no fluid, no pressure) ✓

## Related Topics

- [[conservation-of-energy]] — Bernoulli is the special case for inviscid, incompressible streamline flow
- [[euler-equations-fluid]] — Bernoulli is derived by integrating Euler's equation along a streamline
- [[continuity-equation]] — needed alongside Bernoulli to solve most flow problems (provides the velocity relationship)
- [[navier-stokes]] — the general case that includes viscosity; Bernoulli is the inviscid limit
- [[darcy-weisbach]] — provides the head loss term for extending Bernoulli to viscous pipe flow
- [[pitot-tube]] — direct engineering application of Bernoulli for velocity measurement

---

*Note generated by Claude. Status: draft. Verify against source before relying on this note.*
