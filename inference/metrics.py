"""GPU metrics collection via Prometheus/DCGM."""
from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class GPUMetrics:
    utilization_mean: float
    utilization_max: float
    memory_hwm_mb: float
    duration_sec: float


class GPUMetricsCollector:
    def __init__(
        self,
        prometheus_url: str = "http://localhost:9090",
        instance: str = "localhost:9400",
        poll_interval_sec: float = 1.0,
    ) -> None:
        self.prometheus_url = prometheus_url
        self.instance = instance
        self.poll_interval_sec = poll_interval_sec
        self._samples: list[dict] = []
        self._running = False

    def _query(self, metric: str) -> float | None:
        try:
            import httpx
            resp = httpx.get(
                f"{self.prometheus_url}/api/v1/query",
                params={"query": f'{metric}{{instance="{self.instance}"}}'},
                timeout=5,
            )
            data = resp.json()
            result = data.get("data", {}).get("result", [])
            if result:
                return float(result[0]["value"][1])
        except Exception:
            pass
        return None

    def collect_snapshot(self) -> dict:
        util = self._query("DCGM_FI_DEV_GPU_UTIL") or 0.0
        mem_used = self._query("DCGM_FI_DEV_FB_USED") or 0.0
        mem_total = self._query("DCGM_FI_DEV_FB_FREE")
        temp = self._query("DCGM_FI_DEV_GPU_TEMP") or 0.0
        return {
            "gpu_utilization_percent": util,
            "gpu_memory_used_mb": mem_used,
            "gpu_memory_total_mb": mem_total or 0.0,
            "gpu_temperature_celsius": temp,
            "timestamp": time.time(),
        }

    @contextmanager
    def collect_during(self, fn: Callable):
        import threading

        self._samples = []
        self._running = True
        start = time.monotonic()

        def _poll():
            while self._running:
                self._samples.append(self.collect_snapshot())
                time.sleep(self.poll_interval_sec)

        t = threading.Thread(target=_poll, daemon=True)
        t.start()
        try:
            result = fn()
        finally:
            self._running = False
            t.join(timeout=5)

        duration = time.monotonic() - start
        metrics = self._summarize(duration)
        yield result, metrics

    def _summarize(self, duration_sec: float) -> GPUMetrics:
        if not self._samples:
            return GPUMetrics(
                utilization_mean=0.0,
                utilization_max=0.0,
                memory_hwm_mb=0.0,
                duration_sec=duration_sec,
            )
        utils = [s["gpu_utilization_percent"] for s in self._samples]
        mems = [s["gpu_memory_used_mb"] for s in self._samples]
        return GPUMetrics(
            utilization_mean=sum(utils) / len(utils),
            utilization_max=max(utils),
            memory_hwm_mb=max(mems),
            duration_sec=duration_sec,
        )
