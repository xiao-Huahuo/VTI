#!/usr/bin/env python3
"""Make a one-commit source-only Git bundle without touching the main repo."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'exports/Science_C33_GPU_SOURCE_20260927.tar.gz'
BUNDLE = ROOT / 'exports/Science_C33_GPU_SOURCE_20260927.bundle'
BRANCH = 'codex/gpu-portable'


def run(*args: str, cwd: Path | None = None, env: dict | None = None):
    subprocess.run(args, check=True, cwd=cwd, env=env, stdout=subprocess.DEVNULL)


def main():
    if BUNDLE.exists():
        raise FileExistsError(BUNDLE)
    with tempfile.TemporaryDirectory(prefix='gpu-bundle-', dir=ROOT / '.runtime') as folder:
        work = Path(folder)
        with tarfile.open(SOURCE, 'r:gz') as archive:
            archive.extractall(work, filter='data')
        source = work / 'Science'
        manifest = json.loads((source / 'SOURCE_MANIFEST.json').read_text())
        for item in manifest['files']:
            path = source / item['path']
            if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
                raise RuntimeError(f'Source manifest mismatch: {item["path"]}')
        run('git', 'init', '-q', '-b', BRANCH, str(source))
        run('git', 'add', '-A', cwd=source)
        git_env = dict(os.environ)
        git_env.update({'GIT_AUTHOR_NAME': 'Codex source export',
                        'GIT_AUTHOR_EMAIL': 'codex-source-export@local.invalid',
                        'GIT_COMMITTER_NAME': 'Codex source export',
                        'GIT_COMMITTER_EMAIL': 'codex-source-export@local.invalid'})
        run('git', 'commit', '-q', '-m', 'source-only V57 engineering snapshot', cwd=source, env=git_env)
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip()
        run('git', 'bundle', 'create', str(BUNDLE), BRANCH, cwd=source)
        clone = work / 'clone-check'
        run('git', 'clone', '-q', '--branch', BRANCH, '--single-branch', str(BUNDLE), str(clone))
        if (clone / 'history').exists() or (clone / '.runtime').exists() or (clone / 'third_party').exists():
            raise RuntimeError('Portable Git clone unexpectedly contains ignored assets')
        for item in manifest['files']:
            if hashlib.sha256((clone / item['path']).read_bytes()).hexdigest() != item['sha256']:
                raise RuntimeError(f'Bundle clone differs: {item["path"]}')
    digest = hashlib.sha256(BUNDLE.read_bytes()).hexdigest()
    BUNDLE.with_suffix(BUNDLE.suffix + '.sha256').write_text(f'{digest}  {BUNDLE.name}\n')
    print(json.dumps({'bundle': str(BUNDLE), 'bytes': BUNDLE.stat().st_size,
                      'branch': BRANCH, 'commit': commit,
                      'files': manifest['file_count'], 'sha256': digest,
                      'clone_readback': 'PASS'}))


if __name__ == '__main__':
    main()
