#!/bin/zsh
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BENCHMARK_REPO="$PROJECT_ROOT/third_party/agent-memory-server"
BENCHMARK_DIR="$BENCHMARK_REPO/agent-memory-benchmark"
V40_ROOT="$PROJECT_ROOT/sandbox_snapshot/mnt_data/v40"
RUN_ROOT="${1:-$PROJECT_ROOT/experiment_outputs/redis_v34_v40_$(date +%Y%m%d_%H%M%S)}"

export HTTP_PROXY="${HTTP_PROXY:-http://127.0.0.1:7891}"
export HTTPS_PROXY="${HTTPS_PROXY:-http://127.0.0.1:7891}"
export ALL_PROXY="${ALL_PROXY:-http://127.0.0.1:7891}"
export http_proxy="$HTTP_PROXY"
export https_proxy="$HTTPS_PROXY"
export all_proxy="$ALL_PROXY"
export NO_PROXY="${NO_PROXY:-localhost,127.0.0.1,::1}"
export no_proxy="$NO_PROXY"

if [[ ! -f "$PROJECT_ROOT/.env" ]]; then
  print -u2 "Missing $PROJECT_ROOT/.env"
  exit 2
fi

set -a
source "$PROJECT_ROOT/.env"
set +a

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  print -u2 "OPENAI_API_KEY is not set by .env"
  exit 2
fi

if [[ ! -x "$BENCHMARK_DIR/.venv/bin/python" ]]; then
  print -u2 "Benchmark virtual environment is missing; run uv sync first"
  exit 2
fi

export PATH="$BENCHMARK_DIR/.venv/bin:$PATH"
python --version

exec "$V40_ROOT/code/run_redis_v34_v40.sh" "$BENCHMARK_REPO" "$RUN_ROOT"
