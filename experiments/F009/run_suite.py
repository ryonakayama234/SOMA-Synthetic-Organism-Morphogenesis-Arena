"""Frozen F009 A-F run/replay, independent saved-data verification."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import tempfile

from soma.f009 import CASES, config_for, save_run, source_hashes
from experiments.F009.verify import verify_run, verify_suite


def generate(target: Path) -> None:
    target.mkdir(parents=True,exist_ok=False)
    for case in CASES:
        save_run(config_for(case),target/case)
    cases=[verify_run(target/name) for name in CASES]
    summary={"schema_version":"f009.comparison.v1",
             "science_status":"model_result_candidate_not_adopted",
             "cases":cases}
    (target/"comparison.json").write_text(
        json.dumps(summary,sort_keys=True,ensure_ascii=False,indent=2)+"\n",
        encoding="utf-8")
    files={p.relative_to(target).as_posix():sha256(p.read_bytes()).hexdigest()
           for p in sorted(target.rglob("*")) if p.is_file()}
    suite={"schema_version":"f009.suite.v1","cases":list(CASES),
           "artifacts":files,"source_hashes":source_hashes()}
    (target/"suite_manifest.json").write_text(
        json.dumps(suite,sort_keys=True,ensure_ascii=False,indent=2)+"\n",
        encoding="utf-8")
    verify_suite(target)


def run_pair(first: Path, second: Path) -> dict:
    first,second=Path(first).resolve(),Path(second).resolve()
    if first==second or first in second.parents or second in first.parents:
        raise ValueError("replay output directories overlap")
    if first.exists() or second.exists():
        raise FileExistsError("F009 evidence output exists")
    first.parent.mkdir(parents=True,exist_ok=True)
    second.parent.mkdir(parents=True,exist_ok=True)
    one=Path(tempfile.mkdtemp(prefix=".f009-stage-",dir=first.parent))
    two=Path(tempfile.mkdtemp(prefix=".f009-stage-",dir=second.parent))
    try:
        generate(one/"evidence")
        generate(two/"evidence")
        left=one/"evidence"
        right=two/"evidence"
        a={p.relative_to(left):p.read_bytes() for p in left.rglob("*") if p.is_file()}
        b={p.relative_to(right):p.read_bytes() for p in right.rglob("*") if p.is_file()}
        if a!=b:
            raise ValueError("F009 byte replay differs")
        report=verify_suite(left)
        verify_suite(right)
        # Two destination publication is NOT crash-atomic; no existing output replaced.
        if first.exists() or second.exists():
            raise FileExistsError("destination created during audit")
        os.rename(left,first)
        try:
            if second.exists():
                raise FileExistsError("replay destination appeared")
            os.rename(right,second)
        except BaseException:
            shutil.rmtree(first)
            raise
        return report
    finally:
        shutil.rmtree(one,ignore_errors=True)
        shutil.rmtree(two,ignore_errors=True)


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--replay-output-dir",type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(run_pair(args.output_dir,args.replay_output_dir),
                     ensure_ascii=False,sort_keys=True,indent=2))


if __name__=="__main__":
    main()
