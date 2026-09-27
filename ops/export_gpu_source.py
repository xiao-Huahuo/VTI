#!/usr/bin/env python3
"""Export the current uncommitted, source-only Science tree for server transfer."""
from __future__ import annotations

import hashlib
import io
import json
import subprocess
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'exports/Science_C33_GPU_SOURCE_20260927.tar.gz'
MAX_FILE_BYTES = 10 * 1024 * 1024
BLOCKED = {'history', 'third_party', '.runtime', '.git', 'exports', 'data', 'datasets', 'models', 'cache', 'work', 'outputs'}


def main():
    listing = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=ROOT)
    candidates = sorted({Path(raw.decode('utf-8')) for raw in listing.split(b'\0') if raw})
    files = []
    for relative in candidates:
        if any(part in BLOCKED for part in relative.parts) or relative.name.startswith('.env'):
            continue
        source = ROOT / relative
        if not source.is_file() or source.is_symlink():
            continue
        if source.stat().st_size > MAX_FILE_BYTES:
            raise RuntimeError(f'Unreviewed large source file: {relative}')
        files.append(relative)
    required = ['README.md', 'SERVER_README.md', '.gitignore', 'v57_design/PROTOCOL_DRAFT.json',
                'v57_design/DOWNLOADABLE_ASSETS.json', 'ops/bootstrap_gpu_server.py']
    if any(Path(name) not in files for name in required):
        raise RuntimeError('Portable source is missing a required current file')
    entries = []
    for relative in files:
        source = ROOT / relative
        entries.append({'path': relative.as_posix(), 'bytes': source.stat().st_size,
                        'sha256': hashlib.sha256(source.read_bytes()).hexdigest()})
    manifest = {'schema': 'c33-gpu-source-only-export-v1',
                'scope': 'Current source, protocol drafts, dependency manifest and small audit records only',
                'scientific_status': 'V57_NOT_FROZEN_NO_FORMAL_MODEL_CALLS',
                'files': entries, 'file_count': len(entries),
                'history_included': False, 'runtime_included': False, 'model_weights_included': False}
    payload = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        raise FileExistsError(OUT)
    with tarfile.open(OUT, 'w:gz', compresslevel=9) as archive:
        for relative in files:
            item = tarfile.TarInfo('Science/' + relative.as_posix())
            source = ROOT / relative
            item.size = source.stat().st_size
            item.mode = 0o644
            item.mtime = 0
            item.uid = item.gid = 0
            item.uname = item.gname = ''
            with source.open('rb') as stream:
                archive.addfile(item, stream)
        item = tarfile.TarInfo('Science/SOURCE_MANIFEST.json')
        item.size = len(payload)
        item.mode = 0o644
        item.mtime = 0
        item.uid = item.gid = 0
        item.uname = item.gname = ''
        archive.addfile(item, io.BytesIO(payload))
    digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
    OUT.with_suffix(OUT.suffix + '.sha256').write_text(f'{digest}  {OUT.name}\n')
    print(json.dumps({'archive': str(OUT), 'bytes': OUT.stat().st_size,
                      'source_files': len(files), 'sha256': digest}, ensure_ascii=False))


if __name__ == '__main__':
    main()
