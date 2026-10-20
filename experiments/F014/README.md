# F014: frozen one-bit peer-response experiment (implementation candidate)

F014 is a **candidate**, never evidence of an actual robot, mechanical attachment detection, radio hardware or emergent autonomy. F014 design preregistration is [Draft PR #46](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/46). This implementation PR is stacked onto that design branch.

## Reproduce on WSL2/Linux (Python 3.11 or 3.12)

```bash
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -p test_f014.py -v
python -m experiments.F014.run_suite \
  --output-dir runs/F014-local \
  --replay-output-dir runs/F014-local-replay
```

Output directories MUST be absent, separate, and non-nested. The suite builds, audits, and compares two private copies before publishing; existing targets are never overwritten. Artifact upload is performed by the [F014 workflow](../../.github/workflows/f014.yml) only on success.

## Fixed matrix and audit

L linked, G unlinked ghost, C unlinked coforced, N unlinked free, E unexcited; each at 2, 1 and 0.5 N, four 0.25s steps per run. Exactly **15 runs, 60 observed intervals** plus 3 deterministic step-2 packet-dropout diagnostics. These are numeric simulation runs, not live or noisy sensor readings.

Within each run directory: `config.json` (f014.config.v1 research-only frozen envelope), `F007/config.json`, `F007/states.csv` and F007 ledger/link/SVG/manifest artifacts, `a_local.csv` (adopted F008 A allowlist), `b_packets.csv` (framed B-origin 1-boolean observation). Global `comparison.json` carries researcher-only case labels and verdict; `manifest.json` hashes all evidence and the full source-inventory hashes via `origin`.

`soma.f014.estimate_trial` accepts only typed `LocalObservation` and `PeerPacket`; it reports `peer_motion_seen`, `peer_still`, or `inconclusive`, NEVER `attached`. Raw B speed, world forces and topology are confined to the producer adapter and independently to the verifier. A missing B packet is `None`, not `False`, and invalid packet metadata is rejected. The one bit is the sensor payload, not the total transport framing.

`experiments.F014.verify` does not import the F014 inference or producer; it checks immutable raw rows using F007's separate independent oracle and checks all new A/B outputs against rational formulas, exact same-byte L/G/C and L/C controls, summary meaning and SHA integrity. The tests mutate peer bits and research claims and recompute SHA to verify semantic rejection.

## Expected (preregistered; check actual CI evidence)

At input `u`, A acceleration L/G/C = `u/2`; B moves in L/C but not G. Thus a single B binary observation discriminates **L/G under the fixed hypotheses**, but L/C remain observationally equivalent even with full A-local and B binary streams. E and packet-dropout are inconclusive. **No topology identification**.

Review [SPEC](../../topics/F014-peer-body-observability/SPEC.md), [PLAN](PLAN.md), and [findings](../../findings/F014-validation.md). Do not mark the candidate formally adopted without a separately reviewed successful CI run on final SHA.
