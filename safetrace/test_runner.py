from __future__ import annotations

import os
import re
import subprocess
import time

from .schemas import TestResult


def run_tests(repo_path: str, command: str = "pytest", timeout: int = 60) -> TestResult:
    start = time.time()
    try:
        result = subprocess.run(
            command.split(),
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout + result.stderr
        parsed = parse_pytest_output(output)
        duration = time.time() - start
        passed = result.returncode == 0
        return TestResult(
            passed=passed,
            tests_run=parsed["tests_run"],
            tests_passed=parsed["tests_passed"],
            tests_failed=parsed["tests_failed"],
            failure_output=output if not passed else None,
            duration_sec=round(duration, 3),
            command=command,
        )
    except subprocess.TimeoutExpired:
        duration = time.time() - start
        return TestResult(
            passed=False,
            tests_run=0,
            tests_passed=0,
            tests_failed=0,
            failure_output=f"Test timed out after {timeout}s",
            duration_sec=round(duration, 3),
            command=command,
        )
    except Exception as exc:
        duration = time.time() - start
        return TestResult(
            passed=False,
            tests_run=0,
            tests_passed=0,
            tests_failed=0,
            failure_output=str(exc),
            duration_sec=round(duration, 3),
            command=command,
        )


def parse_pytest_output(output: str) -> dict:
    tests_run = 0
    tests_passed = 0
    tests_failed = 0

    # Match lines like: "3 passed", "2 failed, 1 passed", "5 passed, 0 warnings"
    summary_pattern = re.compile(
        r"(\d+) passed|(\d+) failed|(\d+) error"
    )
    passed_match = re.search(r"(\d+) passed", output)
    failed_match = re.search(r"(\d+) failed", output)
    error_match = re.search(r"(\d+) error", output)

    if passed_match:
        tests_passed = int(passed_match.group(1))
    if failed_match:
        tests_failed += int(failed_match.group(1))
    if error_match:
        tests_failed += int(error_match.group(1))

    tests_run = tests_passed + tests_failed

    # Fallback: look for collected N items
    if tests_run == 0:
        collected = re.search(r"collected (\d+) item", output)
        if collected:
            tests_run = int(collected.group(1))
            tests_failed = tests_run
            tests_passed = 0

    return {
        "tests_run": tests_run,
        "tests_passed": tests_passed,
        "tests_failed": tests_failed,
    }


def apply_patch(repo_path: str, patch_content: str, target_file: str) -> bool:
    target_path = os.path.join(repo_path, target_file)
    try:
        with open(target_path, "w") as f:
            f.write(patch_content)
        return True
    except OSError:
        return False


def reset_repo(repo_path: str, original_files: dict[str, str]) -> None:
    for relative_path, content in original_files.items():
        full_path = os.path.join(repo_path, relative_path)
        try:
            with open(full_path, "w") as f:
                f.write(content)
        except OSError:
            pass
