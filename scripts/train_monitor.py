"""Train monitor classifiers on benchmark diffs.

Two training modes (can run together):
  --tfidf  Train TF-IDF + LogisticRegression (default, fast, no GPU needed)
  --embed  Train CodeBERT embedding monitor   (slow first run; GPU recommended)
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from safetrace.utils import get_diff, read_file


def collect_training_data(
    tasks_json: str, repos_base: str
) -> tuple[list[str], list[str]]:
    with open(tasks_json) as f:
        tasks = json.load(f)

    diffs: list[str] = []
    labels: list[str] = []

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
        src_file = src_files[0]
        original = read_file(os.path.join(repo_path, src_file))

        for mode, label in [("safe", "safe"), ("unsafe", "unsafe")]:
            patch_path = os.path.join(patches_dir, f"{mode}.py")
            if not os.path.exists(patch_path):
                continue
            patched = read_file(patch_path)
            diff = get_diff(original, patched, src_file)

            # Multi-file tasks: append test diff for unsafe patches
            test_patch = os.path.join(patches_dir, "unsafe_test.py")
            if mode == "unsafe" and os.path.exists(test_patch):
                tests_dir = os.path.join(repo_path, "tests")
                if os.path.isdir(tests_dir):
                    test_files = sorted(
                        f for f in os.listdir(tests_dir) if f.startswith("test_")
                    )
                    if test_files:
                        orig_test = read_file(os.path.join(tests_dir, test_files[0]))
                        test_patched = read_file(test_patch)
                        test_diff = get_diff(
                            orig_test, test_patched, f"tests/{test_files[0]}"
                        )
                        diff = diff + "\n" + test_diff

            diffs.append(diff)
            labels.append(label)

    return diffs, labels


def train_tfidf(diffs: list[str], labels: list[str], output_path: str) -> None:
    """Train TF-IDF char n-gram + LogisticRegression classifier."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import cross_val_score
    except ImportError:
        print("scikit-learn not installed. Run: pip install scikit-learn", file=sys.stderr)
        sys.exit(1)

    vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        max_features=10000,
        sublinear_tf=True,
    )
    clf = LogisticRegression(max_iter=1000, C=1.0, random_state=42)

    X = vectorizer.fit_transform(diffs)
    clf.fit(X, labels)

    # Cross-validated F1 to report
    if len(set(labels)) == 2 and len(diffs) >= 10:
        scores = cross_val_score(clf, X, labels, cv=min(5, len(diffs) // 4), scoring="f1_macro")
        print(f"TF-IDF CV F1 (macro): {scores.mean():.3f} ± {scores.std():.3f}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        pickle.dump({"vectorizer": vectorizer, "classifier": clf}, f)

    n_safe = labels.count("safe")
    n_unsafe = labels.count("unsafe")
    print(f"TF-IDF trained on {len(diffs)} diffs ({n_safe} safe, {n_unsafe} unsafe)")
    print(f"TF-IDF model saved → {output_path}")


def train_embeddings(
    diffs: list[str],
    labels: list[str],
    output_path: str,
    model_name: str = "microsoft/codebert-base",
) -> None:
    """Train CodeBERT embedding monitor — compute and save anchor embeddings.

    First call downloads the model (~500 MB). Subsequent calls use the cache.
    GPU recommended but not required.
    """
    import os
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

    try:
        from safetrace.embedding_monitor import EmbeddingMonitor
    except ImportError as exc:
        print(f"Could not import EmbeddingMonitor: {exc}", file=sys.stderr)
        sys.exit(1)

    monitor = EmbeddingMonitor(model_name=model_name, embeddings_path=output_path)
    print(f"Embedding monitor device: {monitor.device_info()}")
    print(f"Model: {model_name}")
    print("Computing embeddings (first run downloads ~500 MB)…")
    monitor.train(diffs, labels)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks", default="benchmark/safecoderepair/tasks.json")
    parser.add_argument("--repos-base", default="benchmark/safecoderepair/repos")
    parser.add_argument("--output", default="models/monitor.pkl")
    parser.add_argument("--embed-output", default="models/embeddings.npz")
    parser.add_argument(
        "--embed-model",
        default="microsoft/codebert-base",
        help="HuggingFace model ID for embedding monitor",
    )
    parser.add_argument("--tfidf", action="store_true", default=False, help="Train TF-IDF model")
    parser.add_argument("--embed", action="store_true", default=False, help="Train CodeBERT embeddings")
    args = parser.parse_args()

    # Default: train both
    if not args.tfidf and not args.embed:
        args.tfidf = True

    print("Collecting training data from benchmark diffs…")
    diffs, labels = collect_training_data(args.tasks, args.repos_base)
    if not diffs:
        print("No training samples found.", file=sys.stderr)
        sys.exit(1)
    print(f"Found {len(diffs)} diffs ({labels.count('safe')} safe, {labels.count('unsafe')} unsafe)")

    if args.tfidf:
        print("\n── TF-IDF + LogisticRegression ──────────────────")
        train_tfidf(diffs, labels, args.output)

    if args.embed:
        print("\n── CodeBERT Embedding Monitor ───────────────────")
        train_embeddings(diffs, labels, args.embed_output, model_name=args.embed_model)


if __name__ == "__main__":
    main()
