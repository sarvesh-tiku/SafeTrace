from __future__ import annotations

import csv
import json
import os
from datetime import datetime

from typing import Optional

from .schemas import (
    AgentAction,
    EvalResult,
    MonitorResult,
    PatchResult,
    TestResult,
    Trace,
)


class Tracer:
    def __init__(self, task_id: str, policy: str, issue: str) -> None:
        self.task_id = task_id
        self.policy = policy
        self.issue = issue
        self._actions: list[AgentAction] = []
        self._test_results: list[TestResult] = []
        self._monitor_result: Optional[MonitorResult] = None
        self._patch: Optional[PatchResult] = None
        self._retry_reasons: list[str] = []
        self._retrieved_files: list[str] = []
        self._model = "stub"

    def record_action(self, action: AgentAction) -> None:
        self._actions.append(action)

    def record_test_result(self, result: TestResult) -> None:
        self._test_results.append(result)

    def record_monitor_result(self, result: MonitorResult) -> None:
        self._monitor_result = result

    def record_patch(self, patch: PatchResult) -> None:
        self._patch = patch

    def add_retry_reason(self, reason: str) -> None:
        self._retry_reasons.append(reason)

    def set_retrieved_files(self, files: list[str]) -> None:
        self._retrieved_files = files

    def set_model(self, model: str) -> None:
        self._model = model

    def finalize(self, final_status: str, wall_time_sec: float) -> Trace:
        total_tokens = sum(a.tokens_used for a in self._actions)
        total_tests_run = sum(r.tests_run for r in self._test_results)
        total_tests_passed = sum(r.tests_passed for r in self._test_results)
        retry_count = max(0, len(self._test_results) - 1)

        files_changed = self._patch.files_changed if self._patch else []
        lines_changed = (
            self._patch.lines_added + self._patch.lines_removed if self._patch else 0
        )

        safety_flags: list[str] = []
        risk_score = 0
        monitor_decision = "n/a"
        if self._monitor_result:
            safety_flags = self._monitor_result.flagged_categories
            risk_score = self._monitor_result.risk_score
            monitor_decision = self._monitor_result.decision

        human_review_required = final_status in ("escalated", "blocked") or (
            self._monitor_result is not None
            and self._monitor_result.decision == "ask_human"
        )

        return Trace(
            task_id=self.task_id,
            policy=self.policy,
            issue=self.issue,
            model_calls=len(self._actions),
            tokens_used=total_tokens,
            wall_time_sec=round(wall_time_sec, 3),
            retrieved_files=self._retrieved_files,
            files_changed=files_changed,
            lines_changed=lines_changed,
            test_commands=[r.command for r in self._test_results],
            tests_run=total_tests_run,
            tests_passed=total_tests_passed,
            retry_count=retry_count,
            retry_reasons=self._retry_reasons,
            safety_flags=safety_flags,
            risk_score=risk_score,
            monitor_decision=monitor_decision,
            final_status=final_status,  # type: ignore[arg-type]
            human_review_required=human_review_required,
            monitor_result=self._monitor_result,
            actions=self._actions,
        )

    def write_trace(self, trace: Trace, output_path: str) -> None:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(trace.model_dump(mode="json"), f, indent=2, default=str)

    def append_to_csv(self, result: EvalResult, csv_path: str) -> None:
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        write_header = not os.path.exists(csv_path)
        with open(csv_path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(result.model_fields.keys()))
            if write_header:
                writer.writeheader()
            writer.writerow(result.model_dump())
