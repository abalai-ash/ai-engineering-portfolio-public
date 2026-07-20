"""Transparent lexical and graph-aware retrieval."""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any


STOPWORDS = {
    "a",
    "after",
    "an",
    "and",
    "are",
    "at",
    "be",
    "can",
    "did",
    "during",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "should",
    "that",
    "the",
    "their",
    "this",
    "to",
    "was",
    "what",
    "when",
    "which",
    "who",
    "why",
    "with",
}


RELATION_WEIGHTS = {
    "depends_on": 0.22,
    "contributes_to": 0.22,
    "mitigated_by": 0.20,
    "responds_to": 0.20,
    "handled_by": 0.18,
    "affected_by": 0.18,
    "related_to": 0.16,
    "impacts": 0.14,
    "applies_to": 0.12,
    "supports": 0.10,
    "writes_to": 0.10,
    "observed_on": 0.08,
}


TYPE_PRIORS = {
    "incident": 0.04,
    "runbook": 0.04,
    "service": 0.02,
}


def tokenize(text: str) -> list[str]:
    """Return normalized tokens with common words removed."""

    normalized = re.sub(
        r"['’]s\b",
        "",
        text.lower(),
    )

    tokens = re.findall(
        r"[a-z0-9]+",
        normalized,
    )

    return [
        token
        for token in tokens
        if token not in STOPWORDS
        and len(token) > 1
    ]


def record_text(record: dict[str, Any]) -> str:
    """Join searchable record fields."""

    return " ".join(
        [
            record["title"],
            record["text"],
            " ".join(record.get("tags", [])),
            record["type"],
        ]
    )


def validate_records(
    records: list[dict[str, Any]],
) -> None:
    """Check required fields, duplicate IDs, and graph targets."""

    required = {
        "id",
        "type",
        "title",
        "text",
        "tags",
        "links",
    }

    record_ids = [
        record.get("id")
        for record in records
    ]

    if len(record_ids) != len(set(record_ids)):
        raise ValueError("Duplicate record IDs were found")

    known_ids = set(record_ids)

    for record in records:
        missing = required.difference(record)

        if missing:
            missing_text = ", ".join(sorted(missing))

            raise ValueError(
                f"Record {record.get('id', '<unknown>')} "
                f"is missing: {missing_text}"
            )

        for link in record["links"]:
            if "target" not in link or "relation" not in link:
                raise ValueError(
                    f"Record {record['id']} has an invalid link"
                )

            if link["target"] not in known_ids:
                raise ValueError(
                    f"Record {record['id']} links to unknown "
                    f"record {link['target']}"
                )


def inverse_document_frequency(
    records: list[dict[str, Any]],
) -> dict[str, float]:
    """Calculate smoothed inverse document frequencies."""

    document_count = len(records)
    document_frequency: Counter[str] = Counter()

    for record in records:
        terms = set(tokenize(record_text(record)))
        document_frequency.update(terms)

    return {
        term: math.log(
            (document_count + 1)
            / (frequency + 1)
        ) + 1.0
        for term, frequency in document_frequency.items()
    }


def lexical_score(
    query: str,
    record: dict[str, Any],
    idf: dict[str, float],
) -> float:
    """Calculate a normalized TF-IDF overlap score."""

    query_terms = tokenize(query)

    if not query_terms:
        return 0.0

    document_terms = tokenize(record_text(record))
    document_counts = Counter(document_terms)

    numerator = 0.0
    query_weight = 0.0

    for term in query_terms:
        weight = idf.get(term, 1.0)
        query_weight += weight

        if term in document_counts:
            term_frequency = (
                1.0
                + math.log(document_counts[term])
            )

            numerator += weight * term_frequency

    if query_weight == 0:
        return 0.0

    return numerator / query_weight


def lexical_search(
    query: str,
    records: list[dict[str, Any]],
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Return records ranked by lexical relevance."""

    idf = inverse_document_frequency(records)
    results = []

    for record in records:
        score = lexical_score(
            query,
            record,
            idf,
        )

        if score <= 0:
            continue

        results.append(
            {
                "record": record,
                "lexical_score": round(score, 6),
                "graph_bonus": 0.0,
                "type_prior": 0.0,
                "final_score": round(score, 6),
                "evidence_path": [record["id"]],
                "reasons": ["lexical match"],
            }
        )

    results.sort(
        key=lambda item: (
            item["final_score"],
            item["record"]["id"],
        ),
        reverse=True,
    )

    return results[:limit]


def build_reverse_links(
    records: list[dict[str, Any]],
) -> dict[str, list[dict[str, str]]]:
    """Create reverse edges so graph search works both ways."""

    reverse: dict[str, list[dict[str, str]]] = {
        record["id"]: []
        for record in records
    }

    for record in records:
        for link in record["links"]:
            reverse[link["target"]].append(
                {
                    "target": record["id"],
                    "relation": link["relation"],
                }
            )

    return reverse


def graph_candidates(
    seed_ids: list[str],
    records: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Collect one-hop graph candidates from lexical seeds."""

    record_map = {
        record["id"]: record
        for record in records
    }

    reverse_links = build_reverse_links(records)
    candidates: dict[str, dict[str, Any]] = {}

    for seed_id in seed_ids:
        seed = record_map[seed_id]

        outgoing = seed["links"]
        incoming = reverse_links[seed_id]

        for link in outgoing + incoming:
            target_id = link["target"]
            relation = link["relation"]

            relation_weight = RELATION_WEIGHTS.get(
                relation,
                0.06,
            )

            current = candidates.get(target_id)

            proposal = {
                "bonus": relation_weight,
                "path": [
                    seed_id,
                    relation,
                    target_id,
                ],
                "relation": relation,
            }

            if (
                current is None
                or proposal["bonus"] > current["bonus"]
            ):
                candidates[target_id] = proposal

    return candidates


def hybrid_search(
    query: str,
    records: list[dict[str, Any]],
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Combine lexical relevance with graph evidence."""

    validate_records(records)

    idf = inverse_document_frequency(records)

    lexical_results = lexical_search(
        query,
        records,
        limit=max(limit, 4),
    )

    seed_ids = [
        result["record"]["id"]
        for result in lexical_results[:3]
    ]

    graph_info = graph_candidates(
        seed_ids,
        records,
    )

    results = []

    for record in records:
        lexical = lexical_score(
            query,
            record,
            idf,
        )

        graph = graph_info.get(record["id"])
        graph_bonus = (
            graph["bonus"]
            if graph is not None
            else 0.0
        )

        type_prior = TYPE_PRIORS.get(
            record["type"],
            0.0,
        )

        if lexical <= 0 and graph_bonus <= 0:
            continue

        final_score = (
            lexical
            + graph_bonus
            + type_prior
        )

        reasons = []

        if lexical > 0:
            reasons.append("lexical match")

        if graph is not None:
            reasons.append(
                "graph relation: "
                f"{graph['relation']}"
            )

        if type_prior > 0:
            reasons.append(
                f"type prior: {record['type']}"
            )

        evidence_path = (
            graph["path"]
            if graph is not None
            else [record["id"]]
        )

        results.append(
            {
                "record": record,
                "lexical_score": round(lexical, 6),
                "graph_bonus": round(graph_bonus, 6),
                "type_prior": round(type_prior, 6),
                "final_score": round(final_score, 6),
                "evidence_path": evidence_path,
                "reasons": reasons,
            }
        )

    results.sort(
        key=lambda item: (
            item["final_score"],
            item["lexical_score"],
            item["record"]["id"],
        ),
        reverse=True,
    )

    return results[:limit]


def confidence_summary(
    results: list[dict[str, Any]],
) -> dict[str, float]:
    """Summarize top score and separation from second place."""

    if not results:
        return {
            "top_score": 0.0,
            "margin": 0.0,
        }

    top_score = results[0]["final_score"]

    second_score = (
        results[1]["final_score"]
        if len(results) > 1
        else 0.0
    )

    return {
        "top_score": round(top_score, 6),
        "margin": round(
            top_score - second_score,
            6,
        ),
    }
