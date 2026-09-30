from __future__ import annotations

import json
import argparse
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

SRC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC))
from control import request_pause, clear_pause
from journal import Journal, sha
import runner
from control import SafePause, STOP_REQUESTED

CHILD = r'''
import sys, asyncio, time, json
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, sys.argv[1])
import runner, backend
root=Path(sys.argv[2]); mode=sys.argv[3]
runner.OUTPUTS=root
runner.frozen=lambda:{'cases':[{'symbol':s,'question_id':s,'sessions':1} for s in 'ABCD']}
runner.selected=lambda *a:({'block':1,'order':'ABCD'},'N')
runner.operation_plan=lambda *a:[{'kind':'ingest','trial':1,'symbol':'A','session':1},{'kind':'ingest','trial':2,'symbol':'B','session':1}]
runner.runtime_preflight=lambda:{'model':'FAKE'}
runner.identity=lambda *a:{'run_id':'v58-pause-test','scope':'same','model':'FAKE','budget':'fixed'}
class FakeBackend:
 def __init__(self,journal,transport): self.journal=journal
 def runtime_preflight(self): return {}
 def case(self,*a): return SimpleNamespace(sessions=[None])
 async def ingest(self,state,scope,session,step):
  with (root/'calls.jsonl').open('a') as f:f.write(json.dumps({'step':step})+'\n')
  (root/'active.fake').write_text(str(step))
  await asyncio.to_thread(time.sleep,0.7)
  (state/'memory.txt').write_text(str(step))
  return {'fake':True}
backend.FrozenBackend=FakeBackend
sys.argv=['runner.py','resume' if mode=='resume' else 'single-sequence','--run-id','v58-pause-test','--block','1','--slot','1','--max-requests','4','--max-input-tokens','131072','--max-output-tokens','8192','--max-cost','0','--allow-model-calls']
if mode=='resume':sys.argv.append('--resume-paused')
runner.main()
'''


class PauseControlTests(unittest.TestCase):
    def test_batch_stops_after_worker_pause_and_resumes_same_sequence_first(self):
        with tempfile.TemporaryDirectory() as temporary:
            outputs = Path(temporary)
            runtime = {"model": "FAKE"}
            args = argparse.Namespace(batch_id="pausedbatch", max_requests=24,
                                      max_input_tokens=24*32768, max_output_tokens=24*2048,
                                      max_cost=0, resume_paused=False)
            sources = {p.name: runner.sha(p) for p in runner.SRC.glob("*.py")}
            completed = set()
            commands = []
            STOP_REQUESTED.clear()

            def start(command, check):
                run_id = command[command.index("--run-id")+1]
                commands.append((command[2], run_id))
                raw = outputs / run_id / "raw"
                raw.mkdir(parents=True, exist_ok=True)
                budget = {"max_requests": int(command[command.index("--max-requests")+1]),
                          "max_input_tokens": int(command[command.index("--max-input-tokens")+1]),
                          "max_output_tokens": int(command[command.index("--max-output-tokens")+1]),
                          "max_cost": 0}
                info = {"code_sha256": sources, "v58_design_sha256": runner.sha(runner.DESIGN),
                        "amendment_sha256": runner.sha(runner.AMENDMENT),
                        "dataset_sha256": runner.sha(runner.DATASET), "model_identity": runtime,
                        "budget_limits": budget}
                (raw / "identity.json").write_text(json.dumps(info))
                if len(commands) == 1:
                    return SimpleNamespace(returncode=75)
                completed.add(run_id)
                calls = raw / "model_calls/one"
                calls.mkdir(parents=True)
                (calls / "dispatched.json").write_text('{}')
                (calls / "response.json").write_text('{}')
                return SimpleNamespace(returncode=0)

            def rb(run_id):
                tail = run_id.rsplit('-',2)
                return {"complete": run_id in completed, "block": int(tail[-2][1:]), "slot": int(tail[-1][1:])}

            with patch.object(runner,"OUTPUTS",outputs), patch.object(runner,"frozen",return_value={}), \
                 patch.object(runner,"runtime_preflight",return_value=runtime), \
                 patch.object(runner.subprocess,"run",side_effect=start), patch.object(runner,"readback",side_effect=rb):
                with self.assertRaises(SafePause):
                    runner.full(args)
                self.assertEqual(len(commands),1)
                args.resume_paused=True
                runner.full(args)
            self.assertEqual(commands[0][1],commands[1][1])
            self.assertEqual(commands[1][0],'resume')
            self.assertEqual(len(completed),24)

    def test_signal_during_request_commits_once_then_resumes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            process = subprocess.Popen([sys.executable, "-c", CHILD, str(SRC), str(root), "new"],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            deadline = time.monotonic() + 10
            while not (root / "active.fake").exists() and process.poll() is None and time.monotonic() < deadline:
                time.sleep(0.02)
            self.assertTrue((root / "active.fake").exists())
            process.terminate()
            stdout, stderr = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 75, (stdout, stderr))
            run = root / "v58-pause-test"
            info = json.loads((run / "raw/identity.json").read_text())
            journal = Journal(run, info, resume=True)
            self.assertEqual(journal.readback()["checkpoints"], 2)
            self.assertFalse((run / "raw/failures").exists())
            before = sha(journal.checkpoint_path(1) / "_checkpoint.json")
            resumed = subprocess.run([sys.executable, "-c", CHILD, str(SRC), str(root), "resume"],
                                     capture_output=True, text=True, timeout=10)
            self.assertEqual(resumed.returncode, 0, (resumed.stdout, resumed.stderr))
            self.assertEqual(sha(journal.checkpoint_path(1) / "_checkpoint.json"), before)
            self.assertEqual([json.loads(line)["step"] for line in (root / "calls.jsonl").read_text().splitlines()], [1, 2])
            self.assertEqual(journal.readback()["checkpoints"], 3)

    def test_pause_request_is_idempotent_and_archived_on_resume(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "raw").mkdir()
            first = request_pause(root)
            self.assertEqual(request_pause(root), first)
            clear_pause(root)
            self.assertFalse((root / "control/pause.request.json").exists())
            self.assertEqual(len(list((root / "control/history").glob("resumed-*.json"))), 1)
