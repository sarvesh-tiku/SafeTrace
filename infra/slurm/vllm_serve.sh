#!/bin/bash
#SBATCH --job-name=safetrace-vllm
#SBATCH --account=paceship-verbalcontracts
#SBATCH --partition=gpu-v100
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --time=24:00:00
#SBATCH --mem=80G
#SBATCH --cpus-per-task=12
#SBATCH --output=/storage/home/hcoda1/0/stiku6/SafeTrace-1/logs/vllm_%j.out
#
# Stand-alone vLLM server — use when running eval from a separate job.
# NOTE: Qwen and DeepSeek are prohibited on Georgia Tech PACE systems.

set -eo pipefail

PROJECT_ROOT="/storage/home/hcoda1/0/stiku6/SafeTrace-1"
cd "$PROJECT_ROOT"
mkdir -p logs

module load cuda/12.3.0 2>/dev/null || module load cuda/12.1.0 2>/dev/null || true
module load python/3.11.9 2>/dev/null || true

VENV_PATH="/storage/home/hcoda1/0/stiku6/venv311"
[[ -f "$VENV_PATH/bin/activate" ]] && source "$VENV_PATH/bin/activate"

MODEL="${MODEL:-microsoft/Phi-3.5-mini-instruct}"
PORT="${PORT:-8000}"

echo "Starting $MODEL on port $PORT..."
python3 -m vllm.entrypoints.openai.api_server \
  --model "$MODEL" \
  --tensor-parallel-size 1 \
  --max-model-len 16384 \
  --enable-prefix-caching \
  --gpu-memory-utilization 0.90 \
  --port "$PORT"
