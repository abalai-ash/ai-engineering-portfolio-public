from __future__ import annotations

import re
from typing import Any


Record = dict[str, Any]

SUPPORTED_METHODS = {
    "analysis",
    "demonstration",
    "inspection",
    "test",
}

VAGUE_TERMS = {
    "adequate",
    "appropriate",
    "easy",
    "efficient",
    "fast",
    "reasonable",
    "sufficient",
    "timely",
    "user-friendly",
    "useful",
}


def extract_words(text: str) -> set[str]:
    """Return normalized words used by the wording checks."""
    return {
        word.lower()
        for word in re.findall(r"[A-Za-z-]+", text)
    }


def review_requirement(
    requirement: Record,
) -> list[str]:
    """Return review findings for one requirement."""
    findings: list[str] = []
    text = str(requirement.get("text", "")).strip()

    if not text:
        return ["Requirement text is empty."]

    if " shall " not in f" {text.lower()} ":
        findings.append(
            "Requirement does not use 'shall'."
        )

    vague_words = sorted(
        extract_words(text) & VAGUE_TERMS
    )

    if vague_words:
        findings.append(
            "Requirement contains vague wording: "
            + ", ".join(vague_words)
            + "."
        )

    if len(text) > 240:
        findings.append(
            "Requirement may contain too much information."
        )

    if not requirement.get("parent"):
        findings.append(
            "Requirement does not identify a parent."
        )

    if not requirement.get("component"):
        findings.append(
            "Requirement is not allocated to a component."
        )

    method = requirement.get("verification_method")

    if method not in SUPPORTED_METHODS:
        findings.append(
            "Verification method is missing or unsupported."
        )

    return findings


def review_requirements(
    requirements: list[Record],
) -> dict[str, list[str]]:
    """Return findings for requirements needing review."""
    results: dict[str, list[str]] = {}

    for requirement in requirements:
        findings = review_requirement(requirement)

        if findings:
            results[str(requirement["id"])] = findings

    return results
