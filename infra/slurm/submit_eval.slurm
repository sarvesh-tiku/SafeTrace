#!/bin/bash
#SBATCH --job-name=safetrace-eval
#SBATCH --account=paceship-verbalcontracts
#SBATCH --partition=gpu-v100
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=12
#SBATCH --time=06:00:00
#SBATCH --mem=80G
#SBATCH --output=/storage/home/hcoda1/0/stiku6/SafeTrace-1/logs/eval_%j.out
#SBATCH --error=/storage/home/hcoda1/0/stiku6/SafeTrace-1/logs/eval_%j.err
#
# SafeTrace full evaluation — Georgia Tech PACE Phoenix (gpu-v100).
# Uses LocalTransformersAgent — no vLLM server required.
#
# NOTE: Qwen and DeepSeek are on Georgia Tech's prohibited software list.
#       Allowed: Llama, Mistral, Phi, CodeLlama.
#
# Usage:
#   sbatch infra/slurm/submit_eval.slurm
#
# Override model (must be non-prohibited):
#   MODEL=meta-llama/Llama-3.1-8B-Instruct sbatch infra/slurm/submit_eval.slurm

set -eo pipefail

# ── 0. Pin working directory to project root ──────────────────────────────────
PROJECT_ROOT="/storage/home/hcoda1/0/stiku6/SafeTrace-1"
cd "$PROJECT_ROOT"

# ── 1. Create output dirs before anything writes to them ─────────────────────
mkdir -p logs results models

# ── 2. Load modules ───────────────────────────────────────────────────────────
module load cuda/12.3.0 2>/dev/null || module load cuda/12.1.0 2>/dev/null || \
  module load cuda 2>/dev/null || true
module load python/3.11.9 2>/dev/null || module load python/3.11 2>/dev/null || true

# ── 3. Activate virtualenv ────────────────────────────────────────────────────
VENV_PATH="/storage/home/hcoda1/0/stiku6/venv311"
if [[ -f "$VENV_PATH/bin/activate" ]]; then
    source "$VENV_PATH/bin/activate"
    echo "[slurm] Activated venv: $VENV_PATH"
else
    echo "[slurm] ERROR: virtualenv not found at $VENV_PATH"
    echo "[slurm]   Run on login node:"
    echo "[slurm]   module load python/3.11.9"
    echo "[slurm]   python3 -m venv ~/venv311 && source ~/venv311/bin/activate"
    echo "[slurm]   pip install --no-cache-dir pydantic rich typer pandas gitpython"
    echo "[slurm]       openai anthropic boto3 httpx python-dotenv prometheus-client"
    echo "[slurm]       pyyaml numpy scikit-learn torch transformers accelerate"
    echo "[slurm]   pip install --no-cache-dir --ignore-requires-python -e . --no-deps"
    exit 1
fi

# ── 4. Model and paths ────────────────────────────────────────────────────────
# Phi-3.5-mini: 3.8B, ~7.6 GB FP16 — fits on V100-16GB, not on GT prohibited list.
# Alternatives: meta-llama/Llama-3.1-8B-Instruct
#               mistralai/Mistral-7B-Instruct-v0.3
#               codellama/CodeLlama-7b-Instruct-hf
MODEL="${MODEL:-microsoft/Phi-3.5-mini-instruct}"
RESULTS_DIR="results/slurm_${SLURM_JOB_ID}"
mkdir -p "$RESULTS_DIR"

echo "════════════════════════════════════════════════"
echo " SafeTrace Evaluation — SLURM Job $SLURM_JOB_ID"
echo "════════════════════════════════════════════════"
echo " Node       : $(hostname)"
echo " Model      : $MODEL"
echo " Results    : $RESULTS_DIR"
echo " Agent      : local (LocalTransformersAgent)"
echo " Python     : $(python3 --version)"
echo " Started    : $(date -u +%FT%TZ)"
echo "════════════════════════════════════════════════"

# ── 5. Load secrets from .env ─────────────────────────────────────────────────
if [[ -f ".env" ]]; then
    set -a; source .env; set +a
    echo "[slurm] Loaded .env"
fi

# ── 6. HuggingFace token (required for gated models like Llama) ───────────────
if [[ -n "${HF_TOKEN:-}" ]]; then
    export HUGGING_FACE_HUB_TOKEN="$HF_TOKEN"
    echo "[slurm] HuggingFace token loaded from .env"
elif [[ -n "${HUGGING_FACE_HUB_TOKEN:-}" ]]; then
    echo "[slurm] HuggingFace token found in environment"
else
    echo "[slurm] WARNING: no HF_TOKEN — gated models (Llama) will fail"
fi

# HF model cache — try scratch paths in order, fall back to home.
# Phi-3.5-mini is ~7.6 GB; keep it off home to avoid quota issues.
HF_CACHE=""
for _candidate in \
    "${SCRATCH}/hf_cache" \
    "/storage/scratch1/${USER}/hf_cache" \
    "/storage/scratch2/${USER}/hf_cache" \
    "/storage/scratch3/${USER}/hf_cache" \
    "$HOME/hf_cache"; do
    [[ -z "$_candidate" || "$_candidate" == "/hf_cache" ]] && continue
    if mkdir -p "$_candidate" 2>/dev/null; then
        HF_CACHE="$_candidate"
        break
    fi
done
export HF_HOME="$HF_CACHE"
export TRANSFORMERS_CACHE="$HF_CACHE"
# Load from cache only — prevents HF from writing lock/metadata files mid-job.
export TRANSFORMERS_OFFLINE=1
export HF_DATASETS_OFFLINE=1
echo "[slurm] HuggingFace cache: $HF_CACHE (offline mode)"

# Disable tokenizers parallelism warning inside SLURM
export TOKENIZERS_PARALLELISM=false

# ── 2b. Ensure torch has CUDA support ────────────────────────────────────────
if ! python -c "import torch; assert torch.cuda.is_available()" 2>/dev/null; then
    echo "[slurm] torch has no CUDA — reinstalling cu121 wheel..."
    pip install torch --index-url https://download.pytorch.org/whl/cu121 -q
fi
echo "[slurm] torch CUDA: $(python -c 'import torch; print(torch.cuda.is_available(), torch.version.cuda)')"

# ── 2c. Pin transformers to <4.46 ─────────────────────────────────────────────
# Phi-3.5's remote modeling_phi3.py (trust_remote_code) uses DynamicCache APIs
# removed in 4.46+. We use the native Phi3ForCausalLM instead (no trust_remote_code),
# but pin here so a future `pip install` doesn't silently break things.
python -c "
import transformers, sys
v = tuple(int(x) for x in transformers.__version__.split('.')[:2])
if v >= (4, 46):
    print(f'[slurm] transformers {transformers.__version__} >= 4.46 detected — pinning to 4.44.2')
    sys.exit(1)
" || pip install "transformers==4.44.2" -q
echo "[slurm] transformers: $(python -c 'import transformers; print(transformers.__version__)')"

# ── 7. Train embedding monitor (skip if already done) ────────────────────────
if [[ ! -f "models/embeddings.npz" ]]; then
    echo "[slurm] Training CodeBERT embedding monitor on GPU..."
    python scripts/train_monitor.py --embed
else
    echo "[slurm] Embedding monitor already trained — skipping"
fi

# ── 8. Run benchmark ──────────────────────────────────────────────────────────
echo "[slurm] Running evaluation (unsafe patches, all policies)..."
python scripts/run_eval.py \
    --agent local \
    --model "$MODEL" \
    --policy all \
    --patch-mode unsafe \
    --output "$RESULTS_DIR/unsafe_results.csv"

echo "[slurm] Running evaluation (safe patches, all policies)..."
python scripts/run_eval.py \
    --agent local \
    --model "$MODEL" \
    --policy all \
    --patch-mode safe \
    --output "$RESULTS_DIR/safe_results.csv"

# ── 9. Generate report ────────────────────────────────────────────────────────
echo "[slurm] Generating report..."
python scripts/make_report.py \
    --input "$RESULTS_DIR/unsafe_results.csv" \
    --output "$RESULTS_DIR/summary.md" \
    --latex "$RESULTS_DIR/tables.tex" || true

echo "[slurm] Done. Results → $RESULTS_DIR"
echo "[slurm] Finished: $(date -u +%FT%TZ)"
