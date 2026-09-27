#!/usr/bin/env python3
"""Prepare portable V57 engineering dependencies; never start an experiment."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'v57_design/DOWNLOADABLE_ASSETS.json'
ENV = ROOT / 'v57_design/environment'
STAT = ROOT / '.runtime/v57-stat-venv'
GRAPHITI = ROOT / '.runtime/v57-graphiti-venv'


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def snapshot_sha(path: Path) -> tuple[str, int]:
    if not path.is_dir():
        raise FileNotFoundError(path)
    h = hashlib.sha256()
    files = sorted(p for p in path.rglob('*') if p.is_file())
    for file in files:
        h.update(file.relative_to(path).as_posix().encode() + b'\0' + sha(file).encode() + b'\n')
    return h.hexdigest(), len(files)


def run(*args: str, cwd: Path = ROOT, env: dict[str, str] | None = None):
    subprocess.run(args, cwd=cwd, env=env, check=True)


def prepare_venv(path: Path, requirements: Path):
    if not shutil.which('uv'):
        raise RuntimeError('Install uv from https://docs.astral.sh/uv/ before server bootstrap')
    if not (path / 'bin/python').is_file():
        run('uv', 'venv', '--python', '3.12', str(path))
    run('uv', 'pip', 'install', '--python', str(path / 'bin/python'), '-r', str(requirements))


def prepare_source(asset: dict):
    dest = ROOT / asset['checkout_dir']
    if dest.exists():
        return
    if not shutil.which('git'):
        raise RuntimeError('git is required to retrieve the pinned benchmark source')
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.benchmark-fetch-', dir=dest.parent) as folder:
        tmp = Path(folder) / 'repo'
        run('git', 'init', '-q', str(tmp))
        run('git', '-C', str(tmp), 'remote', 'add', 'origin', asset['git_url'])
        run('git', '-C', str(tmp), 'fetch', '--depth', '1', 'origin', asset['commit'])
        run('git', '-C', str(tmp), 'checkout', '--detach', 'FETCH_HEAD')
        tmp.rename(dest)


def prepare_dataset(asset: dict):
    dest = Path.home() / asset['cache_relative_to_home']
    if dest.is_file():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + '.download')
    request = urllib.request.Request(asset['url'], headers={'User-Agent': 'C33-portable-bootstrap/1.0'})
    try:
        with urllib.request.urlopen(request, timeout=300) as response, tmp.open('wb') as output:
            shutil.copyfileobj(response, output, 1024 * 1024)
        if sha(tmp) != asset['sha256']:
            raise RuntimeError('Downloaded LongMemEval dataset SHA-256 does not match the pinned input')
        tmp.replace(dest)
    finally:
        if tmp.exists():
            tmp.unlink()


def prepare_embedding(asset: dict):
    revision = asset['observed_hf_revision']
    cache = ROOT / asset['cache_dir']
    snapshot = cache / 'models--Qdrant--bge-small-en-v1.5-onnx-Q' / 'snapshots' / revision
    if snapshot.is_dir() and snapshot_sha(snapshot)[0] == asset['snapshot_tree_sha256']:
        return
    # Pin the actual public model revision; no current-main lookup or LLM call.
    script = (
        'from huggingface_hub import snapshot_download\n'
        'snapshot_download(repo_id=' + repr(asset['hf_repo']) + ', revision=' + repr(revision) +
        ', cache_dir=' + repr(str(cache)) +
        ', allow_patterns=["config.json","model_optimized.onnx","special_tokens_map.json",'
        '"tokenizer.json","tokenizer_config.json"])\n'
    )
    safe_env = dict(os.environ)
    safe_env.pop('OPENAI_API_KEY', None)
    safe_env['GRAPHITI_TELEMETRY_ENABLED'] = 'false'
    run(str(GRAPHITI / 'bin/python'), '-c', script, env=safe_env)


def verify(asset: dict) -> dict:
    repo = ROOT / asset['benchmark_source']['checkout_dir']
    if not (repo / '.git').exists():
        raise RuntimeError('Pinned Redis benchmark checkout missing')
    commit = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
    if commit != asset['benchmark_source']['commit']:
        raise RuntimeError(f'Benchmark source commit drift: {commit}')
    dataset = Path.home() / asset['longmemeval_small']['cache_relative_to_home']
    if sha(dataset) != asset['longmemeval_small']['sha256']:
        raise RuntimeError('LongMemEval dataset SHA-256 drift')
    embedding = asset['measurement_embedding']
    snapshot = ROOT / embedding['cache_dir'] / 'models--Qdrant--bge-small-en-v1.5-onnx-Q' / 'snapshots' / embedding['observed_hf_revision']
    model_sha, files = snapshot_sha(snapshot)
    if model_sha != embedding['snapshot_tree_sha256']:
        raise RuntimeError('Pinned BGE snapshot SHA-256 drift')
    for name, path, expected in (
        ('statistics', STAT, {'numpy': '2.5.3'}),
        ('graphiti', GRAPHITI, {'graphiti-core': '0.30.2', 'fastembed': '0.8.0', 'numpy': '2.5.3'}),
    ):
        if not (path / 'bin/python').is_file():
            raise RuntimeError(f'{name} Python environment missing')
        code = ('import importlib.metadata as m,sys,json; '
                'print(json.dumps({"python":sys.version_info[:3],"packages":{p:m.version(p) for p in '
                + repr(list(expected)) + '}}))')
        observed = json.loads(subprocess.check_output([str(path / 'bin/python'), '-c', code], text=True))
        if observed['python'][:2] != [3, 12] or observed['packages'] != expected:
            raise RuntimeError(f'{name} Python/package version drift: {observed}')
    source_path = str(ROOT / 'v57_design/code')
    stat_smoke = (
        'import sys,numpy as np; sys.path.insert(0,' + repr(source_path) + '); '
        'from count_unit_v1 import score; from partial_conjunction import target_test; '
        'from retrieval_footprint import footprint; '
        'assert score("b5ef892d","8 days.")["status"]=="CORRECT"; '
        'assert target_test(np.zeros((10,1925)),[5,6,7,8,9],formal=True)["p_value"]==1; '
        'assert footprint([],lambda _:[]).shape==(1925,)'
    )
    subprocess.run([str(STAT / 'bin/python'), '-c', stat_smoke], check=True)
    graphiti_smoke = f'''import asyncio, sys
sys.path.insert(0, {source_path!r})
from local_graphiti_components import FastEmbedBGE
async def main():
    vector = await FastEmbedBGE().create("portable toy")
    assert len(vector) == 384
asyncio.run(main())
'''
    safe_env = dict(os.environ)
    safe_env.pop('OPENAI_API_KEY', None)
    safe_env['GRAPHITI_TELEMETRY_ENABLED'] = 'false'
    safe_env['EMBEDDING_DIM'] = '384'
    subprocess.run([str(GRAPHITI / 'bin/python'), '-c', graphiti_smoke], env=safe_env, check=True)
    return {'status': 'ENGINEERING_ASSETS_VERIFIED_NO_V57_RUN', 'benchmark_commit': commit,
            'dataset_sha256': asset['longmemeval_small']['sha256'],
            'bge_snapshot_sha256': model_sha, 'bge_snapshot_files': files,
            'statistics_and_toy_embedding_smoke': 'PASS',
            'model_14b_downloaded_by_this_script': False, 'neo4j_downloaded_by_this_script': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify-only', action='store_true', help='do not download or install anything')
    args = parser.parse_args()
    asset = json.loads(ASSETS.read_text(encoding='utf-8'))
    if not args.verify_only:
        prepare_venv(STAT, ENV / 'requirements-stat.txt')
        prepare_venv(GRAPHITI, ENV / 'requirements-graphiti.txt')
        prepare_source(asset['benchmark_source'])
        prepare_dataset(asset['longmemeval_small'])
        prepare_embedding(asset['measurement_embedding'])
    print(json.dumps(verify(asset), indent=2))
    print('V57 protocol is not frozen. This script never pulls 14B or Neo4j and never starts a formal run.')


if __name__ == '__main__':
    main()
