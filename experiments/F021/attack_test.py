"""Rehashed semantic tampering must be rejected by independent verifier."""
import argparse
import hashlib
import json
from pathlib import Path
from experiments.F021.verify import verify_root, canonical


def attacks(root: Path):
    files = [json.loads(x) for x in (root/"worlds.jsonl").read_text().splitlines()]
    scenarios = [
        ("position", lambda a: a["steps"][0]["x_after_m"].__setitem__(0, .997)),
        ("energy", lambda a: a["steps"][0]["balance_after_uj"].__setitem__("A", 98765)),
        ("motor", lambda a: a["steps"][0]["decision"]["applied_n"].__setitem__("A", -9.)),
        ("provenance", lambda a: a["scene"].__setitem__("seed", 999)),
        ("claim", lambda a: a["net_uj"].__setitem__("B", 999_999)),
        ("arbitration", lambda a: a["steps"][0]["decision"].__setitem__("reason","accepted_unchecked")),
    ]
    from tempfile import TemporaryDirectory
    for name, mutate in scenarios:
        with TemporaryDirectory() as td:
            output=Path(td)
            worlds=json.loads(json.dumps(files))
            mutate(worlds[0])
            (output/"worlds.jsonl").write_text(
                "".join(canonical(w)+"\n" for w in worlds),encoding="utf-8")
            (output/"summary.json").write_bytes((root/"summary.json").read_bytes())
            manifest=json.loads((root/"manifest.json").read_text())
            manifest["worlds_sha256"]=hashlib.sha256((output/"worlds.jsonl").read_bytes()).hexdigest()
            (output/"manifest.json").write_text(canonical(manifest)+"\n")
            try:
                verify_root(output)
            except (AssertionError,ValueError,KeyError,TypeError):
                pass
            else:
                raise AssertionError(f"forgery not caught: {name}")
    print(f"All {len(scenarios)} rehashed semantic forgeries rejected")


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,required=True)
    args=parser.parse_args()
    attacks(args.root)
