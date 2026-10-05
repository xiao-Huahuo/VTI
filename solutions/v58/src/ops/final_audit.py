"""Offline final evidence audit and independent distance-matrix randomization rebuild."""
from pathlib import Path
import sys,json,itertools,math,collections
import numpy as np
SRC=next(p for p in Path(__file__).resolve().parents if p.name=='src');sys.path.insert(0,str(SRC))
from runner import readback,frozen,OUTPUTS,DESIGN,AMENDMENT,DATASET
from journal import sha,immutable_json,utc_now
from execution import verify_execution
from backend import FrozenBackend
from retrieval_footprint import footprint
from recovery_batch import MANIFEST,mapping_check

m=json.loads(MANIFEST.read_text());design=mapping_check(m);runs=m['sequences'];controller=OUTPUTS/f"v58-{m['batch_id']}-controller";complete=json.loads((controller/'raw/batch_complete.json').read_text());assert complete['recovery_manifest_sha256']==sha(MANIFEST)
from types import SimpleNamespace
backend=FrozenBackend(SimpleNamespace(),SimpleNamespace())
records=[];checks=[];scopes=set();calls_total=ingestions=answers=0;cleanup_counts=collections.Counter();max_diff=0.0
for row in runs:
    root=OUTPUTS/row['run_id'];rb=readback(row['run_id']);assert rb['complete'] and rb['block']==row['block'] and rb['slot']==row['slot'] and rb['policy']==row['policy']
    info=json.loads((root/'raw/identity.json').read_text());assert info['scope'] not in scopes;scopes.add(info['scope'])
    assert info['v58_design_sha256']==sha(DESIGN) and info['amendment_sha256']==sha(AMENDMENT) and info['dataset_sha256']==sha(DATASET) and info['execution_amendment_sha256']==verify_execution()
    assert all(sha(SRC/n)==h for n,h in info['code_sha256'].items())
    assert info['model_identity']==json.loads((OUTPUTS/f"v58-{m['previous_batch']}-controller/raw/batch_identity.json").read_text())['runtime']
    assert not list(root.glob('raw/failures/*.json'))
    calls=list(root.glob('raw/model_calls/*/dispatched.json'));assert len(calls)==187;calls_total+=len(calls)
    for dispatched in calls:
        d=dispatched.parent;response=json.loads((d/'response.json').read_text());assert response.get('done_reason')!='length';assert (d/'raw_http_response.bin').exists()
        request=json.loads((d/'prepared.json').read_text())['request'];assert request['options']['num_predict']==8192 and request['options']['num_ctx']==32768
    operations=[json.loads(f.read_text()) for f in root.glob('raw/operations/[0-9]*.json')];assert len(operations)==190
    ingestions+=sum(o['kind']=='ingest' for o in operations);answers+=sum(o['kind']=='observe' for o in operations)
    for f in root.glob('raw/cleanup/*.json'):
        c=json.loads(f.read_text());assert c['policy']==row['policy'];assert c['after_native_vectors']['count']==0 and c['after_native_backend']['count']==0
        assert c['after_cleanup_vectors']['count']==0 and c['after_cleanup_backend']['count']==0
        if row['policy']=='V':assert c['after_cleanup_messages']['count']==0
        else:assert c['after_cleanup_messages']['count']>0
        cleanup_counts[row['policy']]+=1
    for pos,target in enumerate(row['order'],1):
        f=root/f'raw/observations/trial-{pos:02d}.json';o=json.loads(f.read_text());assert o['footprint_dtype']=='float32' and o['question_id']==next(c['question_id'] for c in design['cases'] if c['symbol']==target)
        assert isinstance(o['answer'],str) and o['answer'].strip() and isinstance(o['reference_answer'],str)
        rows=backend.v45.normalize_results(o['search_raw']);texts=[str(x.get('memory') or x.get('text') or x.get('data') or '') for x in rows]
        assert texts==o['retrieval_texts'] and backend.v45.text_hashes_in_order(rows)==o['retrieval_ordered_hashes']
        rebuilt=footprint(texts,backend._embed);old=np.asarray(o['footprint'],dtype=np.float32);diff=float(np.max(np.abs(old-rebuilt)));max_diff=max(max_diff,diff);assert np.array_equal(old,rebuilt),('Footprint reconstruction drift',row['run_id'],pos,diff)
        if pos>1:records.append({'block':row['block'],'slot':row['slot'],'target':target,'position':pos,'v':old.astype(np.float64)})
    checks.append({'run_id':row['run_id'],'readback':rb,'identity_sha256':sha(root/'raw/identity.json'),'complete_sha256':sha(root/'raw/sequence_complete.json')})
assert ingestions==4392 and answers==96 and calls_total==4488 and cleanup_counts=={'N':36,'V':36}
# Independent calculation: precompute distances for six observations per target-position,
# assign policy by original block slot XOR swap, and recompute three-pair means.
cells={}
for target in 'ABCD':
 for pos in (2,3,4):
    group=[r for r in records if r['target']==target and r['position']==pos];assert len(group)==6
    dist=np.zeros((6,6),dtype=np.float64)
    for i,j in itertools.combinations(range(6),2):dist[i,j]=dist[j,i]=float(np.sqrt(np.sum((group[i]['v']-group[j]['v'])**2,dtype=np.float64)))
    cells[target,pos]=(group,dist)
def calc(bits):
    values={'N':[],'V':[]}
    for group,dist in cells.values():
        groups={'N':[],'V':[]}
        for i,r in enumerate(group):
            block=design['blocks'][r['block']-1];policy=block[f"slot{r['slot']}"]
            if bits[r['block']-1]:policy='V' if policy=='N' else 'N'
            groups[policy].append(i)
        for policy,indices in groups.items():
            assert len(indices)==3;values[policy].append(math.fsum(dist[i,j] for i,j in itertools.combinations(indices,2))/3)
    n=math.fsum(values['N'])/12;v=math.fsum(values['V'])/12;return n,v,n-v
observed=calc([0]*12);distribution=[calc(bits)[2] for bits in itertools.product((0,1),repeat=12)];tail=sum(x>=observed[2]-1e-12 for x in distribution)
result_path=OUTPUTS/f"v58-{m['batch_id']}-analysis/processed/exact_randomization.json";result=json.loads(result_path.read_text());assert abs(observed[2]-result['effect'])<1e-12 and tail==result['right_tail_count'];assert max(abs(a-b) for a,b in zip(distribution,result['all_assignment_effects']))<1e-12
receipt={'checked_at_utc':utc_now(),'status':'PASS','recovery_manifest_sha256':sha(MANIFEST),'completion':complete,'selected_sequences':24,'readback_checkpoints':sum(r['readback']['checkpoints'] for r in checks),'unique_scopes':24,'ingestions':ingestions,'answers':answers,'model_requests':calls_total,'cleanup_boundaries':dict(cleanup_counts),'footprints_rebuilt':96,'footprint_max_abs_difference':max_diff,'independent_native_dispersion':observed[0],'independent_verified_dispersion':observed[1],'independent_effect':observed[2],'independent_right_tail_count':tail,'independent_p_value':tail/4096,'assignments':4096,'statistical_result_sha256':sha(result_path),'all_selected_run_checks':checks,'raw_modified':False,'new_model_calls':0,'correctness_score':'NOT_SCORED_PER_USER_DECISION','excluded_failed_run':m['excluded_run_id']}
immutable_json(backend.project/'docs/v58/FINAL_EVIDENCE_AUDIT_20261005.json',receipt)
print(json.dumps({k:v for k,v in receipt.items() if k!='all_selected_run_checks'},ensure_ascii=False))
