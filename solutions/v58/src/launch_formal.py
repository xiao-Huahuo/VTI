"""Detached amended formal launch after saved development qualification; no retries."""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from audit_freeze import audit, src_and_project
from backend import FrozenBackend
from execution import EXECUTION_AMENDMENT, OUTPUT_LIMIT, verify_execution
from journal import immutable_json, sha, utc_now
from machine_metrics import collect
from runner import runtime_preflight


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch-id', required=True)
    parser.add_argument('--allow-model-calls', action='store_true')
    args = parser.parse_args()
    if not args.allow_model_calls:
        raise SystemExit('Explicit formal authorization required')
    if not args.batch_id.replace('-', '').isalnum():
        raise ValueError('Simple batch ID required')
    src, project = src_and_project()
    outputs = src.parent/'outputs'
    if (outputs/f'v58-{args.batch_id}-controller').exists():
        raise RuntimeError('Fresh batch only; use runner full with original budget for a safe resume')
    processes = subprocess.check_output(['ps','-axo','args='],text=True)
    if any('/src/runner.py full ' in line for line in processes.splitlines()):
        raise RuntimeError('Existing full runner; no duplicate launch')
    config = json.loads(EXECUTION_AMENDMENT.read_text())
    verify_execution()
    qualification_root = outputs/'v58-dev-output-20261001'
    gate = json.loads((qualification_root/'raw/qualification.json').read_text())
    identity = json.loads((qualification_root/'raw/identity.json').read_text())
    if gate['status'] != 'PASS' or gate['output_limit'] != OUTPUT_LIMIT or identity['execution_amendment_sha256'] != sha(EXECUTION_AMENDMENT):
        raise RuntimeError('Missing matching output qualification')
    os.environ.update(MEM0_TELEMETRY='false',ANONYMIZED_TELEMETRY='False',HF_HUB_OFFLINE='1',
        FASTEMBED_CACHE_PATH=str(project/'history/pre_v58_root_20260930/.runtime/fastembed-cache'))
    if audit()['status'] != 'PASS':
        raise RuntimeError('Freeze audit failed')
    runtime = runtime_preflight()
    backend = FrozenBackend(SimpleNamespace(),SimpleNamespace())
    backend.runtime_preflight()
    with tempfile.TemporaryDirectory() as temp:
        store = backend._store(Path(temp), 'v58_prelaunch_no_calls')
        backend.v45.close_memory(store._memory)
    launch = outputs/f'v58-{args.batch_id}-launch'
    launch.mkdir()
    immutable_json(launch/'prelaunch.json', {'at_utc':utc_now(),'runtime':runtime,
        'execution_amendment_sha256':sha(EXECUTION_AMENDMENT),
        'qualification_sha256':sha(qualification_root/'raw/qualification.json'),
        'machine':collect(project),'formal_budget':config,
        'source_sha256':{p.name:sha(p) for p in src.glob('*.py')}})
    command = [sys.executable,'-u',str(src/'runner.py'),'full','--batch-id',args.batch_id,'--allow-model-calls']
    for option in ['max_requests','max_input_tokens','max_output_tokens','max_cost']:
        command += ['--'+option.replace('_','-'),str(config[option])]
    with (launch/'runner.log').open('xb') as log:
        proc = subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,
            env=os.environ.copy(),start_new_session=True)
    sleep_guard = subprocess.Popen(['/usr/bin/caffeinate','-i','-s','-w',str(proc.pid)],
        stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
    receipt = {'at_utc':utc_now(),'batch_id':args.batch_id,'runner_pid':proc.pid,
        'caffeinate_pid':sleep_guard.pid,'command':command}
    immutable_json(launch/'launch.json',receipt)
    print(json.dumps(receipt),flush=True)

if __name__ == '__main__':
    main()
