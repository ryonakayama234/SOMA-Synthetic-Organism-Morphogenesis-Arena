# F009 reproduction — 1D force-source and momentum experiment

Status: implementation candidate, NOT adopted. Uses only Python 3.11/3.12 standard library and the adopted F007 dependency for historical regression.

From repository root on Linux / WSL2 bash:

    python -m unittest discover -s tests -v
    python -O -m unittest discover -s tests -p test_f009.py -v
    python -m experiments.F009.run_suite --output-dir runs/F009-ci --replay-output-dir runs/F009-replay

Existing output destinations are never replaced. Use new names to rerun, or deliberately delete **only your own** generated F009 run directory; never delete historical F001-F008 data.

F009 frozen A-F are fixed in SPEC/PLAN and independently recomputed from exact Fraction formulae in verify.py, not from the F009 simulation. Each saved run has config.json, steps.csv, manifest.json (with source SHA256); comparison.json and suite_manifest.json cover the whole six-case run. Replays must be byte-identical in the same checkout. Hash consistency is not author authentication: externally inspect the GitHub checkout and HEAD/CI identity.

Force_origin legacy_effective is F007-equivalent external effective force, not evidence of ground propulsion. internal_pair applies equal-and-opposite internal forces to A/B, not a hidden world force. ground_contact uses an ideal 1D traction-cap parameter and stores equal/opposite ground reaction; does not simulate wheel/foot/slip normal mechanics. No motor efficiency, real battery, contact discovery, cell cognition or emergence. Researcher-only world-state logs must not be injected into F008 local observation.

Evidence and scientific interpretation are in findings/F009-validation.md. The user alone decides formal adoption and main merge.
