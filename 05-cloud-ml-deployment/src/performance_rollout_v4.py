from __future__ import annotations

import hashlib
import json
import math
import statistics
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "eval"
REPORT_JSON = RESULTS_DIR / "performance_rollout_results_v4.json"
REPORT_MD = RESULTS_DIR / "performance_rollout_results_v4.md"


@dataclass(frozen=True)
class ServiceObjectives:
    max_p95_latency_ms: float = 5.0
    max_error_rate: float = 0.02
    min_throughput_rps: float = 500.0


@dataclass(frozen=True)
class BenchmarkResult:
    request_count: int
    warmup_count: int
    mean_latency_ms: float
    median_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    throughput_rps: float
    error_rate: float


@dataclass(frozen=True)
class RolloutDecision:
    decision: str
    reasons: list[str]
    baseline: BenchmarkResult
    candidate: BenchmarkResult


def percentile(values: list[float], percentile_value: float) -> float:
    if not values:
        raise ValueError("values must not be empty")

    ordered = sorted(values)
    position = (len(ordered) - 1) * percentile_value
    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return ordered[lower]

    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def stable_bucket(request_id: str, bucket_count: int = 100) -> int:
    if not request_id:
        raise ValueError("request_id must not be empty")
    if bucket_count <= 0:
        raise ValueError("bucket_count must be positive")

    digest = hashlib.sha256(request_id.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % bucket_count


def select_model(
    request_id: str,
    candidate_percentage: int,
    feature_enabled: bool = True,
) -> str:
    if not 0 <= candidate_percentage <= 100:
        raise ValueError("candidate_percentage must be between 0 and 100")

    if not feature_enabled or candidate_percentage == 0:
        return "baseline"

    if candidate_percentage == 100:
        return "candidate"

    return (
        "candidate"
        if stable_bucket(request_id) < candidate_percentage
        else "baseline"
    )


def baseline_predict(message: str) -> dict[str, Any]:
    normalized = message.lower()

    if "urgent" in normalized or "error" in normalized:
        label = "high"
    elif "review" in normalized or "update" in normalized:
        label = "medium"
    else:
        label = "low"

    return {
        "label": label,
        "model": "baseline",
    }


def candidate_predict(message: str) -> dict[str, Any]:
    normalized = message.lower()
    tokens = normalized.split()

    high_signals = {"urgent", "failure", "failed", "error", "blocked"}
    medium_signals = {"review", "update", "warning", "check"}

    if any(token in high_signals for token in tokens):
        label = "high"
    elif any(token in medium_signals for token in tokens):
        label = "medium"
    else:
        label = "low"

    return {
        "label": label,
        "model": "candidate",
    }


def benchmark(
    predictor: Callable[[str], dict[str, Any]],
    messages: list[str],
    warmup_count: int = 20,
) -> BenchmarkResult:
    if not messages:
        raise ValueError("messages must not be empty")
    if warmup_count < 0:
        raise ValueError("warmup_count must not be negative")

    for index in range(warmup_count):
        predictor(messages[index % len(messages)])

    latencies_ms: list[float] = []
    errors = 0

    benchmark_start = time.perf_counter()

    for message in messages:
        request_start = time.perf_counter()

        try:
            response = predictor(message)
            if response.get("label") not in {"low", "medium", "high"}:
                errors += 1
        except Exception:
            errors += 1

        elapsed_ms = (time.perf_counter() - request_start) * 1000.0
        latencies_ms.append(elapsed_ms)

    total_seconds = time.perf_counter() - benchmark_start
    request_count = len(messages)

    return BenchmarkResult(
        request_count=request_count,
        warmup_count=warmup_count,
        mean_latency_ms=round(statistics.mean(latencies_ms), 6),
        median_latency_ms=round(statistics.median(latencies_ms), 6),
        p95_latency_ms=round(percentile(latencies_ms, 0.95), 6),
        p99_latency_ms=round(percentile(latencies_ms, 0.99), 6),
        throughput_rps=round(request_count / max(total_seconds, 1e-9), 3),
        error_rate=round(errors / request_count, 6),
    )


def evaluate_rollout(
    baseline: BenchmarkResult,
    candidate: BenchmarkResult,
    objectives: ServiceObjectives,
) -> RolloutDecision:
    reasons: list[str] = []

    if candidate.error_rate > objectives.max_error_rate:
        reasons.append("candidate error rate exceeds the service objective")

    if candidate.p95_latency_ms > objectives.max_p95_latency_ms:
        reasons.append("candidate p95 latency exceeds the service objective")

    if candidate.throughput_rps < objectives.min_throughput_rps:
        reasons.append("candidate throughput is below the service objective")

    if candidate.error_rate > baseline.error_rate:
        reasons.append("candidate error rate is worse than the baseline")

    latency_limit = max(
        objectives.max_p95_latency_ms,
        baseline.p95_latency_ms * 1.25,
    )
    if candidate.p95_latency_ms > latency_limit:
        reasons.append("candidate latency regressed by more than 25 percent")

    if any("error rate" in reason for reason in reasons):
        decision = "rollback"
    elif reasons:
        decision = "hold"
    else:
        decision = "continue_rollout"

    return RolloutDecision(
        decision=decision,
        reasons=reasons,
        baseline=baseline,
        candidate=candidate,
    )


def build_messages(count: int = 1000) -> list[str]:
    templates = [
        "general newsletter for later",
        "please review the deployment update",
        "urgent model deployment error please check api",
        "weekly project status",
        "warning dependency check failed",
    ]
    return [templates[index % len(templates)] for index in range(count)]


def demonstrate_routing(
    request_count: int = 100,
    candidate_percentage: int = 20,
) -> dict[str, int]:
    counts = {
        "baseline": 0,
        "candidate": 0,
    }

    for index in range(request_count):
        selected = select_model(
            request_id=f"request-{index:04d}",
            candidate_percentage=candidate_percentage,
        )
        counts[selected] += 1

    return counts


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    objectives = ServiceObjectives()
    messages = build_messages()

    baseline_result = benchmark(baseline_predict, messages)
    candidate_result = benchmark(candidate_predict, messages)
    decision = evaluate_rollout(
        baseline=baseline_result,
        candidate=candidate_result,
        objectives=objectives,
    )

    routing_first = demonstrate_routing()
    routing_second = demonstrate_routing()

    results = {
        "service_objectives": asdict(objectives),
        "baseline": asdict(baseline_result),
        "candidate": asdict(candidate_result),
        "routing": {
            "candidate_percentage": 20,
            "first_run": routing_first,
            "second_run": routing_second,
            "deterministic": routing_first == routing_second,
        },
        "rollout": {
            "decision": decision.decision,
            "reasons": decision.reasons,
        },
        "scope": (
            "This is a deterministic local benchmark using synthetic requests. "
            "It demonstrates latency measurement, throughput measurement, "
            "feature-flag routing, canary assignment, service objectives, and "
            "rollout decisions. It is not a production load test."
        ),
    }

    REPORT_JSON.write_text(
        json.dumps(results, indent=2) + "\n",
        encoding="utf-8",
    )

    reason_text = (
        "; ".join(decision.reasons)
        if decision.reasons
        else "All configured checks passed."
    )

    report_lines = [
        "# Performance and Rollout Evaluation",
        "",
        "## Result",
        "",
        f"- Rollout decision: `{decision.decision}`",
        f"- Reason: {reason_text}",
        "",
        "## Baseline",
        "",
        f"- Requests: {baseline_result.request_count}",
        f"- Mean latency: {baseline_result.mean_latency_ms:.6f} ms",
        f"- p95 latency: {baseline_result.p95_latency_ms:.6f} ms",
        f"- p99 latency: {baseline_result.p99_latency_ms:.6f} ms",
        f"- Throughput: {baseline_result.throughput_rps:.3f} requests/second",
        f"- Error rate: {baseline_result.error_rate:.6f}",
        "",
        "## Candidate",
        "",
        f"- Requests: {candidate_result.request_count}",
        f"- Mean latency: {candidate_result.mean_latency_ms:.6f} ms",
        f"- p95 latency: {candidate_result.p95_latency_ms:.6f} ms",
        f"- p99 latency: {candidate_result.p99_latency_ms:.6f} ms",
        f"- Throughput: {candidate_result.throughput_rps:.3f} requests/second",
        f"- Error rate: {candidate_result.error_rate:.6f}",
        "",
        "## Canary Routing",
        "",
        f"- Baseline requests: {routing_first['baseline']}",
        f"- Candidate requests: {routing_first['candidate']}",
        f"- Repeated routing is deterministic: {routing_first == routing_second}",
        "",
        "## Scope",
        "",
        (
            "This local exercise uses synthetic requests and a hand-written "
            "classifier. It is intended to demonstrate basic benchmarking, "
            "service objectives, canary routing, and rollback logic rather "
            "than production-scale performance."
        ),
        "",
    ]

    REPORT_MD.write_text(
        "\n".join(report_lines),
        encoding="utf-8",
    )

    print("Performance and rollout evaluation")
    print(f"Baseline p95 latency: {baseline_result.p95_latency_ms:.6f} ms")
    print(f"Candidate p95 latency: {candidate_result.p95_latency_ms:.6f} ms")
    print(f"Baseline throughput: {baseline_result.throughput_rps:.3f} rps")
    print(f"Candidate throughput: {candidate_result.throughput_rps:.3f} rps")
    print(f"Canary routing: {routing_first}")
    print(f"Routing deterministic: {routing_first == routing_second}")
    print(f"Rollout decision: {decision.decision}")
    print(f"Wrote {REPORT_JSON}")
    print(f"Wrote {REPORT_MD}")


if __name__ == "__main__":
    main()
