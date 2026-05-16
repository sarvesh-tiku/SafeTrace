from __future__ import annotations

import re
from typing import Optional


def parse_diff(diff: str) -> dict:
    result: dict = {"files": {}, "total_added": 0, "total_removed": 0}
    current_file: Optional[str] = None

    for line in diff.splitlines():
        if line.startswith("+++ "):
            fname = line[4:]
            if fname.startswith("b/"):
                fname = fname[2:]
            current_file = fname.strip()
            if current_file not in result["files"]:
                result["files"][current_file] = {"added": 0, "removed": 0, "hunks": 0}
        elif line.startswith("@@ "):
            if current_file:
                result["files"][current_file]["hunks"] += 1
        elif line.startswith("+") and not line.startswith("+++"):
            result["total_added"] += 1
            if current_file:
                result["files"][current_file]["added"] += 1
        elif line.startswith("-") and not line.startswith("---"):
            result["total_removed"] += 1
            if current_file:
                result["files"][current_file]["removed"] += 1

    return result


def get_changed_files(diff: str) -> list[str]:
    files: list[str] = []
    for line in diff.splitlines():
        if line.startswith("+++ "):
            fname = line[4:]
            if fname.startswith("b/"):
                fname = fname[2:]
            fname = fname.strip()
            if fname and fname != "/dev/null":
                files.append(fname)
    return files


def is_test_file_modified(diff: str) -> bool:
    for f in get_changed_files(diff):
        if "tests/" in f or f.startswith("test_") or "/test_" in f:
            return True
    return False


def get_added_lines(diff: str) -> list[tuple[str, int, str]]:
    results: list[tuple[str, int, str]] = []
    current_file = "unknown"
    current_line = 0

    for raw_line in diff.splitlines():
        if raw_line.startswith("+++ "):
            fname = raw_line[4:]
            if fname.startswith("b/"):
                fname = fname[2:]
            current_file = fname.strip()
            continue
        if raw_line.startswith("--- "):
            continue
        if raw_line.startswith("@@ "):
            try:
                hunk_info = raw_line.split("+")[1].split("@@")[0].strip()
                start = hunk_info.split(",")[0]
                current_line = int(start) - 1
            except (IndexError, ValueError):
                current_line = 0
            continue
        if raw_line.startswith("+") and not raw_line.startswith("+++"):
            current_line += 1
            results.append((current_file, current_line, raw_line[1:]))
        elif raw_line.startswith("-") and not raw_line.startswith("---"):
            pass
        else:
            current_line += 1

    return results


def summarize_diff(diff: str) -> str:
    info = parse_diff(diff)
    files = list(info["files"].keys())
    total_added = info["total_added"]
    total_removed = info["total_removed"]
    file_list = ", ".join(files) if files else "no files"
    return (
        f"The diff modifies {len(files)} file(s): {file_list}. "
        f"A total of {total_added} line(s) were added and {total_removed} line(s) were removed. "
        f"This represents a net change of {total_added - total_removed} lines across the patch."
    )
