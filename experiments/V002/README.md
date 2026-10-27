# V002 implementation candidate — independent source-verified archived two-world projection

**STATUS: CANDIDATE / UNVALIDATED / NO BROWSER ACCEPTANCE / NOT ADOPTED.**
Parent [#86](https://github.com/ryonakayama234/SOMA-Synthetic-Organism-Morphogenesis-Arena/issues/86), frozen v1 design at `4ba05357a426edaa7ec6e9d1d5f905ad64893de8`.

This first implementation slice creates only an immutable derived `view.json`; no physical simulation, new panels or UI implementation is claimed yet. It invokes original F022/F023 *independent saved-data* verifiers, with externally provided exact source SHAs; independently checks source-row projection and applies the frozen JSON schema.

From WSL2/Linux repository root:

```bash
python -m pip install jsonschema
python -m experiments.F022.run_suite --out /tmp/v002-f022-archive
python -m experiments.V002.project --left-root /tmp/v002-f022-archive --right-root /tmp/v002-f022-archive \
  --left-world C01 --right-world C02 \
  --expected-left-sha "$(git rev-parse HEAD)" --expected-right-sha "$(git rev-parse HEAD)" \
  --trusted-left-anchor "checked-out-source:$(git rev-parse HEAD)" \
  --trusted-right-anchor "checked-out-source:$(git rev-parse HEAD)" --out /tmp/v002-demo
```

**Trusted anchors are a caller responsibility.** A label string alone is not secure authentication: the caller must establish expected SHA through an independently inspected checkout and approval record. Self-hashed archival manifests never establish trust. Archive verifier must succeed for *both* sources before publishing output. Source archive bytes are not rewritten.

Next in the same isolated implementation PR: complete read-only six-panel browser display, source-independent view-bundle rejection oracle, semantic forgery controls, two-root deterministic audit, and browser/manual study acceptance. No technical qualification or main merge until these are done.
