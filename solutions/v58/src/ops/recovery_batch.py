"""Explicit composite continuation: verified complete runs plus fresh replacement runs."""
from __future__ import annotations
import argparse,json,os,subprocess,sys
from pathlib import Path
SRC=next(p for p in Path(__file__).resolve().parents if p.name=='src');sys.path.insert(0,str(SRC))
from runner import frozen,readback,runtime_preflight,OUTPUTS,DESIGN,AMENDMENT,DATASET
from journal import immutable_json,sha,utc_now
from control import requested,status,PAUSED_EXIT
from execution import verify_execution
from teardown_supervisor import teardown_abort

MANIFEST=SRC.parent/'RECOVERY_MANIFEST_20261003.json'

def mapping_check(manifest):
    design=frozen();rows=manifest['sequences']
    if [(r['block'],r['slot']) for r in rows] != [(b,s) for b in range(1,13) for s in (1,2)]:
        raise RuntimeError('Must preserve all 24 frozen slots exactly')
    if len({r['run_id'] for r in rows}) != 24:raise RuntimeError('Duplicate run selection')
    for row in rows:
        expected=f"v58-{manifest['previous_batch'] if row['reuse'] else manifest['batch_id']}-b{row['block']:02d}-s{row['slot']}"
        if row['run_id']!=expected:raise RuntimeError('Unexpected selected run ID')
        b=design['blocks'][row['block']-1]
        if row['policy']!=b[f"slot{row['slot']}"] or row['order']!=b['order']:
            raise RuntimeError('Frozen design mismatch')
        if row['reuse']:
            result=readback(row['run_id']);assert result['complete']
            identity=OUTPUTS/row['run_id']/'raw/identity.json'
            if sha(identity)!=row['identity_sha256']:raise RuntimeError('Reuse identity drift')
            info=json.loads(identity.read_text())
            if info['execution_amendment_sha256']!=verify_execution() or any(sha(SRC/n)!=h for n,h in info['code_sha256'].items()):
                raise RuntimeError('Reuse source/execution mismatch')
            if info['block']!=row['block'] or info['slot']!=row['slot'] or info['policy']!=row['policy']:
                raise RuntimeError('Reuse slot mismatch')
    return design

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--allow-model-calls',action='store_true');parser.add_argument('--resume-paused',action='store_true');parser.add_argument('--audit-only',action='store_true');parser.add_argument('--aggregate',action='store_true');args=parser.parse_args()
    m=json.loads(MANIFEST.read_text());design=mapping_check(m);batch=m['batch_id'];controller=OUTPUTS/f'v58-{batch}-controller'
    if args.audit_only:print(json.dumps({'status':'PASS','slots':24,'reused':12}));return
    if args.aggregate:
        from statistics import exact_randomization
        records=[];hashes={}
        for row in m['sequences']:
            result=readback(row['run_id']);assert result['complete'];hashes[row['run_id']]=[]
            for pos,target in enumerate(row['order'],1):
                f=OUTPUTS/row['run_id']/f'raw/observations/trial-{pos:02d}.json';o=json.loads(f.read_text());hashes[row['run_id']].append(sha(f));records.append({'block':row['block'],'slot':row['slot'],'position':pos,'target':target,'predecessor':row['order'][pos-2] if pos>1 else None,'footprint':o['footprint']})
        result=exact_randomization(records,design['blocks']);result['run_ids']=[r['run_id'] for r in m['sequences']];result['source_observation_sha256']=hashes;out=OUTPUTS/f'v58-{batch}-analysis';out.mkdir();immutable_json(out/'raw/source_manifest.json',{'recovery_manifest_sha256':sha(MANIFEST),'source_observation_sha256':hashes});immutable_json(out/'processed/exact_randomization.json',result);return
    if not args.allow_model_calls:raise RuntimeError('Explicit formal authorization required')
    runtime=runtime_preflight();old=json.loads((OUTPUTS/f"v58-{m['previous_batch']}-controller/raw/batch_identity.json").read_text());assert runtime==old['runtime']
    identity={'batch_id':batch,'global_budget':m['remaining_budget'],'recovery_manifest_sha256':sha(MANIFEST),'runtime':runtime,'source_sha256':old['source_sha256'],'execution_amendment_sha256':verify_execution()}
    if not controller.exists():
        controller.mkdir();immutable_json(controller/'raw/batch_identity.json',identity)
    else:
        if json.loads((controller/'raw/batch_identity.json').read_text())!=identity:raise RuntimeError('Recovery identity drift')
    if requested(controller):
        if not args.resume_paused:return
        from control import clear_pause
        clear_pause(controller)
    for row in m['sequences']:
        if row['reuse']:continue
        if requested(controller):status(controller,phase='PAUSED',batch_id=batch);return
        root=OUTPUTS/row['run_id'];existing=root.exists()
        if existing and readback(row['run_id'])['complete']:continue
        consumed={'max_requests':0,'max_input_tokens':0,'max_output_tokens':0,'max_cost':0}
        for r in m['sequences']:
            if r['reuse']:continue
            for f in (OUTPUTS/r['run_id']).glob('raw/model_calls/*/dispatched.json'):
                consumed['max_requests']+=1;response=f.parent/'response.json';q=json.loads(response.read_text()) if response.exists() else {};consumed['max_input_tokens']+=max(int(q.get('prompt_eval_count') or 0),32768);consumed['max_output_tokens']+=max(int(q.get('eval_count') or 0),8192)
        limits=json.loads((root/'raw/identity.json').read_text())['budget_limits'] if existing else {k:v-consumed[k] for k,v in m['remaining_budget'].items()}
        if any(consumed[k]>v for k,v in m['remaining_budget'].items()):raise RuntimeError('Recovery budget exhausted')
        cmd=[sys.executable,'-u',str(SRC/'runner.py'),'resume' if existing else 'single-sequence','--block',str(row['block']),'--slot',str(row['slot']),'--batch-id',batch,'--run-id',row['run_id'],'--allow-model-calls']
        for k,v in limits.items():cmd += ['--'+k.replace('_','-'),str(v)]
        if args.resume_paused:cmd.append('--resume-paused')
        status(controller,phase='RUNNING',batch_id=batch,active_run_id=row['run_id'])
        attempt=0
        while (controller/f'logs/{row["block"]:02d}-{row["slot"]}-{attempt}.log').exists():attempt+=1
        log=controller/f'logs/{row["block"]:02d}-{row["slot"]}-{attempt}.log';log.parent.mkdir(exist_ok=True)
        with log.open('xb') as f:code=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT).returncode
        if code==PAUSED_EXIT:status(controller,phase='PAUSED',batch_id=batch,active_run_id=row['run_id']);return
        if code!=0:
            if not teardown_abort(log.read_text()) or not readback(row['run_id'])['complete']:
                status(controller,phase='FAILED',batch_id=batch,active_run_id=row['run_id']);raise RuntimeError('Failed operation preserved; no retry')
            immutable_json(controller/f'raw/teardown-{row["block"]:02d}-{row["slot"]}.json',{'log_sha256':sha(log),'readback':readback(row['run_id'])})
        assert readback(row['run_id'])['complete']
    if (controller/'raw/batch_complete.json').exists():
        status(controller,phase='COMPLETE',batch_id=batch);return
    immutable_json(controller/'raw/batch_complete.json',{'at_utc':utc_now(),'recovery_manifest_sha256':sha(MANIFEST),'sequences':24});status(controller,phase='COMPLETE',batch_id=batch)

if __name__=='__main__':main()
