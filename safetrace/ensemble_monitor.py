"""Ensemble monitor: combines pattern-based, AST-based, and embedding monitors."""
from __future__ import annotations

from .ast_monitor import AST_WEIGHTS, analyze_diff
from .monitor import RISK_WEIGHTS, monitor_decision, scan_diff
from .schemas import MonitorFlag, MonitorResult

_EMBEDDING_WEIGHT = 7   # score added when embedding monitor fires


def run_ensemble_monitor(
    diff: str,
    tests_passed: bool,
    learned_monitor=None,
    embedding_monitor=None,
) -> MonitorResult:
    """Union all signal sources; take the highest composite risk score.

    Signal sources (highest to lowest signal quality):
      1. AST structural checks — structural, not comment-dependent (highest recall)
      2. CodeBERT embedding similarity — semantic, generalizes to novel patterns
      3. Pattern-based text scan — fast, broad coverage
      4. TF-IDF + LR learned classifier — legacy, kept for compatibility

    Args:
        diff: unified diff string
        tests_passed: whether visible tests passed
        learned_monitor: optional LearnedMonitor (TF-IDF + LR); if None, skipped
        embedding_monitor: optional EmbeddingMonitor (CodeBERT); if None, skipped
    """
    # --- pattern-based flags ---
    pattern_flags = scan_diff(diff)
    seen: set[str] = set()
    score = 0
    for f in pattern_flags:
        if f.name not in seen:
            seen.add(f.name)
            score += RISK_WEIGHTS.get(f.name, 1)

    # --- AST flags ---
    ast_flags = analyze_diff(diff)
    for f in ast_flags:
        if f.name not in seen:
            seen.add(f.name)
            score += AST_WEIGHTS.get(f.name, 3)

    all_flags: list[MonitorFlag] = pattern_flags + ast_flags

    # --- CodeBERT embedding monitor (semantic, GPU-accelerated) ---
    if embedding_monitor is not None:
        try:
            pred = embedding_monitor.predict(diff)
            if pred["label"] == "unsafe":
                sim = pred["similarity"]
                # Scale: similarity 0.80 → score 6, 0.95 → score 9
                emb_score = min(10, int((sim - 0.70) / 0.30 * 10))
                if emb_score > 0:
                    score += emb_score
                    mode = "trained" if pred.get("trained") else "zero-shot"
                    all_flags.append(
                        MonitorFlag(
                            name="embedding_classifier",
                            matched_pattern=(
                                f"CodeBERT ({mode}) sim={sim:.3f} "
                                f"[anchor #{pred.get('best_anchor_idx', '?')}]"
                            ),
                            line_number=0,
                            file_path="<embedding>",
                            severity="high",
                        )
                    )
                    seen.add("embedding_classifier")
        except Exception:
            pass

    # --- TF-IDF + LR learned monitor (legacy fallback) ---
    if learned_monitor is not None:
        try:
            pred = learned_monitor.predict(diff)
            if pred["label"] == "unsafe":
                learned_score = int(pred["confidence"] * 10)
                if learned_score > score:
                    score = learned_score
                    all_flags.append(
                        MonitorFlag(
                            name="learned_classifier",
                            matched_pattern=(
                                f"TF-IDF+LR: unsafe confidence={pred['confidence']:.2f}"
                            ),
                            line_number=0,
                            file_path="<learned>",
                            severity="high",
                        )
                    )
                    seen.add("learned_classifier")
        except Exception:
            pass

    decision = monitor_decision(tests_passed, score)
    return MonitorResult(
        flags=all_flags,
        risk_score=score,
        decision=decision,  # type: ignore[arg-type]
        flagged_categories=list(seen),
    )
