from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Any
import random


class InstrumentError(RuntimeError):
    pass


class InstrumentConnectionError(InstrumentError):
    pass


class InstrumentTimeoutError(InstrumentError):
    pass


class InvalidMeasurementError(InstrumentError):
    pass


@dataclass(frozen=True)
class MeasurementCase:
    case_id: str
    instrument: str
    target: float
    warning_tolerance: float
    failure_tolerance: float
    noise: float
    drift_per_sample: float
    sample_count: int
    expected_status: str
    outlier_index: int | None = None
    outlier_offset: float = 0.0
    connection_failure: bool = False
    timeout_index: int | None = None
    invalid_sample_index: int | None = None


class SimulatedInstrument:
    def __init__(
        self,
        case: MeasurementCase,
        *,
        seed: int,
    ) -> None:
        self.case = case
        self.rng = random.Random(seed)
        self.connected = False

    def connect(self) -> None:
        if self.case.connection_failure:
            raise InstrumentConnectionError(
                f"Could not connect to {self.case.instrument}"
            )

        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def read(self, sample_index: int) -> float:
        if not self.connected:
            raise InstrumentConnectionError(
                "Instrument is not connected"
            )

        if self.case.timeout_index == sample_index:
            raise InstrumentTimeoutError(
                f"Timed out while reading sample {sample_index}"
            )

        if self.case.invalid_sample_index == sample_index:
            raise InvalidMeasurementError(
                f"Invalid response at sample {sample_index}"
            )

        value = (
            self.case.target
            + self.case.drift_per_sample * sample_index
            + self.rng.gauss(0.0, self.case.noise)
        )

        if self.case.outlier_index == sample_index:
            value += self.case.outlier_offset

        return round(value, 6)


def build_case(raw: dict[str, Any]) -> MeasurementCase:
    return MeasurementCase(
        case_id=str(raw["case_id"]),
        instrument=str(raw["instrument"]),
        target=float(raw["target"]),
        warning_tolerance=float(raw["warning_tolerance"]),
        failure_tolerance=float(raw["failure_tolerance"]),
        noise=float(raw["noise"]),
        drift_per_sample=float(raw["drift_per_sample"]),
        sample_count=int(raw["sample_count"]),
        expected_status=str(raw["expected_status"]),
        outlier_index=(
            int(raw["outlier_index"])
            if raw.get("outlier_index") is not None
            else None
        ),
        outlier_offset=float(raw.get("outlier_offset", 0.0)),
        connection_failure=bool(
            raw.get("connection_failure", False)
        ),
        timeout_index=(
            int(raw["timeout_index"])
            if raw.get("timeout_index") is not None
            else None
        ),
        invalid_sample_index=(
            int(raw["invalid_sample_index"])
            if raw.get("invalid_sample_index") is not None
            else None
        ),
    )


def validate_case(case: MeasurementCase) -> None:
    if case.sample_count < 2:
        raise ValueError(
            "sample_count must be at least 2"
        )

    if case.warning_tolerance <= 0:
        raise ValueError(
            "warning_tolerance must be positive"
        )

    if case.failure_tolerance <= case.warning_tolerance:
        raise ValueError(
            "failure_tolerance must be greater than "
            "warning_tolerance"
        )

    if case.noise < 0:
        raise ValueError(
            "noise cannot be negative"
        )


def collect_measurements(
    case: MeasurementCase,
    *,
    seed: int,
) -> dict[str, Any]:
    validate_case(case)

    instrument = SimulatedInstrument(
        case,
        seed=seed,
    )

    readings: list[float] = []
    errors: list[dict[str, Any]] = []

    try:
        instrument.connect()
    except InstrumentConnectionError as exc:
        return {
            "connected": False,
            "readings": [],
            "errors": [
                {
                    "sample_index": None,
                    "error_type": "connection",
                    "message": str(exc),
                }
            ],
        }

    try:
        for index in range(case.sample_count):
            try:
                readings.append(
                    instrument.read(index)
                )
            except InstrumentTimeoutError as exc:
                errors.append(
                    {
                        "sample_index": index,
                        "error_type": "timeout",
                        "message": str(exc),
                    }
                )
            except InvalidMeasurementError as exc:
                errors.append(
                    {
                        "sample_index": index,
                        "error_type": "invalid-sample",
                        "message": str(exc),
                    }
                )
    finally:
        instrument.disconnect()

    return {
        "connected": True,
        "readings": readings,
        "errors": errors,
    }


def simulate_measurements(
    case: MeasurementCase,
    *,
    seed: int,
) -> list[float]:
    collection = collect_measurements(
        case,
        seed=seed,
    )

    if collection["errors"]:
        first_error = collection["errors"][0]
        raise InstrumentError(
            first_error["message"]
        )

    return collection["readings"]


def classify_reading(
    value: float,
    *,
    target: float,
    warning_tolerance: float,
    failure_tolerance: float,
) -> str:
    deviation = abs(value - target)

    if deviation > failure_tolerance:
        return "fail"

    if deviation > warning_tolerance:
        return "warning"

    return "pass"


def detect_drift(
    readings: list[float],
    *,
    warning_tolerance: float,
) -> dict[str, float | bool]:
    if len(readings) < 2:
        return {
            "total_drift": 0.0,
            "average_step": 0.0,
            "drift_detected": False,
        }

    total_drift = readings[-1] - readings[0]
    average_step = total_drift / (len(readings) - 1)

    return {
        "total_drift": round(total_drift, 6),
        "average_step": round(average_step, 6),
        "drift_detected": (
            abs(total_drift) > warning_tolerance
        ),
    }


def detect_outliers(
    readings: list[float],
    *,
    target: float,
    failure_tolerance: float,
) -> list[int]:
    return [
        index
        for index, value in enumerate(readings)
        if abs(value - target) > failure_tolerance
    ]


def build_summary(
    *,
    status: str,
    warning_count: int,
    failure_count: int,
    drift_detected: bool,
    error_count: int,
    connected: bool,
) -> str:
    if not connected:
        return (
            "The test failed because the instrument "
            "connection could not be established."
        )

    if error_count:
        return (
            "The test failed because one or more instrument "
            "responses were missing or invalid."
        )

    if failure_count:
        return (
            "The test failed because one or more readings "
            "exceeded the failure tolerance."
        )

    if status == "warning" and drift_detected:
        return (
            "The test needs review because the readings "
            "showed measurable drift."
        )

    if warning_count:
        return (
            "The test needs review because one or more readings "
            "exceeded the warning tolerance."
        )

    return (
        "The test passed because all readings stayed within "
        "the allowed limits."
    )


def evaluate_case(
    case: MeasurementCase,
    *,
    seed: int,
) -> dict[str, Any]:
    collection = collect_measurements(
        case,
        seed=seed,
    )

    readings = collection["readings"]
    errors = collection["errors"]
    connected = collection["connected"]

    reading_statuses = [
        classify_reading(
            value,
            target=case.target,
            warning_tolerance=case.warning_tolerance,
            failure_tolerance=case.failure_tolerance,
        )
        for value in readings
    ]

    drift = detect_drift(
        readings,
        warning_tolerance=case.warning_tolerance,
    )

    outlier_indices = detect_outliers(
        readings,
        target=case.target,
        failure_tolerance=case.failure_tolerance,
    )

    if not connected or errors:
        status = "fail"
    elif "fail" in reading_statuses:
        status = "fail"
    elif (
        "warning" in reading_statuses
        or drift["drift_detected"]
    ):
        status = "warning"
    else:
        status = "pass"

    warning_count = reading_statuses.count(
        "warning"
    )
    failure_count = reading_statuses.count(
        "fail"
    )

    return {
        "case_id": case.case_id,
        "instrument": case.instrument,
        "connected": connected,
        "requested_samples": case.sample_count,
        "collected_samples": len(readings),
        "missing_samples": (
            case.sample_count - len(readings)
        ),
        "errors": errors,
        "readings": readings,
        "mean": (
            round(mean(readings), 6)
            if readings
            else None
        ),
        "minimum": (
            min(readings)
            if readings
            else None
        ),
        "maximum": (
            max(readings)
            if readings
            else None
        ),
        "reading_statuses": reading_statuses,
        "warning_count": warning_count,
        "failure_count": failure_count,
        "outlier_indices": outlier_indices,
        "drift": drift,
        "status": status,
        "summary": build_summary(
            status=status,
            warning_count=warning_count,
            failure_count=failure_count,
            drift_detected=bool(
                drift["drift_detected"]
            ),
            error_count=len(errors),
            connected=connected,
        ),
        "expected_status": case.expected_status,
        "expected_check_passed": (
            status == case.expected_status
        ),
    }


def evaluate_batch(
    raw_cases: list[dict[str, Any]],
    *,
    seed: int,
) -> dict[str, Any]:
    results = [
        evaluate_case(
            build_case(raw),
            seed=seed + index,
        )
        for index, raw in enumerate(raw_cases)
    ]

    return {
        "case_count": len(results),
        "pass_count": sum(
            result["status"] == "pass"
            for result in results
        ),
        "warning_count": sum(
            result["status"] == "warning"
            for result in results
        ),
        "fail_count": sum(
            result["status"] == "fail"
            for result in results
        ),
        "instrument_error_count": sum(
            len(result["errors"])
            for result in results
        ),
        "all_expected_checks_passed": all(
            result["expected_check_passed"]
            for result in results
        ),
        "results": results,
        "scope": (
            "Synthetic measurement data used for a "
            "portfolio-scale engineering workflow."
        ),
    }
