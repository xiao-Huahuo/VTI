"""Export already accepted derived statistics; never alters raw or calls a model."""
from pathlib import Path
import sys,json,csv
SRC=next(p for p in Path(__file__).resolve().parents if p.name=='src');sys.path.insert(0,str(SRC))
from audit_freeze import src_and_project
from journal import immutable_json,sha
from recovery_batch import MANIFEST
_,project=src_and_project();m=json.loads(MANIFEST.read_text());out=SRC.parent/'outputs'/f"v58-{m['batch_id']}-analysis";result_path=out/'processed/exact_randomization.json';s=json.loads(result_path.read_text());audit=json.loads((project/'docs/v58/FINAL_EVIDENCE_AUDIT_20261005.json').read_text());assert audit['statistical_result_sha256']==sha(result_path)
for name,key in [('cell_dispersion.csv','per_cell_statistics'),('order_distances.csv','per_order_raw_statistics')]:
    rows=s[key]
    with (out/'processed'/name).open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows({k:json.dumps(v) if isinstance(v,list) else v for k,v in r.items()} for r in rows)
summary={'native_dispersion':s['native_dispersion'],'verified_dispersion':s['verified_dispersion'],'effect':s['effect'],'exact_p_value':s['exact_p_value'],'tail_count':s['right_tail_count'],'assignments':4096,'primary_gate_passed':s['significant'],'relative_dispersion_reduction_percent':100*s['effect']/s['native_dispersion'],'scope':'Fixed four-case panel, order/complete-history conditioned retrieval dispersion under amended 8192 execution conditions','accuracy_or_ranking_claim':False,'correctness_scored':False,'selected_sequences':24,'ingestions':4392,'answers_preserved':96,'selected_model_requests':4488,'recovery_manifest_sha256':sha(MANIFEST),'evidence_audit_sha256':sha(project/'docs/v58/FINAL_EVIDENCE_AUDIT_20261005.json'),'source_result_sha256':sha(result_path),'raw_untouched':True}
immutable_json(project/'docs/v58/FINAL_RESULT_SUMMARY_20261005.json',summary)
print(json.dumps(summary))
