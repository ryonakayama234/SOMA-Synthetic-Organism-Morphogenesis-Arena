---
id: EXP-F013
kind: experiment_plan
status: preregistered_not_executed
updated: 2026-10-20
---
# Frozen F013 prospective experimental plan — **UNEXECUTED**

Researcher authorization: 2026-10-20 JST. Applies to SPEC F013 design preregistration before implementation. No F013 simulations have been observed while writing this file.

## Factorial conditions — no tuning
| Case | mu_plus | mu_minus | Drive | Purpose |
| --- | ---: | ---: | --- | --- |
| B-isotropic | 0.04 | 0.04 | ±1N | symmetry zero COM |
| C-directional | 0.02 | 0.08 | ±1N | directionally biased friction rectification |
| D-mirror | 0.08 | 0.02 | ±1N | pointwise mirror of C |
| E-no-drive | 0.02 | 0.08 | 0N | stationary negative |

Each × eps=(0.02,0.005,0.001)m/s × dt=(0.01,0.005,0.0025)s: **36 independent fixed trials**, 9.6s per complete run, each reset to xa=-0.25,xb=+0.25 m, zero velocity. Time steps 960/1920/3840 respectively. Grid transitions at 0.6s exact; phase is indexed by integer half-period count. Do not use seed or parameter optimization. Total separation constrained to [0.2,0.8]m; save failure prefix, mark INCONCLUSIVE.

## Independent preregistered predictions
1. In B, mirror symmetry enforces COM zero pointwise for identical cells and isotropic friction. E has zero drive at spring rest, so exactly stationary.
2. C/D must have equal separation and opposite COM, equal absolute force under reflection and non-positive ground work pointwise. This is independent of whether drift actually exists.
3. Internal force cancels: 1kg*(ΔvA+ΔvB)=dt*(fA+fB). Ground impulse is the only COM momentum source.
4. The smooth friction oddness under simultaneous sign and mu swap produces exact reflection of predicted math; numerical values can have tiny floating deviations.
5. No predetermined C displacement magnitude or model-equivalence claim. F011 benchmark finest C=+3.5023819308m in its ORIGINAL discrete Coulomb model; difference from new law is to be **measured**, not silently attributed to numerical error.
6. H13a positive-drift persistence criteria and H13b timestep 10%/2mm gate fixed in SPEC; if valid results fail, preserve actual failure, not tune eps. Smooth model may not converge uniformly to F011's static/kinetic projection.

## Scientific outputs
Save all raw rows including physical SI units, ground friction impulse/work and discrete defect; final/last two periods COM, r-period return, source and model identity, mirrored controls for all rows, per-eps dt sensitivity and H13a/b/c/d judgement. Report passivity, sum-of-momentum, discrete energy defect and insufficient resolution distinctly.

## Implementation/audit gate
Use independent analytic checks/Wolfram where possible; separate alternate arithmetic solver over saved CSV with no import of F013 simulation, strict manifest+checkout source hashes, rehashed-summary forgery negatives and byte-identical replay. CI Python3.11/3.12, all legacy unit regressions. If independent external human review unavailable mark as NOT PERFORMED. No real electrical battery, active policy, contact normal-force mechanics, 2D, self-model or emergence in scope. Formal adoption and main merge explicitly withheld.
