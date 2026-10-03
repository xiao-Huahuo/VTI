"""Recover controller after verified completed worker's native teardown abort only.
Never retry an incomplete/uncertain scientific operation; original runner/source stays fixed.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

SRC = next(p for p in Path(__file__).resolve().parents if p.name == 'src')
sys.path.insert(0, str(SRC))
from audit_freeze import audit, src_and_project
from journal import immutable_json, sha, utc_now
from runner import readback


def teardown_abort(text):
    return ('recursive_mutex lock failed: Invalid argument' in text and
            ('SIGABRT' in text or 'Signals.SIGABRT' in text) and
            '"status": "COMPLETE"' in text)


def verify_completed_failure(outputs, batch_id, log):
    controller = outputs/f'v58-{batch_id}-controller'
    status = json.loads((controller/'control/status.json').read_text())
    if status.get('phase') != 'FAILED' or (controller/'control/pause.request.json').exists():
        raise RuntimeError('Not an eligible failed controller, or user pause pending')
    if not teardown_abort(log.read_text()):
        raise RuntimeError('Failure is not known post-completion native teardown abort')
    active = status['active_run_id']
    if not active.startswith(f'v58-{batch_id}-b'):
        raise RuntimeError('Unexpected active run')
    result = readback(active)
    if not result['complete']:
        raise RuntimeError('Incomplete operation: NEVER auto retry')
    batch = json.loads((controller/'raw/batch_identity.json').read_text())
    info = json.loads((outputs/active/'raw/identity.json').read_text())
    if info['code_sha256'] != batch['source_sha256'] or any(
            sha(SRC/name) != h for name,h in batch['source_sha256'].items()):
        raise RuntimeError('Original source identity drift')
    if info['model_identity'] != batch['runtime'] or info['budget_limits']['max_cost'] != batch['global_budget']['max_cost']:
        raise RuntimeError('Identity/budget mismatch')
    return {'at_utc':utc_now(),'status':'VERIFIED_POST_COMPLETION_TEARDOWN_ABORT',
            'active_run_id':active,'readback':result,'log_sha256':sha(log),
            'action':'Restart original full controller; completed sequence skipped, no request resend'}


def verify_safe_pause(outputs, batch_id):
    controller = outputs/f'v58-{batch_id}-controller'
    status = json.loads((controller/'control/status.json').read_text())
    if status.get('phase') != 'PAUSED':
        raise RuntimeError('User-authorized resume requires a safe paused controller')
    active = status['active_run_id']
    if not active.startswith(f'v58-{batch_id}-b'):
        raise RuntimeError('Unexpected active run')
    result = readback(active)  # Rejects pending operations/uncertain calls.
    batch = json.loads((controller/'raw/batch_identity.json').read_text())
    info = json.loads((outputs/active/'raw/identity.json').read_text())
    if info['code_sha256'] != batch['source_sha256'] or any(
            sha(SRC/name) != h for name,h in batch['source_sha256'].items()):
        raise RuntimeError('Original source identity drift')
    return {'at_utc':utc_now(),'status':'USER_AUTHORIZED_VERIFIED_SAFE_PAUSE',
            'active_run_id':active,'readback':result,
            'action':'Resume original controller under unchanged budget; no request resend'}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--batch-id', required=True)
    parser.add_argument('--previous-log', type=Path)
    parser.add_argument('--resume-paused', action='store_true')
    parser.add_argument('--allow-model-calls', action='store_true')
    args=parser.parse_args()
    if not args.allow_model_calls:
        raise SystemExit('Formal authorization required')
    if not args.batch_id.replace('-','').isalnum():
        raise ValueError('Invalid batch id')
    _,project=src_and_project();outputs=SRC.parent/'outputs'
    processes=subprocess.check_output(['ps','-axo','args='],text=True)
    if any('/src/runner.py full ' in x for x in processes.splitlines()):
        raise RuntimeError('Existing runner; no duplicate')
    os.environ.update(MEM0_TELEMETRY='false',ANONYMIZED_TELEMETRY='False',HF_HUB_OFFLINE='1',
        FASTEMBED_CACHE_PATH=str(project/'history/pre_v58_root_20260930/.runtime/fastembed-cache'))
    if audit()['status']!='PASS':raise RuntimeError('Freeze audit failed')
    if args.resume_paused:
        evidence=verify_safe_pause(outputs,args.batch_id)
    else:
        if args.previous_log is None:raise RuntimeError('Previous teardown log required')
        evidence=verify_completed_failure(outputs,args.batch_id,args.previous_log)
    suffix = '-resume-' + utc_now().replace(':','').replace('.','').replace('+','') if args.resume_paused else ''
    events=outputs/f'v58-{args.batch_id}-teardown-supervision{suffix}'
    events.mkdir()
    immutable_json(events/'initial_recovery.json',evidence)
    budget=json.loads((outputs/f'v58-{args.batch_id}-controller/raw/batch_identity.json').read_text())['global_budget']
    cmd=[sys.executable,'-u',str(SRC/'runner.py'),'full','--batch-id',args.batch_id,'--allow-model-calls']
    for key,value in budget.items():cmd += ['--'+key.replace('_','-'),str(value)]
    if args.resume_paused:cmd.append('--resume-paused')
    recovered=set() if args.resume_paused else {evidence['active_run_id']}
    # Bound by 24 distinct completed sequences, never replay an incomplete operation.
    for attempt in range(25):
        log=events/f'controller-{attempt:02d}.log'
        immutable_json(events/f'start-{attempt:02d}.json',{'at_utc':utc_now(),'command':cmd})
        with log.open('xb') as stream:
            process=subprocess.Popen(cmd,stdout=stream,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
            immutable_json(events/f'process-{attempt:02d}.json',{'at_utc':utc_now(),'runner_pid':process.pid})
            code=process.wait()
        immutable_json(events/f'exit-{attempt:02d}.json',{'at_utc':utc_now(),'returncode':code})
        if code in (0,75):return
        evidence=verify_completed_failure(outputs,args.batch_id,log)
        if evidence['active_run_id'] in recovered:
            raise RuntimeError('Repeated failure of same complete sequence; no blind restart')
        recovered.add(evidence['active_run_id'])
        immutable_json(events/f'recovery-{attempt:02d}.json',evidence)
    raise RuntimeError('Recovery bound exhausted')

if __name__=='__main__':main()
