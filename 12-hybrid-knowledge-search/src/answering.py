"""Grounded response construction with cautious abstention."""

from __future__ import annotations

from typing import Any

from search import (
    confidence_summary,
    hybrid_search,
    record_text,
    tokenize,
)


MIN_TOP_SCORE = 0.28
MIN_QUERY_COVERAGE = 0.40


REQUIRED_INTENT_GROUPS = {
    "approval_identity": {
        "question_terms": {
            "approved",
            "approver",
            "authorized",
            "authorised",
        },
        "evidence_terms": {
            "approved",
            "approver",
            "authorized",
            "authorised",
            "owner",
            "person",
            "operator",
        },
    },
    "customer_identity": {
        "question_terms": {
            "customer",
            "customers",
            "name",
            "names",
        },
        "evidence_terms": {
            "customer",
            "customers",
            "name",
            "names",
            "account",
            "accounts",
        },
    },
    "credential_value": {
        "question_terms": {
            "password",
            "credential",
            "credentials",
            "secret",
            "secrets",
        },
        "evidence_terms": {
            "password",
            "credential",
            "credentials",
            "secret",
            "secrets",
        },
    },
    "weather_cause": {
        "question_terms": {
            "weather",
            "storm",
            "rain",
            "snow",
            "wind",
        },
        "evidence_terms": {
            "weather",
            "storm",
            "rain",
            "snow",
            "wind",
        },
    },
}


def combined_evidence_terms(
    results: list[dict[str, Any]],
) -> set[str]:
    """Return searchable terms from retrieved records."""

    terms: set[str] = set()

    for result in results:
        terms.update(
            tokenize(
                record_text(result["record"])
            )
        )

    return terms


def evidence_coverage(
    question: str,
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Measure how much of the question appears in the evidence."""

    query_terms = set(tokenize(question))

    if not query_terms:
        return {
            "query_terms": [],
            "matched_terms": [],
            "unmatched_terms": [],
            "matched_count": 0,
            "coverage": 0.0,
        }

    evidence_terms = combined_evidence_terms(
        results
    )

    matched_terms = query_terms.intersection(
        evidence_terms
    )

    unmatched_terms = query_terms.difference(
        evidence_terms
    )

    coverage = (
        len(matched_terms)
        / len(query_terms)
    )

    return {
        "query_terms": sorted(query_terms),
        "matched_terms": sorted(matched_terms),
        "unmatched_terms": sorted(unmatched_terms),
        "matched_count": len(matched_terms),
        "coverage": round(coverage, 6),
    }


def unsupported_intents(
    question: str,
    results: list[dict[str, Any]],
) -> list[str]:
    """Find requested attributes absent from retrieved evidence."""

    question_terms = set(tokenize(question))
    evidence_terms = combined_evidence_terms(
        results
    )

    unsupported = []

    for intent_name, intent in REQUIRED_INTENT_GROUPS.items():
        requested = bool(
            question_terms.intersection(
                intent["question_terms"]
            )
        )

        if not requested:
            continue

        supported = bool(
            evidence_terms.intersection(
                intent["evidence_terms"]
            )
        )

        if not supported:
            unsupported.append(intent_name)

    question_lower = question.lower().strip()

    if question_lower.startswith("who "):
        person_terms = {
            "person",
            "owner",
            "operator",
            "approver",
            "approved",
            "authorized",
            "authorised",
            "engineer",
            "manager",
        }

        if not evidence_terms.intersection(
            person_terms
        ):
            unsupported.append(
                "person_identity"
            )

    return sorted(set(unsupported))


def should_abstain(
    question: str,
    results: list[dict[str, Any]],
) -> bool:
    """Return True when retrieved evidence is too weak."""

    if not results:
        return True

    if unsupported_intents(
        question,
        results,
    ):
        return True

    confidence = confidence_summary(results)

    coverage = evidence_coverage(
        question,
        results,
    )

    if confidence["top_score"] < MIN_TOP_SCORE:
        return True

    query_term_count = len(
        coverage["query_terms"]
    )

    required_matches = (
        1
        if query_term_count <= 2
        else 2
    )

    if coverage["matched_count"] < required_matches:
        return True

    if coverage["coverage"] < MIN_QUERY_COVERAGE:
        return True

    return False


def answer_question(
    question: str,
    records: list[dict[str, Any]],
    limit: int = 3,
) -> dict[str, Any]:
    """Return evidence-backed excerpts or an abstention."""

    results = hybrid_search(
        question,
        records,
        limit=limit,
    )

    confidence = confidence_summary(results)

    coverage = evidence_coverage(
        question,
        results,
    )

    unsupported = unsupported_intents(
        question,
        results,
    )

    if should_abstain(
        question,
        results,
    ):
        return {
            "question": question,
            "status": "insufficient_evidence",
            "answer": (
                "The available records do not contain enough "
                "evidence to answer this question."
            ),
            "confidence": confidence,
            "evidence_coverage": coverage,
            "unsupported_intents": unsupported,
            "citations": [],
            "retrieval": results,
        }

    citations = []

    for result in results:
        record = result["record"]

        citations.append(
            {
                "record_id": record["id"],
                "title": record["title"],
                "record_type": record["type"],
                "evidence": record["text"],
                "score": result["final_score"],
                "path": result["evidence_path"],
            }
        )

    answer_parts = [
        citation["evidence"]
        for citation in citations
    ]

    return {
        "question": question,
        "status": "answered",
        "answer": " ".join(answer_parts),
        "confidence": confidence,
        "evidence_coverage": coverage,
        "unsupported_intents": unsupported,
        "citations": citations,
        "retrieval": results,
    }
