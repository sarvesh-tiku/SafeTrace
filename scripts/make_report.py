#!/usr/bin/env python3
"""Generate a Markdown + LaTeX report from evaluation results."""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import typer
from rich.console import Console

app = typer.Typer()
console = Console()


def main():
    app()


def _pct(num: int | float, denom: int | float) -> str:
    if denom == 0:
        return "N/A"
    return f"{num / denom:.1%}"


def _latex_escape(s: str) -> str:
    return s.replace("_", r"\_").replace("%", r"\%").replace("&", r"\&")


# ── markdown helpers ───────────────────────────────────────────────────────────

def _md_policy_table(rows: list[dict], patch_mode: str) -> list[str]:
    lines = ["| Policy | Tests Pass | Monitor Recall | Blocked | Escalated | Safe Accepted |\n",
             "|--------|-----------|----------------|---------|-----------|---------------|\n"]
    for pol in sorted(set(r["policy"] for r in rows)):
        pol_rows = [r for r in rows if r["policy"] == pol]
        unsafe_rows = [r for r in pol_rows if r.get("patch_mode") == "unsafe"]
        pass_rate = sum(1 for r in pol_rows if r["tests_passed"].lower() == "true") / max(len(pol_rows), 1)
        recall = sum(1 for r in unsafe_rows if r.get("safety_flags")) / max(len(unsafe_rows), 1)
        blocked = sum(1 for r in pol_rows if r.get("final_status") == "blocked")
        escalated = sum(1 for r in pol_rows if r.get("final_status") == "escalated")
        accepted = sum(1 for r in unsafe_rows if r.get("final_status") in ("safe", "unsafe_success_flagged"))
        lines.append(
            f"| {pol} | {pass_rate:.1%} | {_pct(recall * len(unsafe_rows), len(unsafe_rows))} "
            f"| {blocked} | {escalated} | {accepted}/{len(unsafe_rows)} |\n"
        )
    return lines


def _md_category_table(rows: list[dict]) -> list[str]:
    unsafe_rows = [r for r in rows if r.get("patch_mode") == "unsafe" and r.get("policy") == "safetrace"]
    cats: dict[str, dict] = {}
    for r in unsafe_rows:
        cat = r.get("category", "unknown")
        d = cats.setdefault(cat, {"flagged": 0, "total": 0, "status": []})
        d["total"] += 1
        d["flagged"] += 1 if r.get("safety_flags") else 0
        d["status"].append(r.get("final_status", ""))
    lines = ["| Category | Recall | Final Status |\n",
             "|----------|--------|-------------|\n"]
    for cat in sorted(cats):
        d = cats[cat]
        status_str = ", ".join(set(d["status"]))
        lines.append(f"| {cat} | {_pct(d['flagged'], d['total'])} | {status_str} |\n")
    return lines


# ── LaTeX helpers ──────────────────────────────────────────────────────────────

def _latex_policy_table(rows: list[dict]) -> str:
    policies = sorted(set(r["policy"] for r in rows))
    body_rows = []
    for pol in policies:
        pol_rows = [r for r in rows if r["policy"] == pol]
        unsafe_rows = [r for r in pol_rows if r.get("patch_mode") == "unsafe"]
        pass_rate = sum(1 for r in pol_rows if r["tests_passed"].lower() == "true") / max(len(pol_rows), 1)
        recall = sum(1 for r in unsafe_rows if r.get("safety_flags")) / max(len(unsafe_rows), 1)
        blocked = sum(1 for r in pol_rows if r.get("final_status") == "blocked")
        escalated = sum(1 for r in pol_rows if r.get("final_status") == "escalated")
        mean_tok = sum(int(r.get("tokens_used", 0)) for r in pol_rows) / max(len(pol_rows), 1)
        body_rows.append(
            f"    {_latex_escape(pol)} & {pass_rate:.0%} & {recall:.0%} "
            f"& {blocked} & {escalated} & {mean_tok:.0f} \\\\"
        )

    return r"""
\begin{table}[ht]
\centering
\caption{SafeTrace policy comparison across """ + str(len(set(r["task_id"] for r in rows))) + r""" benchmark tasks.}
\label{tab:policy_comparison}
\begin{tabular}{lrrrrr}
\toprule
Policy & Tests Pass & Recall & Blocked & Escalated & Avg Tokens \\
\midrule
""" + "\n".join(body_rows) + r"""
\bottomrule
\end{tabular}
\end{table}
"""


def _latex_monitor_table(monitor_json: str) -> str:
    if not os.path.exists(monitor_json):
        return "% monitor_comparison.json not found — run compare_monitors.py\n"
    with open(monitor_json) as f:
        data = json.load(f)
    valid = [d for d in data if "error" not in d]
    body_rows = []
    for d in valid:
        body_rows.append(
            f"    {_latex_escape(d['name'])} & {d['precision']:.3f} "
            f"& {d['recall']:.3f} & {d['f1']:.3f} & {d['tp']} & {d['fp']} & {d['fn']} \\\\"
        )
    return r"""
\begin{table}[ht]
\centering
\caption{Monitor comparison on SafeTrace benchmark (""" + str(sum(1 for d in valid if "TP" in str(d))) + r""" diffs).}
\label{tab:monitor_comparison}
\begin{tabular}{lrrrrrr}
\toprule
Monitor & Precision & Recall & F1 & TP & FP & FN \\
\midrule
""" + "\n".join(body_rows) + r"""
\bottomrule
\end{tabular}
\end{table}
"""


# ── main ───────────────────────────────────────────────────────────────────────

@app.command()
def report(
    input: str = typer.Option("results/main_results.csv", help="Input CSV path"),
    monitor_json: str = typer.Option("results/monitor_comparison.json"),
    traces_dir: str = typer.Option("results/", help="Directory with trace JSON files"),
    output: str = typer.Option("results/summary.md", help="Output markdown path"),
    latex: str = typer.Option("results/tables.tex", help="Output LaTeX tables path"),
):
    root = Path(__file__).parent.parent
    input_path = input if os.path.isabs(input) else str(root / input)
    monitor_json_path = monitor_json if os.path.isabs(monitor_json) else str(root / monitor_json)
    output_path = output if os.path.isabs(output) else str(root / output)
    latex_path = latex if os.path.isabs(latex) else str(root / latex)

    with open(input_path) as f:
        rows = list(csv.DictReader(f))

    policies = sorted(set(r["policy"] for r in rows))
    n_tasks = len(set(r["task_id"] for r in rows))

    # ── Markdown ──
    md: list[str] = []
    md.append("# SafeTrace Evaluation Report\n\n")
    md.append(f"**Tasks:** {n_tasks}  \n")
    md.append(f"**Total runs:** {len(rows)}  \n")
    md.append(f"**Policies:** {', '.join(policies)}  \n\n")

    md.append("## Policy Comparison\n\n")
    patch_mode = rows[0].get("patch_mode", "unsafe") if rows else "unsafe"
    md.extend(_md_policy_table(rows, patch_mode))
    md.append("\n")

    md.append("## Per-Category Recall (SafeTrace)\n\n")
    md.extend(_md_category_table(rows))
    md.append("\n")

    if os.path.exists(monitor_json_path):
        with open(monitor_json_path) as f:
            mon_data = json.load(f)
        md.append("## Monitor Comparison\n\n")
        md.append("| Monitor | Precision | Recall | F1 | TP | FP | FN |\n")
        md.append("|---------|-----------|--------|----|----|----|----|\n")
        for d in mon_data:
            if "error" not in d:
                md.append(
                    f"| {d['name']} | {d['precision']:.3f} | {d['recall']:.3f} "
                    f"| {d['f1']:.3f} | {d['tp']} | {d['fp']} | {d['fn']} |\n"
                )
        md.append("\n")

    md.append("## Key Findings\n\n")
    st_unsafe = [r for r in rows if r["policy"] == "safetrace" and r.get("patch_mode") == "unsafe"]
    if st_unsafe:
        flagged = sum(1 for r in st_unsafe if r.get("safety_flags"))
        blocked = sum(1 for r in st_unsafe if r.get("final_status") == "blocked")
        escalated = sum(1 for r in st_unsafe if r.get("final_status") == "escalated")
        accepted = sum(1 for r in st_unsafe if r.get("final_status") in ("safe", "unsafe_success_flagged"))
        md.append(f"- SafeTrace flagged **{flagged}/{len(st_unsafe)}** ({_pct(flagged, len(st_unsafe))}) unsafe patches.\n")
        md.append(f"- **{blocked}** patches blocked outright; **{escalated}** escalated to human review.\n")
        md.append(f"- **{accepted}** unsafe patches were accepted (flagged but score below thresholds).\n")

    # Trace examples
    md.append("\n## Unsafe Patch Examples\n\n")
    trace_files = sorted(
        f for f in os.listdir(traces_dir)
        if f.endswith("_trace.json") and "unsafe" in f
    )
    shown = 0
    for tf in trace_files[:5]:
        try:
            with open(os.path.join(traces_dir, tf)) as f:
                trace = json.load(f)
            if trace.get("safety_flags"):
                md.append(f"### {trace['task_id']} — {trace.get('final_status', '?')}\n\n")
                md.append(f"- **Risk score:** {trace.get('risk_score', 0)}\n")
                md.append(f"- **Flags:** {', '.join(trace['safety_flags'])}\n")
                md.append(f"- **Decision:** {trace.get('monitor_decision', '?')}\n\n")
                shown += 1
        except (OSError, json.JSONDecodeError):
            pass
    if shown == 0:
        md.append("_No trace files found — re-run with `--output results/`._\n")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.writelines(md)
    console.print(f"[green]Markdown report → {output_path}[/green]")

    # ── LaTeX ──
    tex_parts = [
        "% SafeTrace LaTeX Tables — generated by make_report.py\n",
        "% Requires: booktabs\n\n",
        _latex_policy_table(rows),
        _latex_monitor_table(monitor_json_path),
    ]
    with open(latex_path, "w") as f:
        f.writelines(tex_parts)
    console.print(f"[green]LaTeX tables → {latex_path}[/green]")


if __name__ == "__main__":
    main()
