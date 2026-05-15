#!/bin/bash
#SBATCH --job-name=safetrace-eval
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --time=06:00:00
#SBATCH --mem=80G
#SBATCH --cpus-per-task=16
#SBATCH --output=logs/eval_%j.out
#SBATCH --error=logs/eval_%j.err
#
# SafeTrace full evaluation job.
# Starts a vLLM server, waits for it to be healthy, then runs all policies.
#
# Usage:
#   sbatch infra/slurm/submit_eval.slurm
#
# Override model:
#   MODEL=meta-llama/Llama-3.1-8B-Instruct sbatch infra/slurm/submit_eval.slurm
#
# For multi-GPU node (4× A100):
#   #SBATCH --gpus-per-node=4
#   TENSOR_PARALLEL=4 sbatch infra/slurm/submit_eval.slurm

set -euo pipefail

MODEL="${MODEL:-Qwen/Qwen2.5-Coder-7B-Instruct}"
PORT=8000
TENSOR_PARALLEL="${TENSOR_PARALLEL:-1}"
RESULTS_DIR="results/slurm_${SLURM_JOB_ID}"
LOG_DIR="logs"

mkdir -p "$LOG_DIR" "$RESULTS_DIR"

echo "════════════════════════════════════════════════"
echo " SafeTrace Evaluation — SLURM Job $SLURM_JOB_ID"
echo "════════════════════════════════════════════════"
echo " Node       : $(hostname)"
echo " GPUs       : $TENSOR_PARALLEL"
echo " Model      : $MODEL"
echo " Results    : $RESULTS_DIR"
echo " Started    : $(date -u +%FT%TZ)"
echo "════════════════════════════════════════════════"

# ── 1. Load CUDA module (cluster-specific) ───────────────────────────────────
module load cuda/12.4 2>/dev/null || true
module load python/3.11 2>/dev/null || true

# ── 2. Activate virtualenv ────────────────────────────────────────────────────
if [[ -f "venv/bin/activate" ]]; then
    source venv/bin/activate
elif [[ -f ".venv/bin/activate" ]]; then
    source .venv/bin/activate
fi

# ── 3. Load secrets ───────────────────────────────────────────────────────────
if [[ -f ".env" ]]; then
    set -a; source .env; set +a
fi

# ── 4. Train embedding monitor (if not already done) ─────────────────────────
if [[ ! -f "models/embeddings.npz" ]]; then
    echo "[slurm] Training embedding monitor on GPU..."
    python scripts/train_monitor.py --embed
fi

# ── 5. Start vLLM server ──────────────────────────────────────────────────────
echo "[slurm] Launching vLLM ($MODEL, TP=$TENSOR_PARALLEL)..."
python3 -m vllm.entrypoints.openai.api_server \
    --model "$MODEL" \
    --port "$PORT" \
    --tensor-parallel-size "$TENSOR_PARALLEL" \
    --gpu-memory-utilization 0.90 \
    --max-model-len 16384 \
    --enable-prefix-caching \
    > "$LOG_DIR/vllm_${SLURM_JOB_ID}.log" 2>&1 &
VLLM_PID=$!
echo "[slurm] vLLM PID: $VLLM_PID"

# ── 6. Wait for vLLM to be healthy ────────────────────────────────────────────
echo "[slurm] Waiting for vLLM to become healthy..."
MAX_WAIT=300
ELAPSED=0
until python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health')" 2>/dev/null; do
    sleep 5
    ELAPSED=$((ELAPSED + 5))
    if [[ $ELAPSED -ge $MAX_WAIT ]]; then
        echo "[slurm] ERROR: vLLM did not start within ${MAX_WAIT}s"
        kill $VLLM_PID 2>/dev/null || true
        exit 1
    fi
done
echo "[slurm] vLLM healthy after ${ELAPSED}s"

# ── 7. Run full benchmark evaluation ─────────────────────────────────────────
echo "[slurm] Running evaluation (unsafe patches, all policies)..."
python scripts/run_eval.py \
    --agent vllm \
    --model "$MODEL" \
    --vllm-url "http://localhost:${PORT}/v1" \
    --policy all \
    --patch-mode unsafe \
    --output "$RESULTS_DIR/unsafe_results.csv"

echo "[slurm] Running evaluation (safe patches, all policies)..."
python scripts/run_eval.py \
    --agent vllm \
    --model "$MODEL" \
    --vllm-url "http://localhost:${PORT}/v1" \
    --policy all \
    --patch-mode safe \
    --output "$RESULTS_DIR/safe_results.csv"

# ── 8. Generate report ────────────────────────────────────────────────────────
echo "[slurm] Generating report..."
python scripts/make_report.py --results-dir "$RESULTS_DIR" || true

# ── 9. Cleanup ────────────────────────────────────────────────────────────────
kill $VLLM_PID 2>/dev/null || true
echo "[slurm] Done. Results → $RESULTS_DIR"
echo "[slurm] Finished: $(date -u +%FT%TZ)"
