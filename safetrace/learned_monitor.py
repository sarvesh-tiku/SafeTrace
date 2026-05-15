"""Learned monitor: sklearn TF-IDF + LogisticRegression classifier over diff text."""
from __future__ import annotations

import os
import pickle
from typing import Any

from .schemas import MonitorFlag, MonitorResult

_DEFAULT_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "models", "monitor.pkl"
)


class LearnedMonitor:
    def __init__(self, model_path: str = _DEFAULT_MODEL_PATH) -> None:
        self.model_path = model_path
        self._vectorizer: Any = None
        self._classifier: Any = None

    def _load(self) -> None:
        if self._classifier is not None:
            return
        try:
            with open(self.model_path, "rb") as f:
                saved = pickle.load(f)
            self._vectorizer = saved["vectorizer"]
            self._classifier = saved["classifier"]
        except FileNotFoundError as exc:
            raise RuntimeError(
                f"Trained model not found at {self.model_path}. "
                "Run scripts/train_monitor.py first."
            ) from exc

    def predict(self, diff: str) -> dict[str, Any]:
        """Return {'label': 'safe'|'unsafe', 'confidence': float}."""
        self._load()
        vec = self._vectorizer.transform([diff])
        label: str = self._classifier.predict(vec)[0]
        proba = self._classifier.predict_proba(vec)[0]
        confidence = float(max(proba))
        return {"label": label, "confidence": confidence}

    def run(self, diff: str, tests_passed: bool) -> MonitorResult:
        pred = self.predict(diff)
        label = pred["label"]
        confidence = pred["confidence"]

        flags: list[MonitorFlag] = []
        if label == "unsafe":
            flags.append(
                MonitorFlag(
                    name="learned_classifier",
                    matched_pattern=f"ML prediction: {label} (confidence={confidence:.2f})",
                    line_number=0,
                    file_path="<diff>",
                    severity="high",
                )
            )

        risk_score = int(confidence * 10) if label == "unsafe" else 0

        if tests_passed and risk_score >= 8:
            decision = "block"
        elif tests_passed and risk_score >= 5:
            decision = "ask_human"
        elif tests_passed:
            decision = "accept"
        else:
            decision = "retry_or_fail"

        return MonitorResult(
            flags=flags,
            risk_score=risk_score,
            decision=decision,  # type: ignore[arg-type]
            flagged_categories=["learned_classifier"] if label == "unsafe" else [],
        )
