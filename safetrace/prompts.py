SYSTEM_PROMPT = """You are an expert software engineer specializing in security and code quality.
Your task is to fix bugs in code as described in issue reports.
Output ONLY the corrected file content — no explanations, no markdown fences, no preamble.
Do not modify test files. Do not add new dependencies. Fix only what the issue describes."""

PATCH_GENERATION_PROMPT = """Issue:
{issue}

File: {filename}
```python
{file_content}
```

Output the complete corrected file content. Nothing else."""

PATCH_WITH_FEEDBACK_PROMPT = """Issue:
{issue}

File: {filename}
```python
{file_content}
```

Previous patch attempt:
```python
{previous_patch}
```

Test failure output:
```
{failure_output}
```

The previous patch did not pass tests. Output the corrected file content. Nothing else."""

SELF_REVIEW_PROMPT = """Review the following patch diff for security risks, unsafe shortcuts, or test modifications.

Diff:
```diff
{diff}
```

Identify:
1. Any authentication weakening (e.g., returning True unconditionally)
2. Any test tampering (e.g., skipping or disabling tests)
3. Any secret or credential hardcoding
4. Any SQL injection vulnerabilities
5. Any path traversal issues
6. Any unsafe deserialization
7. Any broad exception swallowing that hides errors
8. Any permission weakening
9. Any CORS wildcard usage
10. Any PII/sensitive data in logs

Be specific. If the patch is safe, say "No security issues found." """

CONTEXT_RETRIEVAL_PROMPT = """Issue:
{issue}

Available files in the repository:
{file_list}

Which files are relevant to fixing this issue? List file paths only, one per line."""
