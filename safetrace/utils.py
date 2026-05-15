from __future__ import annotations

import difflib
import logging
import os

from rich.logging import RichHandler

from .schemas import TaskSpec


def load_task(task_path: str) -> TaskSpec:
    issue_path = os.path.join(task_path, "issue.md")
    task_id = os.path.basename(task_path.rstrip("/"))

    # Infer source file
    source_files = [
        f for f in os.listdir(task_path)
        if f.endswith(".py") and not f.startswith("test_")
    ]
    main_source = source_files[0] if source_files else "main.py"

    return TaskSpec(
        task_id=task_id,
        category=task_id.rsplit("_", 1)[0],
        repo_path=task_path,
        issue_path=issue_path,
        test_command=f"pytest tests/ -v",
        visible_tests=[os.path.join("tests", f) for f in os.listdir(os.path.join(task_path, "tests")) if f.endswith(".py")],
        hidden_safety_invariant="",
        unsafe_shortcut="",
        safe_fix_description="",
        risk_labels=[],
        expected_monitor_flags=[],
    )


def load_tasks_json(tasks_json_path: str) -> list[TaskSpec]:
    import json
    with open(tasks_json_path) as f:
        data = json.load(f)
    return [TaskSpec(**item) for item in data]


def get_diff(original: str, modified: str, filename: str) -> str:
    original_lines = original.splitlines(keepends=True)
    modified_lines = modified.splitlines(keepends=True)
    diff = difflib.unified_diff(
        original_lines,
        modified_lines,
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
    )
    return "".join(diff)


def read_file(path: str) -> str:
    with open(path) as f:
        return f.read()


def write_file(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def token_estimate(text: str) -> int:
    return len(text) // 4


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )
