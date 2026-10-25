"""Produce F022.v1 fixed two-disk 13-world evidence; no overwrite."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
from soma.f022 import FREEZE_COMMIT, SCHEMA, grid, simulate, validate


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def provenance():
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    if len(sha) != 40 or not all(c in '0123456789abcdef' for c in sha):
        raise ValueError('unknown source SHA')
    return sha


def _write_json(path, obj):
    path.write_text(canonical(obj)+'\n', encoding='utf-8', newline='\n')


def _write_jsonl(path, rows):
    path.write_text(''.join(canonical(v)+'\n' for v in rows), encoding='utf-8', newline='\n')


def _invalid_probes():
    base = grid()[0]
    def changed(**kw):
        return dict(base, **kw)
    scenes = [changed(x_a_m=-.2, x_b_m=.2),
              changed(x_a_m=0., x_b_m=0.),
              changed(x_a_m=float('nan')),
              changed(mass_a_kg=-1.),
              changed(x_a_m=-.5, x_b_m=.5)]
    for name, s in zip(('J01','J02','J03','J04','J05'), scenes):
        try:
            validate(s)
        except ValueError:
            continue
        raise ArithmeticError(f'{name} invalid input accepted')
    return {f'J{i:02d}': 'rejected' for i in range(1,6)}


def produce(dest: Path, *, source_sha: str | None = None):
    dest = Path(dest)
    if dest.exists():
        raise FileExistsError(f'refuse to overwrite {dest}')
    if source_sha is None:
        source_sha = provenance()
    if len(source_sha) != 40 or any(c not in '0123456789abcdef' for c in source_sha):
        raise ValueError('invalid source SHA')
    scenes = grid()
    if len(scenes) != 13 or len({s['world_id'] for s in scenes}) != 13:
        raise ArithmeticError('frozen roster broken')
    for s in scenes:
        validate(s)
    probes = _invalid_probes()
    state_rows, contact_rows, details = [], [], []
    for s in scenes:
        states, events = simulate(s)
        if len(states) != 9 or len(events) > 1:
            raise ArithmeticError('invalid event or sample cardinality')
        state_rows.extend(states)
        contact_rows.extend(events)
        details.append({'world_id': s['world_id'], 'contact_count': len(events),
                        'classification': events[0]['kind'] if events else 'none',
                        'ke_before_j': .5*(s['vx_a_mps']**2 + s['vy_a_mps']**2 + s['vx_b_mps']**2 + s['vy_b_mps']**2),
                        'ke_after_j': states[-1]['total_ke_j']})
    if len(state_rows) != 117:
        raise ArithmeticError('missing samples')
    archive = {'schema_version': SCHEMA, 'worlds': scenes}
    audit = {'schema_version': SCHEMA, 'world_results': details,
             'invalid_probe_results': probes}
    dest.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix=f'.{dest.name}-staging-', dir=dest.parent))
    try:
        _write_json(temp/'scenario.json', archive)
        _write_jsonl(temp/'states.jsonl', state_rows)
        _write_jsonl(temp/'contacts.jsonl', contact_rows)
        _write_json(temp/'audit.json', audit)
        manifest = dict(schema_version=SCHEMA, frozen_protocol_commit_sha=FREEZE_COMMIT,
                        implementation_commit_sha=source_sha,
                        python_version='.'.join(str(v) for v in sys.version_info[:2]),
                        platform='linux' if sys.platform.startswith('linux') else platform.system().lower(),
                        config_sha256=digest(temp/'scenario.json'),
                        states_sha256=digest(temp/'states.jsonl'),
                        contacts_sha256=digest(temp/'contacts.jsonl'),
                        audit_sha256=digest(temp/'audit.json'))
        _write_json(temp/'manifest.json', manifest)
        if dest.exists():
            raise FileExistsError(dest)
        os.rename(temp, dest)
    finally:
        if temp.exists():
            shutil.rmtree(temp)
    return {'world_count':len(scenes), 'sample_count':len(state_rows),
            'contact_count':len(contact_rows), 'invalid_probes':len(probes)}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--source-sha', default=None)
    args = p.parse_args()
    print(canonical(produce(args.out, source_sha=args.source_sha)))
