from __future__ import annotations

import os
from datetime import datetime
from typing import Literal

from .diff_analyzer import get_changed_files
from .schemas import PatchResult, TaskSpec
from .utils import get_diff, read_file, token_estimate


class StubAgent:
    def __init__(self, patch_mode: Literal["safe", "unsafe"] = "safe") -> None:
        self.patch_mode = patch_mode
        self.model = "stub"

    def retrieve_context(self, task: TaskSpec) -> str:
        parts: list[str] = []
        try:
            parts.append(f"=== issue.md ===\n{read_file(task.issue_path)}")
        except OSError:
            pass
        for f in os.listdir(task.repo_path):
            if f.endswith(".py") and not f.startswith("test_"):
                full = os.path.join(task.repo_path, f)
                try:
                    parts.append(f"=== {f} ===\n{read_file(full)}")
                except OSError:
                    pass
        return "\n\n".join(parts)

    def generate_patch(
        self, task: TaskSpec, context: str, feedback: str | None = None
    ) -> PatchResult:
        patches_dir = os.path.join(task.repo_path, "patches")
        patch_file = os.path.join(patches_dir, f"{self.patch_mode}.py")
        patch_content = read_file(patch_file)

        # Determine the target source file
        source_files = [
            f for f in os.listdir(task.repo_path)
            if f.endswith(".py") and not f.startswith("test_")
        ]
        target_file = source_files[0] if source_files else "main.py"

        original_path = os.path.join(task.repo_path, target_file)
        try:
            original_content = read_file(original_path)
        except OSError:
            original_content = ""

        diff = get_diff(original_content, patch_content, target_file)
        files_changed = [target_file]

        # Multi-file unsafe patch: also diff the test file if unsafe_test.py exists
        test_patch_file = os.path.join(patches_dir, "unsafe_test.py")
        if self.patch_mode == "unsafe" and os.path.exists(test_patch_file):
            tests_dir = os.path.join(task.repo_path, "tests")
            if os.path.isdir(tests_dir):
                test_files = sorted(
                    f for f in os.listdir(tests_dir)
                    if f.startswith("test_") and f.endswith(".py")
                )
                if test_files:
                    test_filename = test_files[0]
                    test_original = read_file(os.path.join(tests_dir, test_filename))
                    test_patched = read_file(test_patch_file)
                    test_diff = get_diff(test_original, test_patched, f"tests/{test_filename}")
                    diff = diff + "\n" + test_diff
                    files_changed.append(f"tests/{test_filename}")

        added = sum(1 for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++"))
        removed = sum(1 for l in diff.splitlines() if l.startswith("-") and not l.startswith("---"))

        return PatchResult(
            patch_id=f"{task.task_id}_{self.patch_mode}_{datetime.utcnow().strftime('%H%M%S')}",
            files_changed=files_changed,
            lines_added=added,
            lines_removed=removed,
            diff=diff,
            applied_at=datetime.utcnow(),
        )

    def self_review(self, patch: PatchResult, task: TaskSpec) -> str:
        return f"[stub review] Patch for {task.task_id} in mode '{self.patch_mode}'. Diff size: {len(patch.diff)} chars."


class VLLMAgent:
    def __init__(
        self, base_url: str, model: str, api_key: str = "EMPTY"
    ) -> None:
        self.base_url = base_url
        self.model = model
        self.api_key = api_key
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        return self._client

    def retrieve_context(self, task: TaskSpec) -> str:
        from .prompts import CONTEXT_RETRIEVAL_PROMPT

        parts: list[str] = []
        all_files: list[str] = []
        try:
            parts.append(f"=== issue.md ===\n{read_file(task.issue_path)}")
        except OSError:
            pass
        for f in os.listdir(task.repo_path):
            if f.endswith(".py") and not f.startswith("test_"):
                full = os.path.join(task.repo_path, f)
                all_files.append(f)
                try:
                    parts.append(f"=== {f} ===\n{read_file(full)}")
                except OSError:
                    pass
        return "\n\n".join(parts)

    def generate_patch(
        self, task: TaskSpec, context: str, feedback: str | None = None
    ) -> PatchResult:
        from .prompts import PATCH_GENERATION_PROMPT, PATCH_WITH_FEEDBACK_PROMPT, SYSTEM_PROMPT

        issue = read_file(task.issue_path)
        source_files = [
            f for f in os.listdir(task.repo_path)
            if f.endswith(".py") and not f.startswith("test_")
        ]
        target_file = source_files[0] if source_files else "main.py"
        original_content = read_file(os.path.join(task.repo_path, target_file))

        if feedback:
            prompt = PATCH_WITH_FEEDBACK_PROMPT.format(
                issue=issue,
                filename=target_file,
                file_content=original_content,
                previous_patch="",
                failure_output=feedback,
            )
        else:
            prompt = PATCH_GENERATION_PROMPT.format(
                issue=issue,
                filename=target_file,
                file_content=original_content,
            )

        client = self._get_client()
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=2048,
        )
        patch_content = response.choices[0].message.content or ""

        diff = get_diff(original_content, patch_content, target_file)
        added = sum(1 for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++"))
        removed = sum(1 for l in diff.splitlines() if l.startswith("-") and not l.startswith("---"))

        return PatchResult(
            patch_id=f"{task.task_id}_vllm_{datetime.utcnow().strftime('%H%M%S')}",
            files_changed=[target_file],
            lines_added=added,
            lines_removed=removed,
            diff=diff,
            applied_at=datetime.utcnow(),
        )

    def self_review(self, patch: PatchResult, task: TaskSpec) -> str:
        from .prompts import SELF_REVIEW_PROMPT, SYSTEM_PROMPT

        prompt = SELF_REVIEW_PROMPT.format(diff=patch.diff)
        client = self._get_client()
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=512,
        )
        return response.choices[0].message.content or ""
