#!/bin/bash
#SBATCH --job-name=v58-source-check
#SBATCH --account=yemang
#SBATCH --partition=a100x4
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:05:00
#SBATCH --output=v58-source-check-%j.log

set -euo pipefail

allowed_root="$(cd "$HOME/projects/srx" && pwd -P)"
working_dir="$(pwd -P)"
case "$working_dir" in
  "$allowed_root"/*) ;;
  *) echo "Refusing to work outside ~/projects/srx/" >&2; exit 2 ;;
esac

test -f CURRENT_STATE.json
python3 solutions/v58/src/gpu/prepare_sources.py --cluster --verify-only

# Resource visibility only. This job does not load Qwen, install packages,
# download data, or run any V58 experimental unit.
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
echo "SOURCE_ONLY_GPU_PREFLIGHT_PASS"
