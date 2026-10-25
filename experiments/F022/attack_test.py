"""Rehashed semantic archive attacks, including deletion and input forgery."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from experiments.F022.verify import verify


def canonical(v):
    return json.dumps(v, sort_keys=True, separators=(',', ':'), allow_nan=False)


def write(path, obj, lines=False):
    path.write_text((''.join(canonical(x)+'\n' for x in obj) if lines else
                    canonical(obj)+'\n'), encoding='utf-8', newline='\n')


def attack(root):
    target = Path(root)
    scenarios = [
        ('changed_impulse', 'contacts.jsonl', lambda r: r[0].__setitem__('impulse_ns', r[0]['impulse_ns']+.125)),
        ('changed_normal', 'contacts.jsonl', lambda r: r[2].__setitem__('normal_y', r[2]['normal_y']+.1)),
        ('changed_event_time', 'contacts.jsonl', lambda r: r[0].__setitem__('time_s', r[0]['time_s']+.01)),
        ('removed_event', 'contacts.jsonl', lambda r: r.pop(0)),
        ('changed_state', 'states.jsonl', lambda r: r[12].__setitem__('vx_a_mps', r[12]['vx_a_mps']+.125)),
        ('altered_world', 'scenario.json', lambda r: r['worlds'][0].__setitem__('x_a_m',-1.2)),
        ('fabricated_no_contact', 'contacts.jsonl', lambda r: r.clear()),
        ('missing_row', 'states.jsonl', lambda r: r.pop()),
    ]
    with tempfile.TemporaryDirectory(prefix='f022-attacks-') as scratch:
        for idx,(name, filename, mutation) in enumerate(scenarios):
            work = Path(scratch)/f'case-{idx:02d}'
            shutil.copytree(target, work)
            path = work/filename
            lines = filename.endswith('jsonl')
            obj = [json.loads(x) for x in path.read_text().splitlines()] if lines else json.loads(path.read_text())
            mutation(obj)
            write(path, obj, lines)
            manifest_path = work/'manifest.json'
            manifest = json.loads(manifest_path.read_text())
            keys = {'contacts.jsonl':'contacts_sha256','states.jsonl':'states_sha256',
                    'scenario.json':'config_sha256'}
            manifest[keys[filename]] = hashlib.sha256(path.read_bytes()).hexdigest()
            write(manifest_path, manifest)
            try:
                verify(work)
            except (AssertionError, ValueError, KeyError, TypeError):
                pass
            else:
                raise AssertionError(f'{name}: verifier accepted rehashed fabrication')
    return {'rehash_semantic_attacks_rejected':len(scenarios)}


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,required=True)
    args=p.parse_args()
    print(canonical(attack(args.root)))
