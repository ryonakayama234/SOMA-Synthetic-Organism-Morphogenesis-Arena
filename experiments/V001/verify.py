"""Independent saved-file audit for V001 display evidence.

Do not trust a viewer manifest to validate its own observations or origin.
"""
from __future__ import annotations

import json
from pathlib import Path

from soma.f007 import provenance
from soma.v001 import canonical_json, sha256, verify_frame_projection


def check(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def audit_view(source: Path, output: Path, *, trusted_origin: dict | None = None) -> dict:
    from experiments.V001.build_view import (
        ARTIFACTS, ROOT, VIEWER_SOURCES, html_from_frames,
    )
    source, output = Path(source), Path(output)
    identity = provenance() if trusted_origin is None else trusted_origin
    expected_input_files = {
        "config.json", "states.csv", "link_events.csv",
        "ledger/events.csv", "manifest.json", "motion.svg",
    }
    expected_output = set(ARTIFACTS) | {"viewer_manifest.json"}
    actual_files = {
        f.relative_to(output).as_posix() for f in output.rglob("*")
        if f.is_file()
    }
    check(actual_files == expected_output, "unexpected/missing V001 output files")
    manifest = json.loads((output / "viewer_manifest.json").read_text("utf-8"))
    required = {"schema_version", "experiment_id", "source_artifacts_sha256",
                "trusted_f007_origin", "viewer_sources_sha256",
                "output_artifacts_sha256", "verification"}
    check(set(manifest) == required, "V001 manifest keys")
    check(manifest["schema_version"] == "v001.evidence.v1", "V001 evidence schema")
    check(manifest["trusted_f007_origin"] == identity, "untrusted origin")
    check(set(manifest["source_artifacts_sha256"]) == expected_input_files,
          "incomplete F007 artifact dependencies")
    for name, digest in manifest["source_artifacts_sha256"].items():
        check(sha256(source / name) == digest, "F007 source hash mismatch: " + name)
    check(set(manifest["viewer_sources_sha256"]) == set(VIEWER_SOURCES),
          "incomplete V001 source dependency set")
    for name, digest in manifest["viewer_sources_sha256"].items():
        check(sha256(ROOT / name) == digest, "V001 code hash mismatch: " + name)
    check(set(manifest["output_artifacts_sha256"]) == set(ARTIFACTS),
          "incorrect V001 artifact list")
    for name, digest in manifest["output_artifacts_sha256"].items():
        check(sha256(output / name) == digest, "V001 output hash mismatch: " + name)

    raw_frames = (output / "frames.json").read_bytes()
    frames = json.loads(raw_frames)
    check(canonical_json(frames) == raw_frames, "noncanonical frames.json")
    verdict = verify_frame_projection(source, frames, trusted_origin=identity)
    check(manifest["experiment_id"] == frames["experiment_id"], "experiment ID mismatch")
    check(manifest["verification"] == verdict, "forged validation summary")
    check((output / "viewer.html").read_bytes() == html_from_frames(raw_frames),
          "viewer HTML differs from verified frame payload / template")
    return verdict
