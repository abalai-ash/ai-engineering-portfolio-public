from __future__ import annotations

from typing import Any


def classify(
    requirement: dict[str, Any],
    test: dict[str, Any] | None,
) -> dict[str, str]:
    if test is None:
        return {
            "status": "review",
            "reason": "No test is linked to the requirement.",
        }

    for field in ("parameter", "unit", "configuration"):
        if test[field] != requirement[field]:
            return {
                "status": "fail",
                "reason": f"{field} does not match.",
            }

    value = test.get("value")

    if value is None:
        return {
            "status": "fail",
            "reason": "The test did not produce a valid result.",
        }

    value = float(value)
    minimum = float(requirement["minimum"])
    maximum = float(requirement["maximum"])

    if value < minimum or value > maximum:
        return {
            "status": "fail",
            "reason": "The result exceeded accepted limits.",
        }

    margin = float(test.get("review_margin", 0.0))

    if margin > 0 and (
        value <= minimum + margin
        or value >= maximum - margin
    ):
        return {
            "status": "review",
            "reason": "The result is close to a limit.",
        }

    return {
        "status": "pass",
        "reason": "The result satisfied the requirement.",
    }


def evaluate(
    requirements: list[dict[str, Any]],
    tests: list[dict[str, Any]],
) -> dict[str, Any]:
    tests_by_requirement = {
        test["requirement_id"]: test
        for test in tests
    }

    results = []

    for requirement in requirements:
        test = tests_by_requirement.get(
            requirement["id"]
        )

        outcome = classify(requirement, test)

        result = {
            "requirement_id": requirement["id"],
            "test_id": test["id"] if test else None,
            "status": outcome["status"],
            "reason": outcome["reason"],
        }

        if test:
            expected = test.get("expected_status")
            result["expected_status"] = expected
            result["expected_check_passed"] = (
                expected == outcome["status"]
            )

        results.append(result)

    return {
        "requirement_count": len(requirements),
        "test_count": len(tests),
        "pass_count": sum(
            item["status"] == "pass"
            for item in results
        ),
        "review_count": sum(
            item["status"] == "review"
            for item in results
        ),
        "fail_count": sum(
            item["status"] == "fail"
            for item in results
        ),
        "all_expected_checks_passed": all(
            item.get("expected_check_passed", True)
            for item in results
        ),
        "results": results,
        "scope": "Limited synthetic public portfolio example.",
    }
