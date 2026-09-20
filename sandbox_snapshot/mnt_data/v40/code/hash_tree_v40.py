#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib
from pathlib import Path

p=argparse.ArgumentParser(); p.add_argument('root', type=Path); p.add_argument('--output', type=Path, required=True); a=p.parse_args()
root=a.root.resolve(); output=a.output.resolve(); lines=[]
for f in sorted(x for x in root.rglob('*') if x.is_file() and x.resolve()!=output):
    h=hashlib.sha256()
    with f.open('rb') as inp:
        for b in iter(lambda: inp.read(1024*1024), b''): h.update(b)
    lines.append(f"{h.hexdigest()}  {f.relative_to(root).as_posix()}")
output.write_text('\n'.join(lines)+'\n', encoding='utf-8')
