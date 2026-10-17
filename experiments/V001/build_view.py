"""Build and audit a deterministic, offline V001 replay from an immutable F007 run.

Run from repo root:
python -m experiments.V001.build_view --source runs/F007-ci/E-cut --output runs/V001/E-cut
"""
from __future__ import annotations

import argparse
import base64
import json
import shutil
import tempfile
from pathlib import Path

from soma.f007 import provenance, publish_dir
from soma.v001 import canonical_json, project_run, sha256, verify_frame_projection

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "experiments/V001/viewer_template.html"
VIEWER_SOURCES = (
    "soma/v001.py", "experiments/V001/build_view.py",
    "experiments/V001/viewer_template.html", "experiments/V001/verify.py",
)
ARTIFACTS = ("frames.json", "viewer.html")


def html_from_frames(data: bytes) -> bytes:
    template = TEMPLATE.read_text(encoding="utf-8")
    if template.count("__FRAME_B64__") != 1:
        raise ValueError("viewer template payload marker")
    value = base64.b64encode(data).decode("ascii")
    return template.replace("__FRAME_B64__", value).encode("utf-8")


def generate(source: Path, destination: Path, *, trusted_origin: dict | None = None) -> dict:
    """Stage and independently verify before no-replace publication."""
    source, destination = Path(source), Path(destination)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(str(destination))
    identity = provenance() if trusted_origin is None else trusted_origin
    input_files = ("config.json", "states.csv", "link_events.csv",
                   "ledger/events.csv", "manifest.json", "motion.svg")
    before = {f: sha256(source / f) for f in input_files}
    payload = project_run(source, trusted_origin=identity)
    verification = verify_frame_projection(source, payload, trusted_origin=identity)
    frame_bytes = canonical_json(payload)
    html_bytes = html_from_frames(frame_bytes)
    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="." + destination.name + "-stage-",
                                 dir=destination.parent))
    try:
        (stage / "frames.json").write_bytes(frame_bytes)
        (stage / "viewer.html").write_bytes(html_bytes)
        manifest = {
            "schema_version": "v001.evidence.v1",
            "experiment_id": payload["experiment_id"],
            "source_artifacts_sha256": before,
            "trusted_f007_origin": identity,
            "viewer_sources_sha256": {
                name: sha256(ROOT / name) for name in VIEWER_SOURCES
            },
            "output_artifacts_sha256": {
                name: sha256(stage / name) for name in ARTIFACTS
            },
            "verification": verification,
        }
        (stage / "viewer_manifest.json").write_bytes(canonical_json(manifest))
        from experiments.V001.verify import audit_view
        audit_view(source, stage, trusted_origin=identity)
        after = {f: sha256(source / f) for f in input_files}
        if before != after:
            raise ValueError("F007 source changed while preparing V001 output")
        publish_dir(stage, destination)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True,
                        help="Existing, F007-verifiable run directory")
    parser.add_argument("--output", type=Path, required=True,
                        help="New, previously unused output directory")
    args = parser.parse_args()
    result = generate(args.source, args.output)
    print(json.dumps({
        "output": str(args.output),
        "experiment_id": result["experiment_id"],
        "frame_count": result["verification"]["frames_checked"],
        "verdict": result["verification"]["verdict"],
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
