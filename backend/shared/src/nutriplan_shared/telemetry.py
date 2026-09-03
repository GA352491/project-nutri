"""
NutriPlan Shared Latency & Performance Middleware.

Records real-time request durations across FastAPI services and computes
rolling Average, P95, and P99 latency scores without database overhead.
"""
from __future__ import annotations

import time
from collections import deque
from typing import Dict, List, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class LatencyTracker:
    """Thread-safe in-memory rolling latency ring buffer."""
    def __init__(self, max_samples: int = 1000):
        self._samples: deque[float] = deque(maxlen=max_samples)
        self._endpoint_samples: Dict[str, deque[float]] = {}

    def record(self, duration_ms: float, path: Optional[str] = None):
        self._samples.append(duration_ms)
        if path:
            norm_path = path.split("?")[0]
            if norm_path not in self._endpoint_samples:
                self._endpoint_samples[norm_path] = deque(maxlen=100)
            self._endpoint_samples[norm_path].append(duration_ms)

    def get_metrics(self) -> Dict[str, float]:
        if not self._samples:
            return {"count": 0, "avg_ms": 0.0, "p95_ms": 0.0, "p99_ms": 0.0, "status": "healthy"}
        
        sorted_samples = sorted(self._samples)
        n = len(sorted_samples)
        p95_idx = int(0.95 * n)
        p99_idx = int(0.99 * n)

        avg = sum(sorted_samples) / n
        p95 = sorted_samples[min(p95_idx, n - 1)]
        p99 = sorted_samples[min(p99_idx, n - 1)]

        status = "healthy"
        if p95 > 250:
            status = "degraded"
        elif p95 > 1000:
            status = "critical"

        return {
            "count": n,
            "avg_ms": round(avg, 2),
            "p95_ms": round(p95, 2),
            "p99_ms": round(p99, 2),
            "status": status
        }


global_latency_tracker = LatencyTracker()


class LatencyTelemetryMiddleware(BaseHTTPMiddleware):
    """
    Middleware that records precise latency for each request,
    attaches X-Response-Time-Ms to HTTP headers, and registers in tracker.
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000.0

        # Don't record health-checks to avoid skewing user metrics
        if "/health" not in request.url.path:
            global_latency_tracker.record(duration_ms, request.url.path)

        response.headers["X-Response-Time-Ms"] = f"{duration_ms:.2f}"
        return response
