#!/bin/bash
set -e

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

QWEN_PORT=8000
LLAMA_PORT=8001

# Check if running under SLURM
if [ -n "${SLURM_JOB_ID}" ]; then
    echo "Running under SLURM job: ${SLURM_JOB_ID}"
    LOG_DIR="logs/vllm_${SLURM_JOB_ID}"
else
    LOG_DIR="logs/vllm_local"
fi
mkdir -p "${LOG_DIR}"

echo "Starting Qwen2.5-Coder-32B on port ${QWEN_PORT}..."
vllm serve Qwen/Qwen2.5-Coder-32B-Instruct \
    --tensor-parallel-size 1 \
    --max-model-len 32768 \
    --enable-prefix-caching \
    --gpu-memory-utilization 0.90 \
    --dtype float16 \
    --port "${QWEN_PORT}" \
    > "${LOG_DIR}/qwen.log" 2>&1 &
QWEN_PID=$!
echo "Qwen PID: ${QWEN_PID}"

echo "Starting Llama-3.1-70B on port ${LLAMA_PORT}..."
vllm serve meta-llama/Llama-3.1-70B-Instruct \
    --tensor-parallel-size 1 \
    --max-model-len 16384 \
    --gpu-memory-utilization 0.90 \
    --quantization awq \
    --dtype float16 \
    --port "${LLAMA_PORT}" \
    > "${LOG_DIR}/llama.log" 2>&1 &
LLAMA_PID=$!
echo "Llama PID: ${LLAMA_PID}"

# Wait for health checks
echo "Waiting for models to be ready..."
for port in "${QWEN_PORT}" "${LLAMA_PORT}"; do
    for i in $(seq 1 60); do
        if curl -sf "http://localhost:${port}/health" > /dev/null 2>&1; then
            echo "Port ${port} is ready."
            break
        fi
        if [ "$i" -eq 60 ]; then
            echo "WARNING: Port ${port} did not become healthy after 60 attempts."
        fi
        sleep 5
    done
done

echo "Both models are serving. PIDs: qwen=${QWEN_PID} llama=${LLAMA_PID}"
wait
