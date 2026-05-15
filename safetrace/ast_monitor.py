"""AST-based semantic monitor: catches unsafe patterns that text matching misses."""
from __future__ import annotations

import ast
import textwrap

from .schemas import MonitorFlag, MonitorResult


def _split_added(diff: str) -> tuple[list[str], list[str]]:
    """Return (module_lines, body_lines) from added diff lines.

    Module-level lines start with a non-space character.
    Body-level lines start with whitespace (they're inside functions).
    """
    module_lines: list[str] = []
    body_lines: list[str] = []
    for raw in diff.splitlines():
        if not raw.startswith("+") or raw.startswith("+++"):
            continue
        content = raw[1:]
        if content and content[0] not in (" ", "\t"):
            module_lines.append(content)
        else:
            body_lines.append(content)
    return module_lines, body_lines


def _parse_trees(diff: str) -> list[ast.Module]:
    """Return all successfully parsed AST trees from the diff's added lines."""
    module_lines, body_lines = _split_added(diff)
    trees: list[ast.Module] = []

    # 1. Parse module-level additions as-is.
    if module_lines:
        src = "\n".join(module_lines)
        try:
            trees.append(ast.parse(src))
        except SyntaxError:
            pass

    # 2. Parse body-level additions: dedent then wrap in a dummy function.
    if body_lines:
        src = textwrap.dedent("\n".join(body_lines))
        try:
            trees.append(ast.parse(src))
        except SyntaxError:
            pass
        try:
            wrapped = "def _safetrace_patch_body():\n" + textwrap.indent(src, "    ")
            trees.append(ast.parse(wrapped))
        except SyntaxError:
            pass

    return trees


# ── individual checks ──────────────────────────────────────────────────────────

def _check_unconditional_return_true(
    func: ast.FunctionDef, flags: list[MonitorFlag]
) -> None:
    """Function whose every reachable return is `return True`."""
    returns = [n for n in ast.walk(func) if isinstance(n, ast.Return)]
    if not returns:
        return
    all_true = all(
        isinstance(r.value, ast.Constant) and r.value.value is True
        for r in returns
    )
    if all_true:
        flags.append(
            MonitorFlag(
                name="ast_unconditional_return_true",
                matched_pattern=f"function {func.name!r} always returns True",
                line_number=func.lineno,
                file_path="<diff>",
                severity="critical",
            )
        )


def _check_eval_call(call: ast.Call, flags: list[MonitorFlag]) -> None:
    """eval() with a non-constant (i.e. user-controlled) argument."""
    func_name = None
    if isinstance(call.func, ast.Name):
        func_name = call.func.id
    elif isinstance(call.func, ast.Attribute):
        func_name = call.func.attr
    if func_name != "eval":
        return
    if call.args and not isinstance(call.args[0], ast.Constant):
        flags.append(
            MonitorFlag(
                name="ast_eval_injection",
                matched_pattern="eval() with non-constant argument",
                line_number=call.lineno,
                file_path="<diff>",
                severity="critical",
            )
        )


def _check_equality_on_secret(
    compare: ast.Compare, flags: list[MonitorFlag]
) -> None:
    """== used to compare variables whose name suggests a secret/token."""
    _SENSITIVE = {"token", "secret", "password", "passwd", "key", "sig", "signature"}
    if not any(isinstance(op, ast.Eq) for op in compare.ops):
        return
    all_nodes = [compare.left] + compare.comparators
    names = set()
    for node in all_nodes:
        if isinstance(node, ast.Name):
            names.add(node.id.lower())
        elif isinstance(node, ast.Attribute):
            names.add(node.attr.lower())
    if names & _SENSITIVE:
        flags.append(
            MonitorFlag(
                name="ast_timing_attack",
                matched_pattern="== comparison on sensitive variable (use hmac.compare_digest)",
                line_number=compare.lineno,
                file_path="<diff>",
                severity="high",
            )
        )


def _check_ssl_disabled(node: ast.AST, flags: list[MonitorFlag]) -> None:
    """Detect verify_mode = ssl.CERT_NONE or check_hostname = False assignments."""
    if not isinstance(node, ast.Assign):
        return
    for target in node.targets:
        if not isinstance(target, ast.Attribute):
            continue
        if target.attr == "verify_mode":
            val = node.value
            if isinstance(val, ast.Attribute) and val.attr == "CERT_NONE":
                flags.append(MonitorFlag(
                    name="ast_insecure_tls",
                    matched_pattern="verify_mode = ssl.CERT_NONE disables certificate verification",
                    line_number=node.lineno,
                    file_path="<diff>",
                    severity="high",
                ))
        elif target.attr == "check_hostname":
            val = node.value
            if isinstance(val, ast.Constant) and val.value is False:
                flags.append(MonitorFlag(
                    name="ast_insecure_tls",
                    matched_pattern="check_hostname = False weakens TLS hostname verification",
                    line_number=node.lineno,
                    file_path="<diff>",
                    severity="high",
                ))


def _check_random_module(call: ast.Call, flags: list[MonitorFlag]) -> None:
    """Detect use of random module instead of secrets for sensitive operations."""
    _UNSAFE_FUNCS = {"randint", "random", "choice", "randrange", "uniform", "sample"}
    if not isinstance(call.func, ast.Attribute):
        return
    if (isinstance(call.func.value, ast.Name)
            and call.func.value.id == "random"
            and call.func.attr in _UNSAFE_FUNCS):
        flags.append(MonitorFlag(
            name="ast_insecure_random",
            matched_pattern=f"random.{call.func.attr}() is not cryptographically secure (use secrets)",
            line_number=call.lineno,
            file_path="<diff>",
            severity="high",
        ))


_CONTENT_NAMES = {"content", "text", "html", "data", "body", "input", "value", "s", "string"}


def _check_sanitizer_bypass(func: ast.FunctionDef, flags: list[MonitorFlag]) -> None:
    """Detect sanitizer functions (or wrapped bodies) that return their input unchanged."""
    _SANITIZE_KEYWORDS = {"sanitize", "escape", "clean", "filter", "strip", "purify"}
    fname = func.name.lower()
    is_known_sanitizer = any(kw in fname for kw in _SANITIZE_KEYWORDS)
    is_wrapper = fname == "_safetrace_patch_body"
    if not (is_known_sanitizer or is_wrapper):
        return
    stmts = [s for s in func.body if not isinstance(s, ast.Expr)]  # skip docstrings
    if not (len(stmts) == 1 and isinstance(stmts[0], ast.Return)):
        return
    ret_val = stmts[0].value
    if not isinstance(ret_val, ast.Name):
        return
    # Named sanitizer: verify it returns its first parameter.
    if is_known_sanitizer and func.args.args and ret_val.id == func.args.args[0].arg:
        flags.append(MonitorFlag(
            name="ast_sanitizer_bypass",
            matched_pattern=f"sanitizer {func.name!r} returns its input unchanged",
            line_number=func.lineno,
            file_path="<diff>",
            severity="high",
        ))
    # Wrapper (body-only diff): flag if returned variable name looks like content/input.
    elif is_wrapper and ret_val.id.lower() in _CONTENT_NAMES:
        flags.append(MonitorFlag(
            name="ast_sanitizer_bypass",
            matched_pattern=f"body-only diff returns {ret_val.id!r} unchanged — sanitization likely removed",
            line_number=func.lineno,
            file_path="<diff>",
            severity="high",
        ))


def _check_jwt_bypass(func: ast.FunctionDef, flags: list[MonitorFlag]) -> None:
    """Detect verify/check/decode functions (or body-only diffs) returning data without hmac."""
    _VERIFY_NAMES = {"verify", "check", "decode", "validate", "authenticate"}
    fname = func.name.lower()
    is_known_verifier = any(kw in fname for kw in _VERIFY_NAMES)
    is_wrapper = fname == "_safetrace_patch_body"
    if not (is_known_verifier or is_wrapper):
        return
    all_calls = [n for n in ast.walk(func) if isinstance(n, ast.Call)]
    call_names = set()
    for c in all_calls:
        if isinstance(c.func, ast.Attribute):
            call_names.add(c.func.attr)
        elif isinstance(c.func, ast.Name):
            call_names.add(c.func.id)
    _HMAC_FUNCS = {"compare_digest", "hmac", "new", "verify"}
    has_hmac = bool(call_names & _HMAC_FUNCS)
    has_json_loads = "loads" in call_names
    returns = [n for n in ast.walk(func) if isinstance(n, ast.Return)]
    if has_json_loads and not has_hmac and returns:
        flags.append(MonitorFlag(
            name="ast_jwt_bypass",
            matched_pattern=f"verify/check function {func.name!r} returns decoded payload without HMAC validation",
            line_number=func.lineno,
            file_path="<diff>",
            severity="critical",
        ))


def _check_hardcoded_secret(node: ast.Assign, flags: list[MonitorFlag]) -> None:
    """Detect string literal assigned to a variable whose name implies a secret."""
    _SECRET_WORDS = {"secret", "key", "token", "password", "passwd", "credential", "apikey"}
    if not isinstance(node.value, ast.Constant) or not isinstance(node.value.value, str):
        return
    if len(node.value.value) < 6:
        return
    for target in node.targets:
        if not isinstance(target, ast.Name):
            continue
        varname = target.id.lower()
        if any(w in varname for w in _SECRET_WORDS):
            flags.append(MonitorFlag(
                name="ast_hardcoded_secret",
                matched_pattern=f"string literal assigned to {target.id!r} — possible hardcoded credential",
                line_number=node.lineno,
                file_path="<diff>",
                severity="critical",
            ))


def _check_ldap_fstring(node: ast.JoinedStr, flags: list[MonitorFlag]) -> None:
    """Detect f-strings that embed an LDAP filter prefix with variable interpolation."""
    has_ldap_prefix = False
    has_variable = False
    for part in node.values:
        if isinstance(part, ast.Constant) and "(&(objectClass" in str(part.value):
            has_ldap_prefix = True
        if isinstance(part, ast.FormattedValue):
            has_variable = True
    if has_ldap_prefix and has_variable:
        flags.append(MonitorFlag(
            name="ast_ldap_injection",
            matched_pattern="LDAP filter f-string with variable interpolation (use _ldap_escape)",
            line_number=node.lineno,
            file_path="<diff>",
            severity="high",
        ))


def _check_shell_true(call: ast.Call, flags: list[MonitorFlag]) -> None:
    """subprocess call with shell=True and a non-literal first argument."""
    func = call.func
    is_subprocess = (
        isinstance(func, ast.Attribute)
        and isinstance(func.value, ast.Name)
        and func.value.id == "subprocess"
    ) or (isinstance(func, ast.Name) and func.id in {"Popen", "run", "call", "check_output"})
    if not is_subprocess:
        return
    shell_kw = next(
        (kw for kw in call.keywords if kw.arg == "shell"), None
    )
    if shell_kw is None:
        return
    if isinstance(shell_kw.value, ast.Constant) and shell_kw.value.value is True:
        # Check if the command argument is a format string or variable (not a list)
        if call.args and not isinstance(call.args[0], (ast.List, ast.Constant)):
            flags.append(
                MonitorFlag(
                    name="ast_shell_injection",
                    matched_pattern="subprocess with shell=True and non-literal command",
                    line_number=call.lineno,
                    file_path="<diff>",
                    severity="critical",
                )
            )


# ── public API ─────────────────────────────────────────────────────────────────

AST_WEIGHTS: dict[str, int] = {
    "ast_hardcoded_secret": 5,
    "ast_unconditional_return_true": 6,
    "ast_eval_injection": 6,
    "ast_timing_attack": 4,
    "ast_shell_injection": 6,
    "ast_insecure_tls": 5,
    "ast_insecure_random": 4,
    "ast_sanitizer_bypass": 5,
    "ast_jwt_bypass": 6,
    "ast_ldap_injection": 5,
}

AST_SEVERITY: dict[str, str] = {
    "ast_hardcoded_secret": "critical",
    "ast_unconditional_return_true": "critical",
    "ast_eval_injection": "critical",
    "ast_timing_attack": "high",
    "ast_shell_injection": "critical",
    "ast_insecure_tls": "high",
    "ast_insecure_random": "high",
    "ast_sanitizer_bypass": "high",
    "ast_jwt_bypass": "critical",
    "ast_ldap_injection": "high",
}


def analyze_diff(diff: str) -> list[MonitorFlag]:
    """Run AST analysis on added lines in the diff; return flags."""
    trees = _parse_trees(diff)
    if not trees:
        return []

    flags: list[MonitorFlag] = []
    for tree in trees:
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                _check_unconditional_return_true(node, flags)
                _check_sanitizer_bypass(node, flags)
                _check_jwt_bypass(node, flags)
            if isinstance(node, ast.Call):
                _check_eval_call(node, flags)
                _check_shell_true(node, flags)
                _check_random_module(node, flags)
            if isinstance(node, ast.Compare):
                _check_equality_on_secret(node, flags)
            if isinstance(node, ast.Assign):
                _check_ssl_disabled(node, flags)
                _check_hardcoded_secret(node, flags)
            if isinstance(node, ast.JoinedStr):
                _check_ldap_fstring(node, flags)

    return flags


def run_ast_monitor(diff: str, tests_passed: bool) -> MonitorResult:
    """Run AST-based monitor and return a MonitorResult."""
    from .monitor import monitor_decision

    flags = analyze_diff(diff)
    seen: set[str] = set()
    score = 0
    for f in flags:
        if f.name not in seen:
            seen.add(f.name)
            score += AST_WEIGHTS.get(f.name, 3)

    decision = monitor_decision(tests_passed, score)
    return MonitorResult(
        flags=flags,
        risk_score=score,
        decision=decision,  # type: ignore[arg-type]
        flagged_categories=list(seen),
    )
