"""Generate charts from evaluation results.

Outputs:
  results/figures/monitor_comparison.png  — bar chart of monitor metrics
  results/figures/per_category.png        — recall heatmap by vulnerability category
  results/figures/roc_curve.png           — ROC curve for learned monitor (LOO-CV)
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _require_matplotlib():
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        return plt
    except ImportError:
        print("matplotlib not installed. Run: pip install matplotlib", file=sys.stderr)
        sys.exit(1)


def plot_monitor_comparison(results_json: str, out_dir: str) -> None:
    plt = _require_matplotlib()
    import matplotlib.pyplot as plt_mod

    with open(results_json) as f:
        data = json.load(f)

    valid = [d for d in data if "error" not in d]
    if not valid:
        print("No valid monitor results to plot.")
        return

    names = [d["name"] for d in valid]
    precisions = [d["precision"] for d in valid]
    recalls = [d["recall"] for d in valid]
    f1s = [d["f1"] for d in valid]

    x = list(range(len(names)))
    width = 0.25

    fig, ax = plt_mod.subplots(figsize=(max(8, len(names) * 1.5), 5))
    ax.bar([i - width for i in x], precisions, width, label="Precision", color="#4C72B0")
    ax.bar(x, recalls, width, label="Recall", color="#DD8452")
    ax.bar([i + width for i in x], f1s, width, label="F1", color="#55A868")

    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=20, ha="right", fontsize=9)
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Score")
    ax.set_title("SafeTrace Monitor Comparison")
    ax.legend()
    ax.axhline(1.0, color="gray", linestyle="--", linewidth=0.8, alpha=0.5)

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "monitor_comparison.png")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt_mod.close(fig)
    print(f"Saved → {out_path}")


def plot_per_category(csv_path: str, out_dir: str) -> None:
    plt = _require_matplotlib()
    import csv as csv_mod
    import matplotlib.pyplot as plt_mod

    with open(csv_path) as f:
        rows = list(csv_mod.DictReader(f))

    unsafe_rows = [r for r in rows if r.get("patch_mode") == "unsafe" and r.get("policy") == "safetrace"]
    if not unsafe_rows:
        print("No safetrace unsafe rows found for per-category chart.")
        return

    categories: dict[str, list[int]] = {}
    for row in unsafe_rows:
        cat = row.get("category", "unknown")
        flagged = 1 if row.get("safety_flags") else 0
        categories.setdefault(cat, []).append(flagged)

    cats = sorted(categories)
    recalls = [sum(v) / len(v) for v in [categories[c] for c in cats]]

    fig, ax = plt_mod.subplots(figsize=(max(8, len(cats) * 0.9), 4))
    colors = ["#55A868" if r == 1.0 else "#DD8452" if r >= 0.5 else "#C44E52" for r in recalls]
    ax.barh(cats, recalls, color=colors)
    ax.set_xlim(0, 1.1)
    ax.set_xlabel("Monitor Recall")
    ax.set_title("Per-Category Monitor Recall (SafeTrace Policy)")
    ax.axvline(1.0, color="gray", linestyle="--", linewidth=0.8, alpha=0.5)

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "per_category.png")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt_mod.close(fig)
    print(f"Saved → {out_path}")


def plot_roc_curve(tasks_json: str, repos_base: str, out_dir: str) -> None:
    """LOO-CV ROC curve for the sklearn learned monitor."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import roc_auc_score, roc_curve
    except ImportError:
        print("scikit-learn not installed — skipping ROC curve.")
        return

    plt = _require_matplotlib()
    import matplotlib.pyplot as plt_mod
    import json as _json

    with open(tasks_json) as f:
        tasks = _json.load(f)

    from safetrace.utils import get_diff, read_file

    diffs, labels = [], []
    for task in tasks:
        task_id = task["task_id"]
        repo_path = os.path.join(repos_base, task_id)
        patches_dir = os.path.join(repo_path, "patches")
        src_files = sorted(
            f for f in os.listdir(repo_path)
            if f.endswith(".py") and not f.startswith("test_")
        )
        if not src_files:
            continue
        original = read_file(os.path.join(repo_path, src_files[0]))
        for mode, label in [("safe", "safe"), ("unsafe", "unsafe")]:
            patch_path = os.path.join(patches_dir, f"{mode}.py")
            if not os.path.exists(patch_path):
                continue
            diffs.append(get_diff(original, read_file(patch_path), src_files[0]))
            labels.append(1 if label == "unsafe" else 0)

    scores = []
    for i in range(len(diffs)):
        train_X = diffs[:i] + diffs[i + 1:]
        train_y = labels[:i] + labels[i + 1:]
        if len(set(train_y)) < 2:
            scores.append(0.5)
            continue
        vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5),
                              max_features=5000, sublinear_tf=True)
        clf = LogisticRegression(max_iter=1000, C=1.0, random_state=42)
        clf.fit(vec.fit_transform(train_X), train_y)
        prob = clf.predict_proba(vec.transform([diffs[i]]))[0]
        scores.append(float(prob[list(clf.classes_).index(1)]))

    fpr, tpr, _ = roc_curve(labels, scores)
    auc = roc_auc_score(labels, scores)

    fig, ax = plt_mod.subplots(figsize=(5, 5))
    ax.plot(fpr, tpr, color="#4C72B0", lw=2, label=f"Learned monitor (AUC={auc:.3f})")
    ax.plot([0, 1], [0, 1], "k--", lw=0.8, alpha=0.5)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curve — Learned Monitor (LOO-CV)")
    ax.legend()

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "roc_curve.png")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt_mod.close(fig)
    print(f"Saved → {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", default="results/main_results.csv")
    parser.add_argument("--monitor-json", default="results/monitor_comparison.json")
    parser.add_argument("--tasks", default="benchmark/safecoderepair/tasks.json")
    parser.add_argument("--repos-base", default="benchmark/safecoderepair/repos")
    parser.add_argument("--out-dir", default="results/figures")
    args = parser.parse_args()

    if os.path.exists(args.monitor_json):
        plot_monitor_comparison(args.monitor_json, args.out_dir)
    else:
        print(f"[!] {args.monitor_json} not found — run scripts/compare_monitors.py first.")

    if os.path.exists(args.csv):
        plot_per_category(args.csv, args.out_dir)
    else:
        print(f"[!] {args.csv} not found — run scripts/run_eval.py first.")

    plot_roc_curve(args.tasks, args.repos_base, args.out_dir)


if __name__ == "__main__":
    main()
