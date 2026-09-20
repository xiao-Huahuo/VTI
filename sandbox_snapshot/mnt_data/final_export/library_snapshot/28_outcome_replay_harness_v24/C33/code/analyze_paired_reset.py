from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from collections import defaultdict

REQUIRED = {"case_id","arm","post_reset_count","canary_hit","recall_at_5","mrr","stale_answer"}
ARMS = {"invoke_only","verified_clean"}

def load(path: Path):
    rows=[]
    for n,line in enumerate(path.read_text().splitlines(),1):
        if not line.strip(): continue
        row=json.loads(line)
        missing=REQUIRED-set(row)
        if missing: raise ValueError(f"line {n} missing {sorted(missing)}")
        if row["arm"] not in ARMS: raise ValueError(f"line {n} bad arm")
        rows.append(row)
    return rows

def paired(rows):
    by=defaultdict(dict)
    for r in rows:
        if r["arm"] in by[r["case_id"]]: raise ValueError(f"duplicate arm for {r['case_id']}")
        by[r["case_id"]][r["arm"]]=r
    bad=[k for k,v in by.items() if set(v)!=ARMS]
    if bad: raise ValueError(f"unpaired cases: {bad[:5]}")
    return [(k,v["invoke_only"],v["verified_clean"]) for k,v in sorted(by.items())]

def mean(xs): return sum(xs)/len(xs) if xs else None

def bootstrap_delta(pairs, field, n=5000, seed=42):
    rng=random.Random(seed)
    ds=[]
    vals=[float(a[field])-float(b[field]) for _,a,b in pairs]
    if not vals: return None
    for _ in range(n):
        ds.append(mean([vals[rng.randrange(len(vals))] for __ in vals]))
    ds.sort()
    lo=ds[int(.025*(n-1))]; hi=ds[int(.975*(n-1))]
    return {"delta_invoke_minus_clean":mean(vals),"bootstrap95":[lo,hi]}

def mcnemar_exact(pairs, field):
    b=c=0
    for _,a,z in pairs:
        av=bool(a[field]); zv=bool(z[field])
        if av and not zv: b+=1
        elif zv and not av: c+=1
    n=b+c
    if n==0: return {"discordant":0,"b":b,"c":c,"p_exact":1.0}
    k=min(b,c)
    p=min(1.0, 2*sum(math.comb(n,i) for i in range(k+1))/(2**n))
    return {"discordant":n,"b":b,"c":c,"p_exact":p}

def summarize(rows):
    pairs=paired(rows)
    def rate(arm, field):
        vals=[bool(x[field]) for _,a,b in pairs for x in ([a] if arm=="invoke_only" else [b])]
        return sum(vals)/len(vals)
    def avg(arm, field):
        vals=[float(x[field]) for _,a,b in pairs for x in ([a] if arm=="invoke_only" else [b])]
        return mean(vals)
    return {
      "n_pairs":len(pairs),
      "post_reset_residual_rate":{"invoke_only":rate("invoke_only","post_reset_count"),"verified_clean":rate("verified_clean","post_reset_count")},
      "canary_hit_rate":{"invoke_only":rate("invoke_only","canary_hit"),"verified_clean":rate("verified_clean","canary_hit"),"mcnemar":mcnemar_exact(pairs,"canary_hit")},
      "stale_answer_rate":{"invoke_only":rate("invoke_only","stale_answer"),"verified_clean":rate("verified_clean","stale_answer"),"mcnemar":mcnemar_exact(pairs,"stale_answer")},
      "recall_at_5":{"invoke_only":avg("invoke_only","recall_at_5"),"verified_clean":avg("verified_clean","recall_at_5"),"paired":bootstrap_delta(pairs,"recall_at_5")},
      "mrr":{"invoke_only":avg("invoke_only","mrr"),"verified_clean":avg("verified_clean","mrr"),"paired":bootstrap_delta(pairs,"mrr")},
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("trace"); ap.add_argument("--out")
    a=ap.parse_args(); s=summarize(load(Path(a.trace)))
    txt=json.dumps(s,indent=2,sort_keys=True)
    if a.out: Path(a.out).write_text(txt+"\n")
    print(txt)
if __name__=="__main__": main()
