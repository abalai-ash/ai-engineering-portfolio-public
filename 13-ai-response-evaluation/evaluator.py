"""Small deterministic rubric for technical-response review."""

from __future__ import annotations

from statistics import median
from typing import Any

ABSTENTION_PHRASES = {
    "cannot determine",
    "does not identify",
    "insufficient evidence",
    "not enough evidence",
}

CONTRADICTION_PAIRS = (
    (
        {"healthy", "operating normally"},
        {"degraded", "unhealthy", "failed"},
    ),
)

def words(text: str) -> set[str]:
    """Return normalized words from a short string."""

    return {
        token.strip(".,:;!?()[]{}").lower()
        for token in text.split()
        if token.strip(".,:;!?()[]{}")
    }

def overlap_ratio(
    claim: str,
    evidence: str,
) -> float:
    """Return the fraction of claim words found in evidence."""

    claim_words = words(claim)

    if not claim_words:
        return 0.0

    evidence_words = words(evidence)

    return len(
        claim_words & evidence_words
    ) / len(claim_words)

def answer_abstains(answer: str) -> bool:
    """Check for a clear statement that evidence is insufficient."""

    lowered = answer.lower()

    return any(
        phrase in lowered
        for phrase in ABSTENTION_PHRASES
    )

def contradicts(
    claim: str,
    evidence: str,
) -> bool:
    """Detect direct healthy-versus-degraded conflicts."""

    claim_words = words(claim)
    evidence_words = words(evidence)

    for positive, negative in CONTRADICTION_PAIRS:
        if (
            claim_words & positive
            and evidence_words & negative
        ):
            return True

        if (
            claim_words & negative
            and evidence_words & positive
        ):
            return True

    return False

def review_claim(
    claim: dict[str, Any],
    evidence_by_id: dict[str, str],
) -> dict[str, Any]:
    """Review support, citation validity, and contradiction."""

    cited_ids = claim.get(
        "evidence_ids",
        [],
    )

    valid_ids = [
        evidence_id
        for evidence_id in cited_ids
        if evidence_id in evidence_by_id
    ]

    invalid_ids = [
        evidence_id
        for evidence_id in cited_ids
        if evidence_id not in evidence_by_id
    ]

    claim_text = claim.get(
        "text",
        "",
    )

    cited_evidence = " ".join(
        evidence_by_id[evidence_id]
        for evidence_id in valid_ids
    )

    all_evidence = " ".join(
        evidence_by_id.values()
    )

    contradicted = contradicts(
        claim_text,
        all_evidence,
    )

    content_supported = (
        not contradicted
        and overlap_ratio(
            claim_text,
            all_evidence,
        ) >= 0.50
    )

    citation_valid = (
        bool(valid_ids)
        and not invalid_ids
        and overlap_ratio(
            claim_text,
            cited_evidence,
        ) >= 0.50
    )

    return {
        "content_supported": content_supported,
        "citation_valid": citation_valid,
        "contradicted": contradicted,
        "invalid_evidence_ids": invalid_ids,
    }

def score_case(
    case: dict[str, Any],
) -> dict[str, Any]:
    """Score one synthetic evaluation case."""

    response = case["response"]
    answer = response["answer"]
    claims = response.get(
        "claims",
        [],
    )

    evidence_by_id = {
        item["id"]: item["text"]
        for item in case["evidence"]
    }

    reviews = [
        review_claim(
            claim,
            evidence_by_id,
        )
        for claim in claims
    ]

    abstained = answer_abstains(answer)

    contradicted = any(
        review["contradicted"]
        for review in reviews
    )

    content_supported = all(
        review["content_supported"]
        for review in reviews
    ) if reviews else abstained

    citations_valid = all(
        review["citation_valid"]
        for review in reviews
    ) if reviews else True

    if contradicted:
        status = "fail"
    elif content_supported and citations_valid:
        status = "pass"
    elif content_supported:
        status = "review"
    else:
        status = "fail"

    return {
        "case_id": case["case_id"],
        "status": status,
        "abstained": abstained,
        "claim_reviews": reviews,
    }

def reviewer_spread(
    scores: list[int],
) -> int:
    """Return the difference between highest and lowest scores."""

    if not scores:
        raise ValueError(
            "At least one reviewer score is required"
        )

    return max(scores) - min(scores)

def needs_adjudication(
    scores: list[int],
    threshold: int = 2,
) -> bool:
    """Flag reviewer scores whose spread exceeds a threshold."""

    return reviewer_spread(scores) > threshold

def adjudicated_score(
    scores: list[int],
) -> float:
    """Use the median as a simple final review score."""

    if not scores:
        raise ValueError(
            "At least one reviewer score is required"
        )

    return float(
        median(scores)
    )
