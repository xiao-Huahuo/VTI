"""Original local dashboard with explicit composite run selection; no scientific code edits."""
import json,sys
from pathlib import Path
SRC=next(p for p in Path(__file__).resolve().parents if p.name=='src');sys.path.insert(0,str(SRC))
import progress_server as dashboard
from recovery_batch import MANIFEST
original_progress=dashboard.progress

def composite_progress(_batch=None):
    m=json.loads(MANIFEST.read_text());current=original_progress(m['batch_id']);old=original_progress(m['previous_batch']);oldrows={r['run_id']:r for r in old['sequences']};newrows={r['run_id']:r for r in current['sequences']}
    current['new_model_requests']=current['model_requests']
    current['budget_scope']='Fresh recovery runs only; exclude 2244 reused requests'
    current['sequences']=[oldrows[r['run_id']] if r['reuse'] else newrows[r['run_id']] for r in m['sequences']]
    for name,field in [('completed_sessions','sessions'),('model_requests','model_requests')]:current[name]=sum(r[field] for r in current['sequences'])
    current['completed_sequences']=sum(r['phase']=='COMPLETE' for r in current['sequences'])
    return current

dashboard.progress=composite_progress
if __name__=='__main__':dashboard.main()
