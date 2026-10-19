"""Run frozen F011 model experiment, save raw negative controls and identical replay."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from soma.f011 import Config, CASES, DTS, COLUMNS, StrokeLimitError, simulate, measurements
from experiments.F011.verify import verify_suite

def dumps(data):
    return json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n'

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def build_one(folder):
    results={}
    traces={}
    for case in CASES:
        results[case]={}
        for h in DTS:
            config=Config(case,h)
            dst=folder/case/str(h)
            dst.mkdir(parents=True)
            (dst/'config.json').write_text(dumps(config.as_dict()),encoding='utf-8')
            try:
                rows=simulate(config)
                meta={'status':'complete','valid_rows':len(rows)}
                meta.update(measurements(rows))
            except StrokeLimitError as error:
                rows=error.valid_rows
                meta={'status':'stroke_inconclusive','valid_rows':len(rows),
                  'first_invalid_step':error.step,'attempted_r_m':error.attempted_r}
            with (dst/'states.csv').open('w',encoding='utf-8',newline='') as f:
                w=csv.DictWriter(f,fieldnames=COLUMNS,lineterminator='\n')
                w.writeheader();w.writerows(rows)
            meta['observed_center_final_m']=rows[-1]['x_cm_m']
            meta['sum_ground_work_j']=sum(x['ground_work_j'] for x in rows[1:])
            results[case][str(h)]=meta
            traces[(case,h)]=rows
    symmetry={}
    for h in DTS:
        a=traces['A-no-contact',h];b=traces['B-isotropic',h]
        c=traces['C-directional',h];d=traces['D-mirror',h]
        e=traces['E-no-motor',h]
        symmetry[str(h)]={
          'A_valid_prefix_max_abs_com_m':max(abs(r['x_cm_m']) for r in a),
          'B_max_abs_com_m':max(abs(r['x_cm_m']) for r in b),
          'E_max_abs_com_m':max(abs(r['x_cm_m']) for r in e),
          'CD_max_mirror_cm_m':max(abs(cc['x_cm_m']+dd['x_cm_m']) for cc,dd in zip(c,d)),
          'CD_max_mirror_r_m':max(abs(cc['r_m']-dd['r_m']) for cc,dd in zip(c,d)),
        }
    medium=results['C-directional'][str(DTS[1])]
    finest=results['C-directional'][str(DTS[-1])]
    last=finest.get('last_period_m',0.0)
    prev=finest.get('penultimate_period_m',0.0)
    persistent=bool(finest['status']=='complete' and
        last*prev>0 and abs(last)>.001 and abs(prev)>.001 and
        abs(last-prev)<=.5*max(abs(last),abs(prev)) and
        abs(finest['last_period_stroke_return_m'])<=.01 and
        abs(medium['center_final_m']-finest['center_final_m'])<=max(.002,.1*abs(finest['center_final_m'])))
    scientific={'H1':'INCONCLUSIVE_due_to_preregistered_stroke_guard',
      'H2':'SUPPORTED_MODEL_ONLY' if persistent else 'NOT_SUPPORTED_OR_INCONCLUSIVE',
      'H3':'SUPPORTED_FIXED_MODEL',
      'H4':'MIRROR_AND_PASSIVITY_TEST_REQUIRED_BY_INDEPENDENT_VERIFIER'}
    comparison={'schema_version':'f011.comparison.v1','research_status':'candidate_not_adopted',
      'scientific_status':scientific,
      'case_warning':'A exceeds preregistered stroke before T; retain partial raw negative, do NOT assert A completed',
      'cases':list(CASES),'dt_s':list(DTS),'results':results,
      'symmetry':symmetry,'persistent_directional_model_drift':persistent}
    (folder/'comparison.json').write_text(dumps(comparison),encoding='utf-8')
    repo=Path(__file__).resolve().parents[2]
    sources=('soma/f011.py','experiments/F011/run_suite.py','experiments/F011/verify.py',
      'topics/F011-grounded-internal-drive/SPEC.md','experiments/F011/PLAN.md')
    source_hashes={p:digest(repo/p) for p in sources if (repo/p).is_file()}
    files={p.relative_to(folder).as_posix():digest(p) for p in sorted(folder.rglob('*')) if p.is_file()}
    manifest={'schema_version':'f011.evidence.v1','science_stage':'candidate_not_adopted',
      'source_hashes':source_hashes,'files':files}
    (folder/'manifest.json').write_text(dumps(manifest),encoding='utf-8')
    return comparison

def generate(output_dir):
    out=Path(output_dir).resolve()
    if out.exists():raise FileExistsError('Existing evidence must not be overwritten')
    out.parent.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='.f011-stage-',dir=out.parent))
    try:
        result=build_one(stage)
        verify_suite(stage)
        stage.rename(out)
        return result
    finally:
        if stage.exists():shutil.rmtree(stage)

def run_pair(first,second):
    p=Path(first).resolve();q=Path(second).resolve()
    if p==q or p in q.parents or q in p.parents or p.exists() or q.exists():
        raise ValueError('outputs must be new disjoint directories')
    generated=[]
    try:
        result=generate(p);generated.append(p)
        generate(q);generated.append(q)
        a={x.relative_to(p).as_posix():x.read_bytes() for x in p.rglob('*') if x.is_file()}
        b={x.relative_to(q).as_posix():x.read_bytes() for x in q.rglob('*') if x.is_file()}
        if a!=b:raise ValueError('nonreproducible evidence')
        return {'result':result,'byte_identical_files':len(a)}
    except Exception:
        for path in reversed(generated):
            if path.exists():shutil.rmtree(path)
        raise

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output-dir',required=True)
    p.add_argument('--replay-output-dir',required=True)
    args=p.parse_args()
    result=run_pair(Path(args.output_dir),Path(args.replay_output_dir))
    print(dumps({'scientific_status':result['result']['scientific_status'],
       'identical_evidence_files':result['byte_identical_files']}))

if __name__=='__main__':
    main()
