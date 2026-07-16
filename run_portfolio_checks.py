#!/usr/bin/env python3
"""
Run the main evaluation checks across the AI engineering portfolio.

This script is intentionally lightweight and public-safe. It does not call
external APIs, use private data, or require credentials. It runs the existing
local evaluation scripts and reports pass/fail status for quick review.
"""

from __future__ import annotations

import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent


@dataclass
class Check:
    name: str
    path: str
    reason: str


CHECKS = [
    Check(
        name="01 RAG Research Assistant v2",
        path="01-rag-research-assistant/eval/evaluate_v2.py",
        reason="retrieval scoring, source grounding, abstention, and evaluation",
    ),
    Check(
        name="02 Notification Relevance Ranker",
        path="02-notification-relevance-ranker/eval/evaluate.py",
        reason="explainable ranking and expected top-result behavior",
    ),
    Check(
        name="03 Agentic Research Workflow v4",
        path="03-agentic-research-workflow/eval/evaluate_v4.py",
        reason="deterministic routing, safety checks, and grounded workflow behavior",
    ),
    Check(
        name="04 Scientific Image Search v2",
        path="04-scientific-image-search/eval/evaluate_v2.py",
        reason="weighted similarity search, top-k ranking, and explanations",
    ),
    Check(
        name="05 Cloud ML Deployment v2",
        path="05-cloud-ml-deployment/eval/evaluate_v2.py",
        reason="health/readiness checks, validation, batch behavior, and error handling",
    ),
    Check(
        name="06 RL Agent Evaluation Loop v2",
        path="06-rl-agent-evaluation-loop/eval/evaluate_v2.py",
        reason="agent decisions, reward scoring, safety-aware behavior, and reliability checks",
    ),
    Check(
        name="07 Sparse Linear Algebra Engine",
        path="07-sparse-linear-algebra-engine/eval/evaluate.py",
        reason="sparse operations, iterative scoring, convergence, and numerical checks",
    ),
    Check(
        name="08 LLM Knowledge Failure Evaluation",
        path="08-llm-knowledge-failure-evaluation/eval/evaluate.py",
        reason="groundedness, unsupported claims, uncertainty behavior, and failure cases",
    ),
    Check(
        name="08 LLM Response Comparison",
        path="08-llm-knowledge-failure-evaluation/eval/evaluate_comparisons.py",
        reason="candidate response comparison and failure-report behavior",
    ),
    Check(
        name="09 AI System Readiness and Risk Evaluation",
        path="09-ai-system-readiness-risk-evaluation/eval/evaluate.py",
        reason="launch readiness, safety, evidence, human review, and operational risk checks",
    ),
    Check(
        name="09 AI System Readiness and Risk Evaluation v2",
        path="09-ai-system-readiness-risk-evaluation/eval/evaluate_v2.py",
        reason="controlled safeguard changes, malformed-input handling, deterministic checks, and before-after risk evaluation",
    ),
    Check(
        name="10 Enterprise AI Delivery Workflow",
        path="10-enterprise-ai-delivery-workflow/eval/evaluate.py",
        reason=(
            "technical discovery, cross-domain architecture planning, "
            "risk evaluation, deterministic checks, and stakeholder reporting"
        ),
    ),

]


def run_check(check: Check) -> tuple[bool, float, str]:
    script = ROOT / check.path
    if not script.exists():
        return False, 0.0, f"Missing file: {check.path}"

    start = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(script.parent),
        text=True,
        capture_output=True,
        timeout=60,
    )
    elapsed = time.perf_counter() - start
    output = (proc.stdout + proc.stderr).strip()
    return proc.returncode == 0, elapsed, output


def main() -> int:
    print("AI Engineering Portfolio Checks")
    print("=" * 34)
    print(f"Root: {ROOT}")
    print()

    results = []
    for check in CHECKS:
        ok, elapsed, output = run_check(check)
        results.append(ok)

        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {check.name}")
        print(f"  file: {check.path}")
        print(f"  why:  {check.reason}")
        print(f"  time: {elapsed:.2f}s")

        if output:
            compact_output = "\n".join(output.splitlines()[-8:])
            print("  output:")
            for line in compact_output.splitlines():
                print(f"    {line}")
        print()

    passed = sum(results)
    total = len(results)
    print("=" * 34)
    print(f"Summary: {passed}/{total} checks passed")

    if passed != total:
        print("One or more portfolio checks failed.")
        return 1

    print("All portfolio checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
