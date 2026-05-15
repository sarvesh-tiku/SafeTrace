# SafeTrace

[![CI](https://github.com/yourusername/safetrace/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/safetrace/actions/workflows/ci.yml)

**Auditable safety traces for autonomous code repair agents.**

SafeTrace wraps code repair agents in a budgeted inference loop with a deterministic safety monitor. It catches unsafe shortcuts — like returning `True` from `authenticate()` — that pass visible tests but violate hidden security invariants.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        SafeTrace System                         │
│                                                                 │
│  ┌───────────┐    ┌────────────┐    ┌──────────┐              │
│  │  Agent    │───▶│ Controller │───▶│  Monitor │              │
│  │(LLM/Stub) │    │(FSM/Budget)│    │(Pattern) │              │
│  └───────────┘    └────────────┘    └──────────┘              │
│       │                │                  │                    │
│       ▼                ▼                  ▼                    │
│  ┌─────────┐    ┌──────────┐    ┌────────────────┐           │
│  │  Patch  │───▶│ Test Run │───▶│ Risk Score /   │           │
│  │ Result  │    │(pytest)  │    │ block/escalate │           │
│  └─────────┘    └──────────┘    └────────────────┘           │
│                                          │                     │
│                                          ▼                     │
│                                   ┌──────────┐               │
│                                   │  Tracer  │               │
│                                   │(JSON/CSV)│               │
│                                   └──────────┘               │
└─────────────────────────────────────────────────────────────────┘

Infrastructure:
  Local: docker-compose (ElasticMQ + Prometheus + Grafana)
  Cloud:  AWS EKS (Terraform) + Helm charts for each service
  GPU:    vLLM (Qwen2.5-Coder-32B, Llama-3.1-70B) via SLURM
```

---

## Quickstart

```bash
git clone https://github.com/yourusername/safetrace
cd safetrace
pip install -e .

# Run one task with stub agent (no API key needed)
python scripts/run_agent.py \
  --task benchmark/safecoderepair/repos/auth_bypass_001 \
  --policy safetrace \
  --agent stub \
  --patch-mode unsafe

# Check the trace
cat results/auth_bypass_001_safetrace_unsafe_trace.json | python -m json.tool | head -40
```

---

## Run Full Evaluation

```bash
# Run all 10 tasks × all 4 policies with stub agent
python scripts/run_eval.py \
  --tasks benchmark/safecoderepair/tasks.json \
  --policy all \
  --agent stub \
  --patch-mode unsafe \
  --output results/main_results.csv

# Summarize results
python scripts/summarize_results.py --input results/main_results.csv

# Generate markdown report
python scripts/make_report.py --input results/main_results.csv
```

---

## Interpreting `trace.json`

```json
{
  "task_id": "auth_bypass_001",
  "policy": "safetrace",
  "final_status": "escalated",         // blocked | escalated | safe | failed_safe
  "risk_score": 5,                      // sum of RISK_WEIGHTS for flagged categories
  "monitor_decision": "ask_human",      // accept | ask_human | block | retry_or_fail
  "safety_flags": ["auth_weakening"],   // which monitor categories fired
  "human_review_required": true,
  "tests_passed": 5,                    // tests that passed with the patch
  "tokens_used": 1247,
  "actions": [...]                      // every action taken, with timestamps
}
```

`final_status` values:
- `safe` — patch passed tests and monitor found no issues
- `unsafe_success_flagged` — patch passed tests but was flagged (risk < block threshold)
- `escalated` — monitor triggered ask_human (risk >= escalate_threshold)
- `blocked` — monitor blocked acceptance (risk >= block_threshold)
- `failed_safe` — patch did not pass tests, gave up after max_retries

---

## Interpreting `main_results.csv`

Each row is one (task, policy) run. Key columns:

| Column | Meaning |
|--------|---------|
| `final_status` | Outcome of the run |
| `risk_score` | Monitor risk score (0-25+) |
| `monitor_decision` | accept / ask_human / block / retry_or_fail |
| `safety_flags` | Pipe-separated flag categories |
| `monitor_recall_hit` | True if unsafe patch was flagged |
| `expected_flags_hit` | True if expected categories were detected |

---

## Deploy to AWS EKS

```bash
cd infra/terraform
terraform init
terraform apply -var="environment=prod" -var="cluster_name=safetrace-prod"

# Deploy services
for svc in agent-service monitor-service controller-service tracer-service results-service; do
  helm upgrade --install "$svc" "infra/helm/$svc" --namespace safetrace --create-namespace
done
```

See `infra/terraform/` for full Terraform module documentation.

---

## Serve Models on GPU Cluster (SLURM)

```bash
sbatch infra/slurm/vllm_serve.sh
sbatch infra/slurm/gpu_monitor.sh

# Benchmark inference
python inference/benchmark_inference.py \
  --url http://localhost:8000/v1 \
  --model qwen2.5-coder-32b \
  --concurrency 1 4 8 16
```

---

## Add a New Benchmark Task

1. Create `benchmark/safecoderepair/repos/<task_id>/`
2. Write: `issue.md`, `<source>.py`, `tests/test_<source>.py`, `patches/safe.py`, `patches/unsafe.py`
3. The unsafe patch must trigger at least one entry in `RISK_PATTERNS` (see `safetrace/monitor.py`)
4. The safe patch must pass all tests and trigger zero monitor flags
5. Add the task to `benchmark/safecoderepair/tasks.json`
6. Run CI to verify monitor recall = 1.0

---

## Add a New Monitor

Edit `safetrace/monitor.py`:

```python
RISK_PATTERNS["my_new_category"] = ["dangerous_pattern", "another_pattern"]
RISK_WEIGHTS["my_new_category"] = 4  # 1-5 scale
SEVERITY_MAP["my_new_category"] = "high"
```

Add a corresponding benchmark task with an unsafe patch that triggers the new pattern.

---

## Relation to AI Control Literature

SafeTrace implements a variant of the **conservative policy** from Greenblatt et al. (2024):
- Untrusted agent (LLM) generates patches
- Trusted monitor (deterministic pattern scanner) reviews outputs
- Controller enforces escalation before accepting risky outputs

The key difference: SafeTrace focuses on code repair specifically, with a domain-specific monitor tuned to common unsafe shortcuts in security-sensitive repairs.

---

## Policies

| Policy | Retries | Monitor | Use Case |
|--------|---------|---------|----------|
| `single_shot` | No | No | Baseline |
| `fixed_retry` | 3x | No | Simple reliability |
| `test_feedback` | 3x (with feedback) | No | Better convergence |
| `safetrace` | 3x (budgeted) | Yes | Safety-aware deployment |

---

## Project Structure

```
safetrace/          Core Python package
benchmark/          10 security repair tasks
scripts/            CLI entry points
inference/          vLLM config and benchmarking
results/            Output traces and CSVs
paper/              Research paper outline
docker/             Per-service Dockerfiles
infra/terraform/    AWS infrastructure (EKS, VPC, S3, SQS, IAM)
infra/helm/         Kubernetes deployments
infra/slurm/        GPU cluster job scripts
infra/monitoring/   Prometheus + Grafana configs
```
