#!/usr/bin/env python3
"""Run a single agent on a single benchmark task."""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

# Allow running from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from safetrace import (
    FixedRetryPolicy,
    SafeTracePolicy,
    SingleShotPolicy,
    StubAgent,
    TestFeedbackPolicy,
    Tracer,
    VLLMAgent,
)
from safetrace.schemas import EvalResult
from safetrace.utils import load_tasks_json, setup_logging

app = typer.Typer()
console = Console()

POLICIES = {
    "single_shot": SingleShotPolicy,
    "fixed_retry": FixedRetryPolicy,
    "test_feedback": TestFeedbackPolicy,
    "safetrace": SafeTracePolicy,
}


def main():
    app()


@app.command()
def run(
    task: str = typer.Option(..., help="Path to task repo OR task_id from tasks.json"),
    tasks_json: Optional[str] = typer.Option(None, help="Path to tasks.json"),
    issue: Optional[str] = typer.Option(None, help="Path to issue.md (overrides tasks.json)"),
    policy: str = typer.Option("safetrace", help="Policy: single_shot|fixed_retry|test_feedback|safetrace"),
    budget_tokens: int = typer.Option(8000, help="Token budget for safetrace policy"),
    agent: str = typer.Option("stub", help="Agent type: stub|vllm"),
    patch_mode: str = typer.Option("unsafe", help="Patch mode for stub agent: safe|unsafe"),
    vllm_url: str = typer.Option("http://localhost:8000/v1", help="vLLM base URL"),
    model: str = typer.Option("qwen2.5-coder-32b", help="Model name"),
    output: str = typer.Option("results/", help="Output directory for traces"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    setup_logging(verbose)

    # Load task
    if tasks_json:
        tasks = load_tasks_json(tasks_json)
        task_spec = next((t for t in tasks if t.task_id == task), None)
        if task_spec is None:
            console.print(f"[red]Task '{task}' not found in {tasks_json}[/red]")
            raise typer.Exit(1)
    else:
        from safetrace.utils import load_task
        # Resolve relative path from project root
        task_path = task
        if not os.path.isabs(task_path):
            task_path = os.path.join(str(Path(__file__).parent.parent), task_path)
        task_spec = load_task(task_path)

    console.print(Panel(f"[bold]SafeTrace Agent Run[/bold]\nTask: {task_spec.task_id}\nPolicy: {policy}\nAgent: {agent} ({patch_mode})"))

    # Build agent
    if agent == "stub":
        agent_obj = StubAgent(patch_mode=patch_mode)
    elif agent == "vllm":
        agent_obj = VLLMAgent(base_url=vllm_url, model=model)
    else:
        console.print(f"[red]Unknown agent: {agent}[/red]")
        raise typer.Exit(1)

    # Build policy
    if policy == "single_shot":
        policy_obj = SingleShotPolicy()
    elif policy == "fixed_retry":
        policy_obj = FixedRetryPolicy()
    elif policy == "test_feedback":
        policy_obj = TestFeedbackPolicy()
    elif policy == "safetrace":
        policy_obj = SafeTracePolicy(budget_tokens=budget_tokens)
    else:
        console.print(f"[red]Unknown policy: {policy}[/red]")
        raise typer.Exit(1)

    # Read issue
    try:
        issue_text = open(task_spec.issue_path).read()
    except OSError:
        issue_text = ""

    tracer = Tracer(task_id=task_spec.task_id, policy=policy, issue=issue_text)
    tracer.set_model(agent_obj.model)

    console.print(f"\n[cyan]Running {policy} policy...[/cyan]")
    start = time.time()
    trace = policy_obj.run(agent_obj, task_spec, tracer)

    # Print results
    table = Table(title="Run Results")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")
    table.add_row("Task ID", trace.task_id)
    table.add_row("Final Status", f"[bold {'green' if trace.final_status == 'safe' else 'red'}]{trace.final_status}[/bold {'green' if trace.final_status == 'safe' else 'red'}]")
    table.add_row("Tests Passed", str(trace.tests_passed))
    table.add_row("Tests Run", str(trace.tests_run))
    table.add_row("Risk Score", str(trace.risk_score))
    table.add_row("Monitor Decision", trace.monitor_decision)
    table.add_row("Safety Flags", ", ".join(trace.safety_flags) or "none")
    table.add_row("Tokens Used", str(trace.tokens_used))
    table.add_row("Wall Time", f"{trace.wall_time_sec:.2f}s")
    table.add_row("Human Review Required", str(trace.human_review_required))
    console.print(table)

    # Write trace
    os.makedirs(output, exist_ok=True)
    trace_path = os.path.join(output, f"{task_spec.task_id}_{policy}_{patch_mode}_trace.json")
    tracer.write_trace(trace, trace_path)
    console.print(f"\n[green]Trace written to:[/green] {trace_path}")

    # Build eval result
    eval_result = EvalResult(
        task_id=trace.task_id,
        category=task_spec.category,
        policy=policy,
        model=agent_obj.model,
        patch_mode=patch_mode,
        tests_passed=trace.tests_passed > 0,
        tests_run=trace.tests_run,
        retry_count=trace.retry_count,
        risk_score=trace.risk_score,
        monitor_decision=trace.monitor_decision,
        final_status=trace.final_status,
        human_review_required=trace.human_review_required,
        safety_flags="|".join(trace.safety_flags),
        flagged_categories="|".join(trace.safety_flags),
        tokens_used=trace.tokens_used,
        wall_time_sec=trace.wall_time_sec,
        lines_changed=trace.lines_changed,
        files_changed="|".join(trace.files_changed),
        monitor_recall_hit=len(trace.safety_flags) > 0 and patch_mode == "unsafe",
        expected_flags_hit=any(f in trace.safety_flags for f in task_spec.expected_monitor_flags),
    )
    csv_path = os.path.join(output, "main_results.csv")
    tracer.append_to_csv(eval_result, csv_path)
    console.print(f"[green]Result appended to:[/green] {csv_path}")


if __name__ == "__main__":
    main()
