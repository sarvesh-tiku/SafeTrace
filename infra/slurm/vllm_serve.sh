#!/bin/bash
#SBATCH --job-name=safetrace-vllm
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --time=24:00:00
#SBATCH --mem=80G
#SBATCH --cpus-per-task=16
#SBATCH --output=logs/vllm_%j.out

set -e

module load cuda/12.1 2>/dev/null || true

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

mkdir -p logs

echo "Starting Qwen2.5-Coder-32B on port 8000..."
vllm serve Qwen/Qwen2.5-Coder-32B-Instruct \
  --tensor-parallel-size 1 \
  --max-model-len 32768 \
  --enable-prefix-caching \
  --gpu-memory-utilization 0.90 \
  --port 8000 &
QWEN_PID=$!

echo "Starting Llama-3.1-70B on port 8001..."
vllm serve meta-llama/Llama-3.1-70B-Instruct \
  --tensor-parallel-size 1 \
  --max-model-len 16384 \
  --gpu-memory-utilization 0.90 \
  --quantization awq \
  --port 8001 &
LLAMA_PID=$!

echo "Qwen PID: $QWEN_PID, Llama PID: $LLAMA_PID"

wait $QWEN_PID $LLAMA_PID
