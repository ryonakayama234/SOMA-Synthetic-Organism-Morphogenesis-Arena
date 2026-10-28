"""Create an offline V003 request-preparation workspace from verified original ONLY.

This does NOT produce a V003 derived world or silently launch Python from HTML.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from experiments.V003.verify import original,accept_source_receipt,read_rows
from experiments.V003.viewer import render_prepare

def export_html(original_root,source_receipt_file,out):
    original_root=Path(original_root)
    accept_source_receipt(original_root,source_receipt_file)
    scene=next(s for s in original(original_root) if s["world_id"]=="C05")
    states=[s for s in read_rows(original_root/"states.jsonl") if s["world_id"]=="C05"]
    if len(states)!=9: raise AssertionError("original C05 nine saved rows required")
    with Path(out).open("x",encoding="utf-8",newline="\n") as handle:
        handle.write(render_prepare(scene,states))
    return {"mode":"prepare_request","derived":"NOT GENERATED","output":str(out)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original-root",type=Path,required=True)
    p.add_argument("--source-receipt",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    print(export_html(a.original_root,a.source_receipt,a.out))

if __name__=="__main__": main()
