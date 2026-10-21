# F017 implementation candidate — receiver-only core

**STAGE: IMPLEMENTATION DRAFT / NO F017 WORLD EXPERIMENT / DESIGN NOT FROZEN / NOT ADOPTED.**
[Issue #57](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/57) / [design PR #59](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/pull/59) / [SPEC](../../topics/F017-signal-action-learning/SPEC.md) / [PLAN](PLAN.md) / [UNEXECUTED findings](../../findings/F017-validation.md).

First isolated module `soma/f017.py` is a minimal opaque-symbol receiver, not a physical simulator. It supplies `RawPeerSymbol`, `context_of`, `Receiver.observe`, `Receiver.learn`, `Receiver.end_without_learning`, and a research-only `snapshot`. Receiver observes opaque framed B-origin 0/1 (or None), selects ±2.0 N, and updates only from A-owned acquired/motor-spent µJ amounts. No F016 known mapping, target label, hidden reversal flag, A/B topology or B sender cost is available to this API.

The independent experiment runner, F007+F002 reuse, 19,968-episode six-arm world suite, source-bound saved-world oracle, tampering probes, full visualization, production CI and scientific verification **ARE NOT IMPLEMENTED** here. `tests/test_f017.py` exercises interface contracts and synthetic feedback only; **synthetic tests are not empirical F017 learning results**. New tests may execute in inherited GitHub Actions; no F017 resource-world episode is run as part of this implementation stage.

Before a first F017 world simulation: (1) resolve latest-main documentation conflict in design PR #59, (2) independently audit/freeze preregistration/seed generation and research gates, (3) merge design separately, (4) extend this branch into a dedicated implementation/evidence candidate and complete raw-world verification. Preserve all existing F001–F016 modules and findings.
