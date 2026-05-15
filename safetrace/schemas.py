from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class TaskSpec(BaseModel):
    task_id: str
    category: str
    repo_path: str
    issue_path: str
    test_command: str
    visible_tests: list[str]
    hidden_safety_invariant: str
    unsafe_shortcut: str
    safe_fix_description: str
    risk_labels: list[str]
    expected_monitor_flags: list[str]


class MonitorFlag(BaseModel):
    name: str
    matched_pattern: str
    line_number: int
    file_path: str
    severity: Literal["low", "medium", "high", "critical"]


class MonitorResult(BaseModel):
    flags: list[MonitorFlag]
    risk_score: int
    decision: Literal["accept", "ask_human", "block", "retry_or_fail"]
    flagged_categories: list[str]


class AgentAction(BaseModel):
    action_type: str
    timestamp: datetime
    tokens_used: int
    model: str
    input_summary: str
    output_summary: str


class TestResult(BaseModel):
    passed: bool
    tests_run: int
    tests_passed: int
    tests_failed: int
    failure_output: str | None = None
    duration_sec: float
    command: str


class PatchResult(BaseModel):
    patch_id: str
    files_changed: list[str]
    lines_added: int
    lines_removed: int
    diff: str
    applied_at: datetime


class AgentState(BaseModel):
    task_id: str
    policy: str
    tokens_remaining: int
    min_tokens_to_continue: int
    has_relevant_context: bool
    patch_generated: bool
    patch: PatchResult | None = None
    tests_run: bool
    tests_passed: bool
    risk_score: int
    block_threshold: int
    escalate_threshold: int
    retry_count: int
    max_retries: int
    failure_is_localized: bool
    retrieved_files: list[str]


class Trace(BaseModel):
    task_id: str
    policy: str
    issue: str
    model_calls: int
    tokens_used: int
    wall_time_sec: float
    retrieved_files: list[str]
    files_changed: list[str]
    lines_changed: int
    test_commands: list[str]
    tests_run: int
    tests_passed: int
    retry_count: int
    retry_reasons: list[str]
    safety_flags: list[str]
    risk_score: int
    monitor_decision: str
    final_status: Literal[
        "safe",
        "unsafe_success",
        "unsafe_success_flagged",
        "failed_safe",
        "failed_unsafe",
        "blocked",
        "escalated",
        "unclear",
    ]
    human_review_required: bool
    monitor_result: MonitorResult | None = None
    actions: list[AgentAction]


class EvalResult(BaseModel):
    task_id: str
    category: str
    policy: str
    model: str
    patch_mode: str
    tests_passed: bool
    tests_run: int
    retry_count: int
    risk_score: int
    monitor_decision: str
    final_status: str
    human_review_required: bool
    safety_flags: str
    flagged_categories: str
    tokens_used: int
    wall_time_sec: float
    lines_changed: int
    files_changed: str
    monitor_recall_hit: bool
    expected_flags_hit: bool
