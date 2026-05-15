"""Claude-based repair agent using the Anthropic API."""
from __future__ import annotations

import os
from datetime import datetime

from .schemas import PatchResult, TaskSpec
from .utils import get_diff, read_file


class ClaudeAgent:
    """Sends repair tasks to Claude and returns PatchResult diffs.

    Requires ANTHROPIC_API_KEY in the environment.
    """

    def __init__(self, model: str = "claude-opus-4-7") -> None:
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import anthropic
            except ImportError as exc:
                raise RuntimeError(
                    "anthropic package not installed. Run: pip install anthropic"
                ) from exc
            self._client = anthropic.Anthropic(
                api_key=os.environ.get("ANTHROPIC_API_KEY")
            )
        return self._client

    def retrieve_context(self, task: TaskSpec) -> str:
        parts: list[str] = []
        try:
            parts.append(f"=== issue.md ===\n{read_file(task.issue_path)}")
        except OSError:
            pass
        for f in sorted(os.listdir(task.repo_path)):
            if f.endswith(".py") and not f.startswith("test_"):
                try:
                    parts.append(f"=== {f} ===\n{read_file(os.path.join(task.repo_path, f))}")
                except OSError:
                    pass
        return "\n\n".join(parts)

    def generate_patch(
        self, task: TaskSpec, context: str, feedback: str | None = None
    ) -> PatchResult:
        issue = read_file(task.issue_path)
        src_files = sorted(
            f for f in os.listdir(task.repo_path)
            if f.endswith(".py") and not f.startswith("test_")
        )
        target_file = src_files[0] if src_files else "main.py"
        original = read_file(os.path.join(task.repo_path, target_file))

        prompt_parts = [
            "You are a careful software engineer fixing a bug.",
            "Return ONLY the complete corrected file — no explanation, no markdown fences.",
            "",
            f"Issue:\n{issue}",
            "",
            f"File to fix ({target_file}):\n{original}",
        ]
        if feedback:
            prompt_parts += ["", f"Your previous attempt failed tests:\n{feedback}"]

        client = self._get_client()
        message = client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": "\n".join(prompt_parts)}],
        )
        patch_content = message.content[0].text.strip()

        diff = get_diff(original, patch_content, target_file)
        added = sum(
            1 for l in diff.splitlines()
            if l.startswith("+") and not l.startswith("+++")
        )
        removed = sum(
            1 for l in diff.splitlines()
            if l.startswith("-") and not l.startswith("---")
        )

        return PatchResult(
            patch_id=f"{task.task_id}_claude_{datetime.utcnow().strftime('%H%M%S')}",
            files_changed=[target_file],
            lines_added=added,
            lines_removed=removed,
            diff=diff,
            applied_at=datetime.utcnow(),
        )

    def self_review(self, patch: PatchResult, task: TaskSpec) -> str:
        client = self._get_client()
        message = client.messages.create(
            model=self.model,
            max_tokens=512,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Review this code patch for security vulnerabilities. "
                        "Be concise.\n\n" + patch.diff
                    ),
                }
            ],
        )
        return message.content[0].text
