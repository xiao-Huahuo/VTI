"""One explicitly authorized development replay of the previous truncated request."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from types import SimpleNamespace
import ollama
from audit_freeze import audit, src_and_project
from backend import FrozenBackend
from execution import OUTPUT_LIMIT, verify_execution
from journal import Journal, immutable_json, sha
from transport import ReceiptTransport


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--allow-development-model-calls', action='store_true')
    args = parser.parse_args()
    if not args.allow_development_model_calls:
        raise SystemExit('Explicit development call authorization required')
    if not args.run_id.startswith('v58-dev-') or not args.run_id.replace('-', '').isalnum():
        raise ValueError('Development run ID required')
    src, project = src_and_project()
    assert audit()['status'] == 'PASS'
    execution_hash = verify_execution()
    old = src.parent/'outputs/v58-formal-mac-20260930-r02-b01-s2/raw/model_calls/00004-64d3ba7e9c820d47/prepared.json'
    request = json.loads(old.read_text())['request']
    request['options']['num_predict'] = OUTPUT_LIMIT
    root = src.parent/'outputs'/args.run_id
    journal = Journal(root, {'run_id':args.run_id, 'status':'DEVELOPMENT_QUALIFICATION',
                            'formal_data':False,'source_request_sha256':sha(old),
                            'execution_amendment_sha256':execution_hash}, resume=False)
    transport = ReceiptTransport(journal, max_requests=1,max_input_tokens=32768,
                                 max_output_tokens=OUTPUT_LIMIT,max_cost=0,
                                 output_reserve_per_request=OUTPUT_LIMIT)
    backend = FrozenBackend(journal, transport)
    backend.runtime_preflight()
    response = transport.call_once(ollama.Client(host='http://127.0.0.1:11434', timeout=1800), request, step=1)
    backend.validate_memory_json(backend.v45.response_content(response))
    count = int(response.eval_count or 0)
    if response.done_reason == 'length' or count >= 0.75 * OUTPUT_LIMIT:
        raise RuntimeError('Output completion/headroom qualification failed')
    immutable_json(root/'raw/qualification.json', {'status':'PASS', 'formal_data':False,
        'done_reason':response.done_reason,'eval_count':count,'output_limit':OUTPUT_LIMIT,
        'schema_valid':True,'headroom_gate':'eval_count < 75% of cap', 'model_calls':1})
    print(json.dumps({'status':'PASS','eval_count':count,'run_id':args.run_id}), flush=True)

if __name__ == '__main__':
    main()
