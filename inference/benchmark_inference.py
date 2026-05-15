#!/usr/bin/env python3
"""Benchmark vLLM inference endpoints for throughput and latency."""
from __future__ import annotations

import asyncio
import csv
import os
import sys
import time
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

BENCHMARK_PROMPT = (
    "def quicksort(arr):\n    # Fix the bug in this quicksort implementation\n    if len(arr) <= 1:\n        return arr\n"
)


async def send_request(session, url: str, model: str, prompt: str) -> dict:
    import httpx

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 256,
        "stream": False,
    }
    start = time.monotonic()
    first_token_time = None
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(f"{url}/chat/completions", json=payload)
        first_token_time = time.monotonic() - start
        resp.raise_for_status()
        data = resp.json()
    end = time.monotonic()
    total_time = end - start
    usage = data.get("usage", {})
    output_tokens = usage.get("completion_tokens", 0)
    tokens_per_sec = output_tokens / total_time if total_time > 0 else 0
    return {
        "latency_sec": total_time,
        "ttft_sec": first_token_time,
        "tokens_per_sec": tokens_per_sec,
        "output_tokens": output_tokens,
    }


async def run_concurrent(url: str, model: str, concurrency: int, n_requests: int = 20) -> list[dict]:
    semaphore = asyncio.Semaphore(concurrency)
    results = []

    async def bounded_request():
        async with semaphore:
            return await send_request(None, url, model, BENCHMARK_PROMPT)

    tasks = [bounded_request() for _ in range(n_requests)]
    completed = await asyncio.gather(*tasks, return_exceptions=True)
    for r in completed:
        if isinstance(r, Exception):
            console.print(f"[red]Request error: {r}[/red]")
        else:
            results.append(r)
    return results


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    idx = int(len(sorted_vals) * p / 100)
    return sorted_vals[min(idx, len(sorted_vals) - 1)]


def main():
    app()


@app.command()
def benchmark(
    url: str = typer.Option("http://localhost:8000/v1", help="vLLM base URL"),
    model: str = typer.Option("qwen2.5-coder-32b", help="Model name"),
    concurrency: list[int] = typer.Option([1, 4, 8, 16], help="Concurrency levels"),
    n_requests: int = typer.Option(20, help="Requests per concurrency level"),
    output: str = typer.Option("results/inference_benchmarks.csv", help="Output CSV"),
):
    all_results = []
    table = Table(title=f"Inference Benchmark: {model}")
    table.add_column("Concurrency")
    table.add_column("Throughput (tok/s)")
    table.add_column("Latency p50 (s)")
    table.add_column("Latency p95 (s)")
    table.add_column("Latency p99 (s)")
    table.add_column("TTFT p50 (s)")
    table.add_column("N Successful")

    for c in concurrency:
        console.print(f"[cyan]Running concurrency={c}...[/cyan]")
        try:
            results = asyncio.run(run_concurrent(url, model, c, n_requests))
        except Exception as exc:
            console.print(f"[red]Failed at concurrency={c}: {exc}[/red]")
            continue

        latencies = [r["latency_sec"] for r in results]
        ttfts = [r["ttft_sec"] for r in results]
        throughputs = [r["tokens_per_sec"] for r in results]

        row = {
            "concurrency": c,
            "throughput_mean": sum(throughputs) / max(len(throughputs), 1),
            "latency_p50": percentile(latencies, 50),
            "latency_p95": percentile(latencies, 95),
            "latency_p99": percentile(latencies, 99),
            "ttft_p50": percentile(ttfts, 50),
            "n_successful": len(results),
        }
        all_results.append(row)

        table.add_row(
            str(c),
            f"{row['throughput_mean']:.1f}",
            f"{row['latency_p50']:.3f}",
            f"{row['latency_p95']:.3f}",
            f"{row['latency_p99']:.3f}",
            f"{row['ttft_p50']:.3f}",
            str(row["n_successful"]),
        )

    console.print(table)

    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    with open(output, "w", newline="") as f:
        if all_results:
            writer = csv.DictWriter(f, fieldnames=list(all_results[0].keys()))
            writer.writeheader()
            writer.writerows(all_results)
    console.print(f"[green]Results written to:[/green] {output}")


if __name__ == "__main__":
    main()
