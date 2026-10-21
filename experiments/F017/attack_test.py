"""Negative research audit: rehash a semantically forged raw episode; MUST reject."""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from experiments.F017.verify import verify_suite

def canonical(x):
    return (json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode()

def assert_rehashed_forgery_rejected(source_root: Path):
    with tempfile.TemporaryDirectory(prefix="f017-forgery-") as tmp:
        fake=Path(tmp)/"candidate"
        shutil.copytree(source_root,fake)
        archive=fake/"episodes.jsonl.gz"
        temp=fake/"recompressed.gz"
        with gzip.open(archive,"rb") as original, temp.open("wb") as raw:
            with gzip.GzipFile(filename="",fileobj=raw,mode="wb",mtime=0,compresslevel=6) as output:
                first=json.loads(original.readline())
                first["net_uj"]+=3_000_000  # fabricated successful energy result
                output.write(canonical(first))
                shutil.copyfileobj(original,output)
        temp.replace(archive)
        manifest=fake/"manifest.json"
        obj=json.loads(manifest.read_text())
        obj["artifacts"]["episodes.jsonl.gz"]=hashlib.sha256(archive.read_bytes()).hexdigest()
        manifest.write_bytes(canonical(obj))  # cryptographic hashes now match tampered data
        try:
            verify_suite(fake)
        except ValueError as e:
            if "independent saved-world rejection" not in str(e):
                raise AssertionError("wrong reason for rejecting rehashed false science") from e
            return {"rehash_verified":True,"semantic_forgery_rejected":True,"reason":str(e)}
        raise AssertionError("F017 falsely accepted a rehashed fake energy outcome")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(assert_rehashed_forgery_rejected(a.root),sort_keys=True))
