"""Post-completion descriptive report tables; no new model calls or primary tests."""
from pathlib import Path
import sys,json,collections,numpy as np
SRC=next(p for p in Path(__file__).resolve().parents if p.name=='src');sys.path.insert(0,str(SRC))
from journal import sha,immutable_json,utc_now
from recovery_batch import MANIFEST
m=json.loads(MANIFEST.read_text());p=SRC.parent/'outputs'/f"v58-{m['batch_id']}-analysis/processed/exact_randomization.json";s=json.loads(p.read_text());d={(r['policy'],r['target'],r['position']):r['dispersion'] for r in s['per_cell_statistics']};by_target=[];by_position=[];cells=[]
for t in 'ABCD':
 n=sum(d['N',t,p] for p in (2,3,4))/3;v=sum(d['V',t,p] for p in (2,3,4))/3;by_target.append({'target':t,'N':n,'V':v,'delta':n-v,'relative_percent':100*(n-v)/n})
 for pos in (2,3,4):cells.append({'target':t,'position':pos,'N':d['N',t,pos],'V':d['V',t,pos],'delta':d['N',t,pos]-d['V',t,pos]})
for pos in (2,3,4):
 n=sum(d['N',t,pos] for t in 'ABCD')/4;v=sum(d['V',t,pos] for t in 'ABCD')/4;by_position.append({'position':pos,'N':n,'V':v,'delta':n-v})
mechanism=[]
for row in m['sequences']:
 r=SRC.parent/'outputs'/row['run_id']
 for f in r.glob('checkpoints/[0-9]*/_checkpoint.json'):
  c=json.loads(f.read_text());op=c.get('receipt',{}).get('operation',{})
  if op.get('kind')=='ingest' and op.get('session')==1:
   records=c['receipt']['result']['prompt_records'];assert len(records)==1;rec=records[0];mechanism.append({'run_id':row['run_id'],'policy':row['policy'],'trial':op['trial'],'last_k_nonempty':rec['last_k_nonempty'],'last_k_bytes':rec['last_k_bytes'],'checkpoint_sha256':sha(f)})
summary=[]
for policy in ('N','V'):
 for initial in (True,False):
  rows=[x for x in mechanism if x['policy']==policy and (x['trial']==1)==initial];summary.append({'policy':policy,'phase':'initial' if initial else 'post_cleanup','n':len(rows),'nonempty':sum(x['last_k_nonempty'] for x in rows),'min_bytes':min(x['last_k_bytes'] for x in rows),'max_bytes':max(x['last_k_bytes'] for x in rows)})
counts,edges=np.histogram(s['all_assignment_effects'],bins=np.linspace(-.18,.18,19));out=SRC.parent/'outputs/v58-report-20261006/processed';out.mkdir(parents=True,exist_ok=True)
immutable_json(out/'descriptive_analysis.json',{'created_at_utc':utc_now(),'status':'POST_HOC_DESCRIPTIVE_NO_NEW_PRIMARY_TEST','source_result_sha256':sha(p),'by_target':by_target,'by_position':by_position,'cells':cells,'positive_cells':sum(x['delta']>0 for x in cells),'mechanism_summary':summary,'mechanism_checkpoint_evidence':mechanism,'permutation_histogram': [{'left':float(edges[i]),'right':float(edges[i+1]),'count':int(c)} for i,c in enumerate(counts)],'primary_p_value_unchanged':s['exact_p_value'],'model_calls':0})
print(json.dumps({'mechanism':summary,'by_target':by_target,'by_position':by_position,'hist_counts':counts.tolist()},ensure_ascii=False))
