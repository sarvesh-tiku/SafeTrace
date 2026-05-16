#!/usr/bin/env bash
# start_vllm.sh — Launch a local vLLM server for SafeTrace evaluation.
#
# Usage:
#   bash scripts/start_vllm.sh                         # default model
#   MODEL=Qwen/Qwen2.5-Coder-7B-Instruct bash scripts/start_vllm.sh
#   MODEL=meta-llama/Llama-3.1-8B-Instruct bash scripts/start_vllm.sh
#   bash scripts/start_vllm.sh --4bit                  # enable AWQ/GPTQ quant
#
# Environment variables:
#   MODEL                  HF model ID   (default: Qwen/Qwen2.5-Coder-7B-Instruct)
#   PORT                   Server port   (default: 8000)
#   GPU_MEM_UTIL           Fraction 0-1  (default: 0.90)
#   MAX_MODEL_LEN          Context len   (default: 16384)
#   TENSOR_PARALLEL        GPU count     (default: auto-detect)

set -euo pipefail

# NOTE: Qwen is prohibited on Georgia Tech / PACE systems.
# Default: Llama 3.1 8B (Meta). Alternatives: mistralai/Mistral-7B-Instruct-v0.3
#          codellama/CodeLlama-7b-Instruct-hf  microsoft/Phi-3.5-mini-instruct
MODEL="${MODEL:-meta-llama/Llama-3.1-8B-Instruct}"
PORT="${PORT:-8000}"
GPU_MEM_UTIL="${GPU_MEM_UTIL:-0.90}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-16384}"

# Auto-detect GPU count
if command -v nvidia-smi &>/dev/null; then
    N_GPUS=$(nvidia-smi --list-gpus | wc -l)
else
    N_GPUS=1
fi
TENSOR_PARALLEL="${TENSOR_PARALLEL:-$N_GPUS}"

QUANTIZE=""
for arg in "$@"; do
    if [[ "$arg" == "--4bit" ]]; then
        QUANTIZE="--quantization awq"
    fi
done

echo "═══════════════════════════════════════════════════════"
echo " SafeTrace vLLM Server"
echo "═══════════════════════════════════════════════════════"
echo " Model      : $MODEL"
echo " Port       : $PORT"
echo " GPUs       : $TENSOR_PARALLEL × (detected $N_GPUS)"
echo " GPU mem    : $GPU_MEM_UTIL"
echo " Context    : $MAX_MODEL_LEN tokens"
echo " Quantize   : ${QUANTIZE:-none}"
echo "═══════════════════════════════════════════════════════"
echo ""

# Check vllm installed
if ! python3 -c "import vllm" 2>/dev/null; then
    echo "[ERROR] vllm not installed. Run:"
    echo "  pip install 'vllm>=0.6.0'"
    echo "  # or for source:"
    echo "  pip install 'safetrace[gpu]'"
    exit 1
fi

echo "Starting vLLM server — will be available at http://localhost:${PORT}/v1"
echo "Run evaluation with:"
echo "  python scripts/run_eval.py --agent vllm --model $MODEL --vllm-url http://localhost:${PORT}/v1"
echo ""

# shellcheck disable=SC2086
python3 -m vllm.entrypoints.openai.api_server \
    --model "$MODEL" \
    --port "$PORT" \
    --tensor-parallel-size "$TENSOR_PARALLEL" \
    --gpu-memory-utilization "$GPU_MEM_UTIL" \
    --max-model-len "$MAX_MODEL_LEN" \
    --enable-prefix-caching \
    --served-model-name "$MODEL" \
    $QUANTIZE
