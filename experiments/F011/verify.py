"""Researcher-only independent F011 saved-evidence arithmetic oracle.

Does not import soma.f011. Recomputes full state updates, force origins,
energy and scientific status from actual CSV rather than trusting SHA alone.
"""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path
import math

DTS=(0.01,0.005,0.0025)
CASES={'A-no-contact':(0.,0.,1.),'B-isotropic':(.04,.04,1.),
       'C-directional':(.02,.08,1.),'D-mirror':(.08,.02,1.),
       'E-no-motor':(.02,.08,0.)}
COLUMNS=('step','time_s','x_a_m','x_b_m','v_a_m_s','v_b_m_s','r_m','x_cm_m',
  'internal_n','ground_a_n','ground_b_n','ground_work_j','motor_work_j',
  'kinetic_j','spring_j','impulse_residual_ns','energy_defect_j','expected_defect_j')

def close(a,b,tol=1e-9):
    if not math.isfinite(a) or not math.isfinite(b) or abs(a-b)>tol:
        raise ValueError(f'arithmetic mismatch {a!r} vs {b!r}')

def number(raw):
    try: n=float(raw)
    except (TypeError,ValueError) as e: raise ValueError('invalid numeric') from e
    if not math.isfinite(n): raise ValueError('nonfinite value')
    return n

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def rows_from(path):
    with Path(path).open(encoding='utf-8',newline='') as f:
        reader=csv.DictReader(f)
        if tuple(reader.fieldnames or ())!=COLUMNS: raise ValueError('schema differs')
        return list(reader)

def verify_raw(path,case,h,expected_rows):
    if case not in CASES or h not in DTS: raise ValueError('unregistered control')
    rows=rows_from(path)
    if len(rows)!=expected_rows: raise ValueError('missing/extra rows')
    mp,mm,amp=CASES[case]
    old=None
    for i,row in enumerate(rows):
        if row['step']!=str(i): raise ValueError('step sequence')
        z={key:(None if value=='' else number(value)) for key,value in row.items() if key!='step'}
        close(z['time_s'],i*h,1e-10)
        close(z['r_m'],z['x_b_m']-z['x_a_m'])
        close(z['x_cm_m'],(z['x_a_m']+z['x_b_m'])/2)
        close(z['kinetic_j'],(z['v_a_m_s']**2+z['v_b_m_s']**2)/2)
        close(z['spring_j'],10*(z['r_m']-.5)**2)
        if not .2-1e-12<=z['r_m']<=.8+1e-12: raise ValueError('stroke invalid')
        if i==0:
            for field in COLUMNS[8:]:
                if field not in ('kinetic_j','spring_j') and z[field] is not None:
                    raise ValueError('initial interval data')
            for field,expected in [('x_a_m',-.25),('x_b_m',.25),('v_a_m_s',0),('v_b_m_s',0)]:
                close(z[field],expected)
        else:
            sign=1 if ((i-1)//round(.6/h))%2==0 else -1
            u=amp*sign
            internal=u+20*(old['r_m']-.5)
            close(z['internal_n'],internal)
            for label,force,ground in [('a',internal,'ground_a_n'),('b',-internal,'ground_b_n')]:
                prior=old[f'v_{label}_m_s']
                free=prior+h*force
                if free>h*mp*9.81: expected=free-h*mp*9.81
                elif free< -h*mm*9.81: expected=free+h*mm*9.81
                else: expected=0.
                close(z[f'v_{label}_m_s'],expected)
                close(z[ground],(expected-free)/h)
                close(z[f'x_{label}_m'],old[f'x_{label}_m']+h*expected)
            impulse=z['v_a_m_s']+z['v_b_m_s']-old['v_a_m_s']-old['v_b_m_s']-h*(z['ground_a_n']+z['ground_b_n'])
            gw=h*(z['ground_a_n']*z['v_a_m_s']+z['ground_b_n']*z['v_b_m_s'])
            wm=h*u*(z['v_a_m_s']-z['v_b_m_s'])
            ed=(z['kinetic_j']+z['spring_j']-old['kinetic_j']-old['spring_j'])-gw-wm
            expected_defect=10*(z['r_m']-old['r_m'])**2-((z['v_a_m_s']-old['v_a_m_s'])**2+(z['v_b_m_s']-old['v_b_m_s'])**2)/2
            for field,expected in [('impulse_residual_ns',impulse),('ground_work_j',gw),('motor_work_j',wm),('energy_defect_j',ed),('expected_defect_j',expected_defect)]:
                close(z[field],expected)
            if gw>1e-11 or abs(impulse)>1e-10 or abs(ed-expected_defect)>1e-9:
                raise ValueError('passive force/momentum/energy invariant')
        old=z
    return {'center':number(rows[-1]['x_cm_m']),
            'ground_work':math.fsum(number(z['ground_work_j']) for z in rows[1:]),'rows':rows}

def verify_suite(root):
    root=Path(root)
    manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    compare=json.loads((root/'comparison.json').read_text(encoding='utf-8'))
    if manifest['schema_version']!='f011.evidence.v1' or manifest['science_stage']!='candidate_not_adopted':
        raise ValueError('provenance status false')
    if compare['research_status']!='candidate_not_adopted' or compare['schema_version']!='f011.comparison.v1':
        raise ValueError('science interpretation false')
    if tuple(compare['cases'])!=tuple(CASES) or tuple(compare['dt_s'])!=DTS:
        raise ValueError('unexpected control')
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    if actual!=set(manifest['files'])|{'manifest.json'}:raise ValueError('missing/extra artifact')
    for path,sha in manifest['files'].items():
        if digest(root/path)!=sha:raise ValueError('artifact hash')
    project=Path(__file__).resolve().parents[2]
    must=('soma/f011.py','experiments/F011/run_suite.py','experiments/F011/verify.py')
    for source in must:
        if source not in manifest['source_hashes'] or digest(project/source)!=manifest['source_hashes'][source]:
            raise ValueError('untrusted source')
    for source,sha in manifest['source_hashes'].items():
        if source.startswith('/') or '..' in Path(source).parts or not (project/source).is_file() or digest(project/source)!=sha:
            raise ValueError('source hash mismatch')
    records={}
    for case in CASES:
        records[case]={}
        for h in DTS:
            item=compare['results'][case][str(h)]
            conf=json.loads((root/case/str(h)/'config.json').read_text(encoding='utf-8'))
            mp,mm,amp=CASES[case]
            expected_conf={'schema_version':'f011.config.v1','case_id':case,'dt_s':h,
                'duration_s':9.6,'m_kg':1.0,'g_m_s2':9.81,'x_a0_m':-0.25,
                'x_b0_m':0.25,'v_a0_m_s':0.0,'v_b0_m_s':0.0,'rest_m':0.5,
                'k_n_m':20.0,'amplitude_n':amp,'period_s':1.2,
                'mu_plus':mp,'mu_minus':mm,'stroke_min_m':0.2,'stroke_max_m':0.8,
                'seed':None,'ground_semantics':'velocity_implicit_directional_coulomb_equal_static_kinetic'}
            if conf!=expected_conf:raise ValueError('mutated frozen config')
            if case=='A-no-contact':
                if item['status']!='stroke_inconclusive':raise ValueError('A negative result hidden')
                step=item['first_invalid_step']
                if item['valid_rows']!=step:raise ValueError('wrong prefix length')
                count=step
            else:
                if item['status']!='complete' or item['valid_rows']!=round(9.6/h)+1:
                    raise ValueError('incomplete nominal control')
                count=round(9.6/h)+1
            outcome=verify_raw(root/case/str(h)/'states.csv',case,h,count)
            close(outcome['center'],item['observed_center_final_m'])
            close(outcome['ground_work'],item['sum_ground_work_j'])
            records[case][h]=outcome['rows']
            if case=='A-no-contact':
                last=outcome['rows'][-1]
                r=number(last['r_m']);va=number(last['v_a_m_s']);vb=number(last['v_b_m_s'])
                sign=1 if ((step-1)//round(.6/h))%2==0 else -1
                internal=sign+20*(r-.5)
                predicted=r+h*((vb-h*internal)-(va+h*internal))
                close(item['attempted_r_m'],predicted,1e-8)
                if .2-1e-12<=predicted<=.8+1e-12:raise ValueError('faked stroke failure')
    for h in DTS:
        a=records['A-no-contact'][h];b=records['B-isotropic'][h]
        c=records['C-directional'][h];d=records['D-mirror'][h]
        e=records['E-no-motor'][h]
        expected={
          'A_valid_prefix_max_abs_com_m':max(abs(number(z['x_cm_m'])) for z in a),
          'B_max_abs_com_m':max(abs(number(z['x_cm_m'])) for z in b),
          'E_max_abs_com_m':max(abs(number(z['x_cm_m'])) for z in e),
          'CD_max_mirror_cm_m':max(abs(number(zz['x_cm_m'])+number(ww['x_cm_m'])) for zz,ww in zip(c,d)),
          'CD_max_mirror_r_m':max(abs(number(zz['r_m'])-number(ww['r_m'])) for zz,ww in zip(c,d))}
        for k,val in expected.items():
            close(val,compare['symmetry'][str(h)][k])
            if val>1e-9:raise ValueError('symmetry invalid')
    def metrics(case,h):
        x=records[case][h];s=round(1.2/h)
        X=lambda i:number(x[i]['x_cm_m'])
        return X(-1),X(-1)-X(-1-s),X(-1-s)-X(-1-2*s),number(x[-1]['r_m'])-number(x[-1-s]['r_m'])
    finest=metrics('C-directional',DTS[-1]);medium=metrics('C-directional',DTS[1])
    v,w=finest[1],finest[2]
    persistent=bool(v*w>0 and abs(v)>.001 and abs(w)>.001 and
        abs(v-w)<=.5*max(abs(v),abs(w)) and abs(finest[3])<=.01 and
        abs(finest[0]-medium[0])<=max(.002,.1*abs(finest[0])))
    statuses={'H1':'INCONCLUSIVE_due_to_preregistered_stroke_guard',
      'H2':'SUPPORTED_MODEL_ONLY' if persistent else 'NOT_SUPPORTED_OR_INCONCLUSIVE',
      'H3':'SUPPORTED_FIXED_MODEL',
      'H4':'MIRROR_AND_PASSIVITY_TEST_REQUIRED_BY_INDEPENDENT_VERIFIER'}
    if compare['persistent_directional_model_drift'] is not persistent or compare['scientific_status']!=statuses:
        raise ValueError('forged scientific result')
    return {'verified_cases':len(CASES)*len(DTS),'verified_artifacts':len(manifest['files']),
      'research_status':compare['research_status']}
