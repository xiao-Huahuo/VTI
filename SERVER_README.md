# GPU server preparation (engineering only)

This source tree intentionally omits `history/`, `.runtime/`, `third_party/`, downloaded datasets, model weights and exports. The active V57 protocol is **not frozen**, and this guide does not authorize or start scientific inference.

## Prepare public dependencies

On a Linux GPU server with Git, Python and [uv](https://docs.astral.sh/uv/) installed, clone the pushed source-only `main` branch and prepare public dependencies:

```bash
git clone --depth 1 --branch main git@github.com:xiao-Huahuo/VTI.git Science
cd Science
python3 ops/bootstrap_gpu_server.py
python3 ops/bootstrap_gpu_server.py --verify-only
```

The bootstrap installs two isolated Python 3.12 engineering environments, fetches Redis's benchmark at pinned commit `94192c39e2a4a154f441a5411e3d73c4f54974a6`, downloads the LongMemEval Small JSON, and downloads the pinned BGE ONNX snapshot. Every fetched source/data/model file is checked against `v57_design/DOWNLOADABLE_ASSETS.json`. It does **not** pull Qwen3 14B or Neo4j, contact OpenAI, or run V57.

If this source came from the portable `.tar.gz`, extract it and run the commands from its `Science/` directory. An alternative is the source-only `Science_C33_GPU_SOURCE_20260927.bundle`:

```bash
git clone --branch codex/gpu-portable --single-branch /path/to/Science_C33_GPU_SOURCE_20260927.bundle Science
cd Science
python3 ops/bootstrap_gpu_server.py
```

The bundle has one source-only commit and can be cloned without a Git hosting account. The local `main` branch is pushed to `git@github.com:xiao-Huahuo/VTI.git`; use `--depth 1` for the smallest hosted clone. Do not use `git push --mirror`, which would include local Codex turn-diff refs. The older commits remain in `main` history, while the portable bundle has no historical parent and is the smallest Git transfer.

## Still required before formal V57

Freeze a reviewed runtime manifest with the server's actual Qwen3 14B digest, Neo4j image digest, Graphiti-Local adapter/source hashes, per-unit isolation and checkpoint drill, and assignment schedule. The 14B/model/database downloads must be done under that reviewed protocol. `history/` is intentionally absent on the server; the V57 engineering preflight reads its BGE identity from the active `DOWNLOADABLE_ASSETS.json`, not historical V56 files.

Future raw V57 runs, checkpoints and large outputs are ignored by Git. Transfer them back as a separately hashed research artifact; do not rely on a source-code commit to preserve the experiment.
