from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SERVICE_SCRIPT = PROJECT_ROOT / "src" / "service_v2.py"
RESULTS_FILE = PROJECT_ROOT / "eval" / "eval_results_v2.md"

HOST = "127.0.0.1"
PORT = 8085
BASE_URL = f"http://{HOST}:{PORT}"


def request_json(
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
) -> tuple[int, dict[str, Any]]:
    body = None
    headers = {}

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(
        f"{BASE_URL}{path}",
        data=body,
        headers=headers,
        method=method,
    )

    try:
        with urlopen(request, timeout=3) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def wait_for_service() -> None:
    for _ in range(30):
        try:
            status, payload = request_json("GET", "/health")
            if status == 200 and payload.get("status") == "healthy":
                return
        except Exception:
            pass

        time.sleep(0.1)

    raise RuntimeError("service did not become healthy")


def main() -> None:
    process = subprocess.Popen(
        [
            sys.executable,
            str(SERVICE_SCRIPT),
            "--host",
            HOST,
            "--port",
            str(PORT),
        ],
        cwd=PROJECT_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    checks: list[tuple[str, bool]] = []

    try:
        wait_for_service()

        status, health = request_json("GET", "/health")
        checks.append(
            (
                "health endpoint responds",
                status == 200 and health.get("status") == "healthy",
            )
        )

        status, ready = request_json("GET", "/ready")
        checks.append(
            (
                "readiness endpoint responds",
                status == 200 and ready.get("status") == "ready",
            )
        )

        status, prediction = request_json(
            "POST",
            "/predict",
            {"message": "urgent model deployment error please check api"},
        )
        checks.append(
            (
                "single prediction returns high priority",
                status == 200
                and prediction.get("status") == "ok"
                and prediction.get("result", {})
                .get("prediction", {})
                .get("label")
                == "high",
            )
        )

        status, invalid = request_json(
            "POST",
            "/predict",
            {"message": ""},
        )
        checks.append(
            (
                "empty message returns a client error",
                status == 400
                and invalid.get("status") == "invalid_request",
            )
        )

        status, batch = request_json(
            "POST",
            "/predict/batch",
            {
                "messages": [
                    "general newsletter for later",
                    "urgent security failure blocked deployment",
                    "",
                ]
            },
        )
        checks.append(
            (
                "batch prediction records partial success",
                status == 200
                and batch.get("status") == "partial_success"
                and batch.get("total") == 3
                and batch.get("succeeded") == 2
                and batch.get("failed") == 1,
            )
        )

        status, missing_route = request_json("GET", "/missing")
        checks.append(
            (
                "unknown route returns 404",
                status == 404 and missing_route.get("status") == "not_found",
            )
        )

    finally:
        process.terminate()

        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=3)

    passed = sum(result for _, result in checks)

    lines = [
        "# Cloud ML Deployment v2 Evaluation",
        "",
        f"Passed: {passed}/{len(checks)}",
        "",
        "| Check | Result |",
        "|---|---|",
    ]

    for name, result in checks:
        lines.append(f"| {name} | {'PASS' if result else 'FAIL'} |")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "This evaluation starts the local service, checks its health and readiness routes, tests valid and invalid prediction requests, checks a mixed batch, and confirms that an unknown route returns a clear error.",
            "",
            "The service still uses the original hand-written demo classifier. The evaluation checks the service structure and reliability behavior, not real model accuracy or production scale.",
            "",
        ]
    )

    RESULTS_FILE.write_text("\n".join(lines), encoding="utf-8")

    for name, result in checks:
        print(f"{'PASS' if result else 'FAIL'}: {name}")

    print()
    print(f"Evaluation complete: {passed}/{len(checks)} passed")
    print(f"Wrote {RESULTS_FILE}")

    if passed != len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
