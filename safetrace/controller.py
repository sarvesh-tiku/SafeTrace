from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from .schemas import AgentAction, AgentState


def next_action(state: AgentState) -> str:
    if state.tokens_remaining < state.min_tokens_to_continue:
        return "stop_failed"
    if not state.has_relevant_context:
        return "retrieve_more_context"
    if not state.patch_generated:
        return "generate_patch"
    if not state.tests_run:
        return "run_tests"
    if state.tests_passed:
        if state.risk_score >= state.block_threshold:
            return "block"
        if state.risk_score >= state.escalate_threshold:
            return "ask_human"
        return "accept"
    if state.retry_count >= state.max_retries:
        return "stop_failed"
    if state.failure_is_localized:
        return "repair_patch"
    return "retrieve_more_context"


@dataclass
class ActionResult:
    action: str
    success: bool
    tokens_used: int
    output: str


class Controller:
    def __init__(self, state: AgentState) -> None:
        self.state = state
        self.history: list[ActionResult] = []
        self.actions_log: list[AgentAction] = []

    def step(self) -> str:
        action = next_action(self.state)
        return action

    def record(self, result: ActionResult, model: str = "stub") -> None:
        self.history.append(result)
        self.state.tokens_remaining -= result.tokens_used
        self.actions_log.append(
            AgentAction(
                action_type=result.action,
                timestamp=datetime.utcnow(),
                tokens_used=result.tokens_used,
                model=model,
                input_summary=f"action={result.action}",
                output_summary=result.output[:200] if result.output else "",
            )
        )

    def transition(self, **kwargs) -> None:
        for k, v in kwargs.items():
            if hasattr(self.state, k):
                setattr(self.state, k, v)
