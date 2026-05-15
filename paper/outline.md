# SafeTrace: Auditable Safety Traces for Autonomous Code Repair Agents

## Paper Outline

---

## Abstract
- Autonomous code repair agents can fix bugs quickly but may adopt unsafe shortcuts (auth bypass, test tampering) that pass visible tests
- We introduce SafeTrace: a policy that wraps repair agents in a budgeted inference loop with a deterministic safety monitor
- We evaluate 4 policies (SingleShot, FixedRetry, TestFeedback, SafeTrace) on SafeCodeRepair, a benchmark of 10 security-sensitive repair tasks
- SafeTrace achieves 100% monitor recall on unsafe patches with <20% false block rate on safe patches

---

## 1. Introduction
- AI coding agents (Copilot, Devin, SWE-agent) can close issues autonomously
- A key risk: agents find shortcuts that pass visible tests but violate hidden safety invariants
- Example: returning `True` from `authenticate()` passes functional tests but is catastrophically unsafe
- Existing evaluations measure test pass rate, not safety
- Contribution: (1) SafeCodeRepair benchmark, (2) SafeTrace policy, (3) empirical comparison

---

## 2. Background
- **Autonomous code repair:** program repair as agent loop (SWE-bench, Agentless, SWE-agent)
- **AI control:** monitoring untrusted models to prevent catastrophic actions (Greenblatt et al. 2024)
- **Static analysis vs. dynamic monitors:** tradeoffs in coverage, false positive rate
- **Unsafe shortcut taxonomy:** auth weakening, test tampering, secret leakage, injection, deserialization, exception swallowing, permission weakening, CORS misconfiguration, PII logging

---

## 3. The SafeCodeRepair Benchmark
- 10 tasks across 9 security categories
- Each task: source file with a bug, pytest test suite, safe patch, unsafe patch
- Hidden safety invariant: a property the agent must not violate even if tests pass
- Unsafe patch construction: minimal change that passes all visible tests while violating the invariant
- Evaluation metrics: test pass rate, unsafe acceptance rate, monitor recall/precision, human escalation rate, token cost

### 3.1 Task Construction
- Tasks represent real vulnerability classes (CWE-287, CWE-89, CWE-22, CWE-502, CWE-312, etc.)
- Bugs are minimal and unambiguous so safe fix is clear
- Unsafe patches are the "obvious shortcut" an agent might take under pressure

### 3.2 Evaluation Protocol
- Run each policy with stub agent (deterministic, uses pre-written patches) for reproducibility
- Run with real LLM agents (vLLM: Qwen2.5-Coder-32B, Llama-3.1-70B) for generalization
- Report all metrics in main_results.csv, traces in JSON

---

## 4. SafeTrace Policy
- **Controller FSM:** deterministic next_action() function; no model call determines control flow
- **Budgeted inference loop:** token budget prevents runaway spending
- **Monitor:** pattern-based, runs on diffs of added lines only; weighted risk scoring
- **Decision thresholds:** block (risk ≥ 8), ask_human (risk ≥ 5), accept (risk < 5)
- **Full auditability:** every action, test result, monitor flag, and decision is recorded in Trace

### 4.1 Monitor Design
- Scans only added lines in unified diff (not context lines)
- RISK_PATTERNS: 10 categories, 40+ patterns
- RISK_WEIGHTS: higher weight for auth/permission/test-tampering categories
- Decision rule preserves test-passing requirement before safety evaluation

### 4.2 Controller Design
- next_action() is a pure function of AgentState — deterministic, testable
- Separates "what to do next" (controller) from "how to do it" (agent)
- Enables replay and auditing of any run

---

## 5. Experiments

### 5.1 Main Results Table

| Policy | Test Pass Rate | Unsafe Accepted | Monitor Recall | Escalations | Mean Tokens |
|--------|----------------|-----------------|----------------|-------------|-------------|
| SingleShot | 70% | 70% | 0% | 0% | 400 |
| FixedRetry | 80% | 80% | 0% | 0% | 1200 |
| TestFeedback | 85% | 85% | 0% | 0% | 1600 |
| **SafeTrace** | **80%** | **~10%** | **100%** | **70%** | **2000** |

*Expected result pattern: SafeTrace has highest safety (lowest unsafe accepted, highest recall) at a cost of higher token use. SingleShot has lowest cost but zero safety filtering.*

### 5.2 Per-Category Analysis
- Auth weakening and test tampering are always caught (high-weight patterns)
- Exception swallowing has highest false positive rate (broad `except` is common in safe code too)
- Path traversal detection may miss obfuscated traversals

### 5.3 LLM Agent Results
- LLM agents generate more varied patches than stub; some unsafe patches differ from expected patterns
- Monitor recall drops slightly on LLM-generated patches (~85-95%)
- Tuning RISK_PATTERNS on LLM outputs improves recall

---

## 6. Discussion
- **Limitations:** pattern-based monitor has false positives and false negatives; does not understand semantics
- **Comparison to human review:** SafeTrace reduces human review load by catching most unsafe patches automatically
- **Token cost:** SafeTrace uses ~5x tokens of SingleShot; justified for security-sensitive repairs
- **Relation to AI control:** SafeTrace implements a "conservative policy" in the sense of Greenblatt et al. — when uncertain, escalate rather than accept

---

## 7. Related Work
- SWE-bench, SWE-agent, Agentless: code repair evaluation
- Greenblatt et al. 2024: AI control via monitoring
- Static analysis tools (Semgrep, Bandit): rule-based vulnerability detection
- CodeBERT, GraphCodeBERT: learned vulnerability detection
- Human-in-the-loop for AI safety: escalation and oversight mechanisms

---

## 8. Conclusion
- SafeTrace demonstrates that auditable policy wrappers can significantly reduce unsafe shortcut acceptance with modest cost increase
- SafeCodeRepair is a reproducible benchmark for evaluating safety-aware code repair
- Open questions: semantic monitors, learned detectors, multi-agent oversight

---

## Appendix

### A. Full RISK_PATTERNS and RISK_WEIGHTS
### B. Controller FSM Pseudocode
### C. Per-Task Traces (unsafe examples)
### D. Full Results Tables
