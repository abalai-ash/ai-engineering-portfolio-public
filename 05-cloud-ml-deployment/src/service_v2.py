from __future__ import annotations

import argparse
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from app_v1 import make_response


@dataclass
class ServiceResult:
    request_id: str
    status: str
    timestamp: str
    result: dict[str, Any]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def error_payload(
    message: str,
    *,
    request_id: str | None = None,
    status: str = "invalid_request",
) -> dict[str, Any]:
    return {
        "request_id": request_id or str(uuid.uuid4()),
        "status": status,
        "timestamp": utc_now(),
        "error": message,
    }


def validate_message(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("message must be a string")

    message = value.strip()

    if not message:
        raise ValueError("message must not be empty")

    if len(message) > 1000:
        raise ValueError("message must be 1000 characters or fewer")

    return message


def predict_one(message: Any, request_id: str | None = None) -> dict[str, Any]:
    clean_message = validate_message(message)
    prediction = make_response(clean_message)

    result = ServiceResult(
        request_id=request_id or str(uuid.uuid4()),
        status="ok",
        timestamp=utc_now(),
        result=prediction,
    )
    return asdict(result)


def predict_batch(messages: Any) -> dict[str, Any]:
    if not isinstance(messages, list):
        raise ValueError("messages must be a list")

    if not messages:
        raise ValueError("messages must not be empty")

    if len(messages) > 50:
        raise ValueError("batch size must be 50 messages or fewer")

    batch_id = str(uuid.uuid4())
    results = []

    for index, message in enumerate(messages):
        item_request_id = f"{batch_id}:{index + 1}"
        try:
            results.append(
                {
                    "index": index,
                    "success": True,
                    "response": predict_one(message, item_request_id),
                }
            )
        except ValueError as exc:
            results.append(
                {
                    "index": index,
                    "success": False,
                    "response": error_payload(
                        str(exc),
                        request_id=item_request_id,
                    ),
                }
            )

    passed = sum(1 for item in results if item["success"])

    return {
        "batch_id": batch_id,
        "status": "ok" if passed == len(results) else "partial_success",
        "timestamp": utc_now(),
        "total": len(results),
        "succeeded": passed,
        "failed": len(results) - passed,
        "results": results,
    }


class PredictionHandler(BaseHTTPRequestHandler):
    server_version = "CloudMLDemo/2.0"

    def log_message(self, format: str, *args: Any) -> None:
        log_record = {
            "timestamp": utc_now(),
            "client": self.client_address[0],
            "message": format % args,
        }
        print(json.dumps(log_record, sort_keys=True))

    def send_json(self, status_code: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json_body(self) -> dict[str, Any]:
        content_length = self.headers.get("Content-Length")

        if content_length is None:
            raise ValueError("request body is required")

        try:
            body_size = int(content_length)
        except ValueError as exc:
            raise ValueError("invalid Content-Length header") from exc

        if body_size <= 0:
            raise ValueError("request body is required")

        if body_size > 100_000:
            raise ValueError("request body is too large")

        raw_body = self.rfile.read(body_size)

        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("request body must contain valid JSON") from exc

        if not isinstance(payload, dict):
            raise ValueError("request body must be a JSON object")

        return payload

    def do_GET(self) -> None:
        path = urlparse(self.path).path

        if path == "/health":
            self.send_json(
                200,
                {
                    "status": "healthy",
                    "service": "cloud-ml-deployment-demo",
                    "version": "2",
                    "timestamp": utc_now(),
                },
            )
            return

        if path == "/ready":
            self.send_json(
                200,
                {
                    "status": "ready",
                    "model": "hand-written-priority-rules",
                    "timestamp": utc_now(),
                },
            )
            return

        self.send_json(404, error_payload("route not found", status="not_found"))

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        request_id = self.headers.get("X-Request-ID") or str(uuid.uuid4())

        try:
            payload = self.read_json_body()

            if path == "/predict":
                result = predict_one(payload.get("message"), request_id)
                self.send_json(200, result)
                return

            if path == "/predict/batch":
                result = predict_batch(payload.get("messages"))
                self.send_json(200, result)
                return

            self.send_json(
                404,
                error_payload(
                    "route not found",
                    request_id=request_id,
                    status="not_found",
                ),
            )
        except ValueError as exc:
            self.send_json(
                400,
                error_payload(str(exc), request_id=request_id),
            )
        except Exception:
            self.send_json(
                500,
                error_payload(
                    "unexpected service error",
                    request_id=request_id,
                    status="service_error",
                ),
            )


def run_server(host: str, port: int) -> None:
    server = ThreadingHTTPServer((host, port), PredictionHandler)

    print(
        json.dumps(
            {
                "event": "service_started",
                "host": host,
                "port": port,
                "timestamp": utc_now(),
            },
            sort_keys=True,
        )
    )

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        server.server_close()
        print(
            json.dumps(
                {
                    "event": "service_stopped",
                    "timestamp": utc_now(),
                },
                sort_keys=True,
            )
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the local Cloud ML Deployment v2 service."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8085)
    args = parser.parse_args()

    run_server(args.host, args.port)


if __name__ == "__main__":
    main()
