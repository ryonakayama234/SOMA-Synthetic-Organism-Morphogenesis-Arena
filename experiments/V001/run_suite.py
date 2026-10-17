"""V001 A-F saved-run projection, negative controls, and byte replay."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import tempfile

from experiments.F007.run_suite import scenarios
from experiments.F007.verify import audit_run
from experiments.V001.build_view import generate
from experiments.V001.verify import audit_view
from soma.f007 import Config, provenance, publish_dir, save_run
from soma.v001 import canonical_json, sha256

CASES = (
    "A-free", "B-linked", "C-zero", "D-external", "E-cut",
    "F-01", "F-02", "F-03", "F-04",
)
ARTIFACTS = ("frames.json", "viewer.html", "viewer_manifest.json")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def suite_pass(output: Path, identity: dict) -> dict:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() or output.is_symlink():
        raise FileExistsError(str(output))
    stage = Path(tempfile.mkdtemp(prefix="." + output.name + "-stage-",
                                 dir=output.parent))
    try:
        data = {}
        scenarios_by_name = scenarios()
        for name in CASES:
            source = stage / "f007" / name
            visual = stage / "v001" / name
            source.parent.mkdir(parents=True, exist_ok=True)
            visual.parent.mkdir(parents=True, exist_ok=True)
            save_run(Config.from_dict(scenarios_by_name[name]), source, identity=identity)
            old = {p:sha256(source / p) for p in (
                "config.json", "states.csv", "ledger/events.csv",
                "link_events.csv", "motion.svg", "manifest.json",
            )}
            audit_run(source, trusted_origin=identity)
            generate(source, visual, trusted_origin=identity)
            report = audit_view(source, visual, trusted_origin=identity)
            require(report["coverage"] == 1.0, name + " coverage")
            require(report["frames_checked"] == 1 +
                    Config.from_dict(scenarios_by_name[name]).steps,
                    name + " frame count")
            require(old == {p:sha256(source / p) for p in old},
                    name + " F007 source modified")
            content = json.loads((visual / "frames.json").read_text("utf-8"))
            frames = content["frames"]
            if name == "A-free":
                require(all(not f["attached"] for f in frames), "A should be free")
            if name == "B-linked":
                require(all(f["attached"] for f in frames), "B should be joined")
                require(all(abs(f["x_b_m"]-f["x_a_m"]-0.5)<1e-12 for f in frames),
                        "B rigid gap")
            if name == "E-cut":
                require([f["attached"] for f in frames] ==
                        [True,True,False,False,False], "E-cut post-event semantics")
                require(frames[2]["link_event_kind"] == "detach" and
                        frames[2]["time_s"] == 0.5, "E-cut time/event")
                require(frames[-1]["x_a_m"] == 0.8125 and
                        frames[-1]["x_b_m"] == 0.9375, "E-cut Wolfram end positions")
            if name == "F-01":
                require(frames[1]["balance_a_uj"] == 0 and
                        all(f["motor_applied_n"] == 0 for f in frames[2:]),
                        "F-01 depleted motor must stop")
            data[name] = {
                "frames": report["frames_checked"],
                "source_states_sha256": sha256(source / "states.csv"),
                "viewer_frame_sha256": sha256(visual / "frames.json"),
                "viewer_html_sha256": sha256(visual / "viewer.html"),
                "verdict": report["verdict"],
            }
        result = {
            "schema_version":"v001.suite.v1", "case_count":len(CASES),
            "cases":data, "verified_step_count":sum(x["frames"] for x in data.values()),
            "conclusion":"saved source projection matches",
        }
        (stage / "comparison.json").write_bytes(canonical_json(result))
        publish_dir(stage, output)
        return result
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def full_replay(primary: Path, secondary: Path) -> dict:
    primary, secondary = Path(primary), Path(secondary)
    identity = provenance()
    a = suite_pass(primary, identity)
    b = suite_pass(secondary, identity)
    require(a == b, "replay suite reports differ")
    all_names = ["comparison.json"]
    for case in CASES:
        all_names += [f"v001/{case}/{name}" for name in ARTIFACTS]
        all_names += [f"f007/{case}/{name}" for name in (
            "config.json", "states.csv", "ledger/events.csv",
            "link_events.csv", "motion.svg", "manifest.json",
        )]
    require(all((primary / n).read_bytes() == (secondary / n).read_bytes()
                for n in all_names), "byte replay mismatch")
    return {
        **a,
        "replay_files_checked": len(all_names),
        "byte_replay_match": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--replay-output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(full_replay(args.output_dir, args.replay_output_dir),
                     sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
