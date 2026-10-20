"""F013 frozen 36-run experiment, source-bound evidence and deterministic replay."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import tempfile

from soma.f013 import CASES, COLUMNS, DTS, EPSILONS, Config, StrokeLimitError, simulate, summarize
from experiments.F013.verify import verify
from experiments.F013.ode_audit import independent_ode_audit

REPO = Path(__file__).resolve().parents[2]
SOURCES = ("soma/f013.py", "experiments/F013/run_suite.py",
           "experiments/F013/verify.py", "experiments/F013/ode_audit.py",
           "topics/F013-contact-rectification/SPEC.md",
           "experiments/F013/PLAN.md")


def canonical(obj):
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True,
                       indent=2, allow_nan=False) + "\n").encode("utf-8")


def write_json(path, value):
    path.write_bytes(canonical(value))


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def persistent(c):
    if c is None or not c.get("complete"):
        return False
    a, b = c["last_period_m"], c["penultimate_period_m"]
    return (a*b > 0 and min(abs(a), abs(b)) > .001 and
            min(abs(a), abs(b)) >= .5*max(abs(a), abs(b)) and
            abs(c["last_period_r_return_m"]) <= .01)


def key(case, eps, dt):
    return f"{case}/eps-{eps:g}/dt-{dt:g}"


def build(root):
    if root.exists():
        raise FileExistsError(f"no overwrite: {root}")
    root.mkdir(parents=True)
    output = {}
    for case in CASES:
        for eps in EPSILONS:
            for h in DTS:
                cfg = Config(case, float(eps), float(h))
                folder = root / key(case, eps, h)
                folder.mkdir(parents=True)
                write_json(folder/"config.json", cfg.as_dict())
                try:
                    rows = simulate(cfg)
                    outcome = "complete"
                    attempted = None
                    stopped_at = None
                except StrokeLimitError as e:
                    rows = e.valid_rows
                    outcome = "stroke_inconclusive"
                    attempted = e.attempted_r
                    stopped_at = e.step
                with (folder/"states.csv").open("w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
                    writer.writeheader()
                    writer.writerows(rows)
                stats = summarize(rows)
                stats.update(outcome=outcome, invalid_step=stopped_at,
                             attempted_r_m=attempted)
                output[key(case, eps, h)] = stats

    # No favorable model selection. Each fixed width must pass its OWN timestep gate.
    dt_status = {}
    for case in CASES:
        for eps in EPSILONS:
            a = output[key(case, eps, .005)]
            b = output[key(case, eps, .0025)]
            if not a["complete"] or not b["complete"]:
                status = "INCONCLUSIVE"
            else:
                x, y = a["center_final_m"], b["center_final_m"]
                tol = max(.002, .1*abs(y))
                same_sign = x*y > 0 or (abs(x) <= 1e-10 and abs(y) <= 1e-10)
                status = "SUPPORTED" if abs(x-y) <= tol and same_sign else "INCONCLUSIVE"
            dt_status[f"{case}/eps-{eps:g}"] = status

    directional = []
    for eps in EPSILONS:
        c = output[key("C-directional", eps, .0025)]
        d = output[key("D-mirror", eps, .0025)]
        if (dt_status[f"C-directional/eps-{eps:g}"] != "SUPPORTED" or
                dt_status[f"D-mirror/eps-{eps:g}"] != "SUPPORTED" or
                not c["complete"] or not d["complete"]):
            directional.append("INCONCLUSIVE")
        elif persistent(c) and persistent(d) and c["center_final_m"] > 0 and d["center_final_m"] < 0:
            directional.append("SUPPORTED")
        else:
            directional.append("CONTRADICTED")

    if "INCONCLUSIVE" in directional:
        h13a = "INCONCLUSIVE"
    elif all(v == "SUPPORTED" for v in directional):
        h13a = "SUPPORTED"
    else:
        h13a = "CONTRADICTED"

    # This is a cross-CONSTITUTIVE law observation, not a finite-dt numerical error estimate.
    fine = output[key("C-directional", .001, .0025)]
    comparison = dict(
        schema_version="f013.comparison.v1", preregistered_runs=36,
        results=output,
        h13a=h13a, per_epsilon_h13a=directional,
        h13b=dt_status,
        h13c="INCONCLUSIVE",
        f011_reference_center_m=3.50238193081765,
        f013_minus_f011_center_m=(fine["center_final_m"] - 3.50238193081765
                                  if fine["complete"] else None),
        h13d="SUPPORTED",
        model_limit="different continuous C0 directional tanh constitutive law (not globally C1); NOT real contact or learned locomotion",
    )
    write_json(root/"comparison.json", comparison)
    write_json(root/"ode_audit.json", independent_ode_audit(output))
    names = sorted(str(x.relative_to(root)) for x in root.rglob("*") if x.is_file())
    manifest = dict(
        schema_version="f013.evidence.v1",
        source_sha256={p:file_sha(REPO/p) for p in SOURCES},
        files_sha256={p:file_sha(root/p) for p in names},
    )
    write_json(root/"manifest.json", manifest)


def run(output: Path, replay: Path):
    if output.resolve() == replay.resolve():
        raise ValueError("output and replay directories must differ")
    if output.exists() or replay.exists():
        raise FileExistsError("refuse replacement of experimental evidence")
    for folder in (output.parent, replay.parent):
        folder.mkdir(parents=True, exist_ok=True)
    staging = []
    installed = []
    try:
        for target in (output, replay):
            tmp = Path(tempfile.mkdtemp(prefix=".f013-stage-", dir=target.parent))
            shutil.rmtree(tmp)
            staging.append((tmp, target))
            build(tmp)
            verify(tmp)
        a, b = staging[0][0], staging[1][0]
        paths_a = sorted(str(p.relative_to(a)) for p in a.rglob("*") if p.is_file())
        paths_b = sorted(str(p.relative_to(b)) for p in b.rglob("*") if p.is_file())
        if paths_a != paths_b or any((a/p).read_bytes() != (b/p).read_bytes() for p in paths_a):
            raise AssertionError("F013 same-byte replay mismatch")
        for tmp, target in staging:
            os.replace(tmp, target)
            installed.append(target)
        return len(paths_a)
    except BaseException:
        for tmp, _ in staging:
            if tmp.exists():
                shutil.rmtree(tmp)
        for target in installed:
            if target.exists():
                shutil.rmtree(target)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--replay-output-dir", required=True, type=Path)
    args = parser.parse_args()
    count = run(args.output_dir, args.replay_output_dir)
    print(f"F013 VERIFIED: 36 fixed cases, {count} files per destination, independent raw audit and identical replay")
    report = json.loads((args.output_dir/"comparison.json").read_text(encoding="utf-8"))
    print("F013 SCIENTIFIC OUTCOMES " + json.dumps({
        "h13a": report["h13a"],
        "per_epsilon_h13a": report["per_epsilon_h13a"],
        "h13b": report["h13b"],
        "c_fine": {str(e): report["results"][key("C-directional", e, .0025)] for e in EPSILONS},
        "f013_minus_f011_center_m": report["f013_minus_f011_center_m"],
    }, sort_keys=True))
