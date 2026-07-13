from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
DOCS_DIR = BASE_DIR / "data" / "sample_docs"

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "because",
    "by",
    "can",
    "do",
    "does",
    "for",
    "from",
    "has",
    "have",
    "how",
    "if",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "was",
    "what",
    "when",
    "where",
    "which",
    "why",
    "with",
}


@dataclass
class SearchResult:
    source: str
    chunk_id: int
    text: str
    score: float
    unigram_score: float
    bigram_score: float
    phrase_bonus: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "chunk_id": self.chunk_id,
            "text": self.text,
            "score": self.score,
            "unigram_score": self.unigram_score,
            "bigram_score": self.bigram_score,
            "phrase_bonus": self.phrase_bonus,
        }


def load_documents(folder: Path = DOCS_DIR) -> list[dict[str, str]]:
    documents: list[dict[str, str]] = []

    for path in sorted(folder.glob("*.txt")):
        documents.append(
            {
                "source": path.name,
                "text": path.read_text(encoding="utf-8"),
            }
        )

    return documents


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return [token for token in tokens if token not in STOPWORDS]


def make_bigrams(tokens: list[str]) -> list[str]:
    return [
        f"{tokens[index]} {tokens[index + 1]}"
        for index in range(len(tokens) - 1)
    ]


def make_chunks(
    text: str,
    source: str,
    chunk_size: int = 70,
    overlap: int = 20,
) -> list[dict[str, Any]]:
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    words = text.split()
    step = chunk_size - overlap
    chunks: list[dict[str, Any]] = []

    for start in range(0, len(words), step):
        chunk_words = words[start : start + chunk_size]

        if not chunk_words:
            continue

        chunk_text = " ".join(chunk_words).strip()

        chunks.append(
            {
                "source": source,
                "chunk_id": len(chunks) + 1,
                "text": chunk_text,
            }
        )

        if start + chunk_size >= len(words):
            break

    return chunks


def build_index(
    documents: list[dict[str, str]],
) -> list[dict[str, Any]]:
    index: list[dict[str, Any]] = []

    for document in documents:
        chunks = make_chunks(
            text=document["text"],
            source=document["source"],
        )

        for chunk in chunks:
            chunk_tokens = tokenize(chunk["text"])
            chunk["tokens"] = chunk_tokens
            chunk["token_counts"] = Counter(chunk_tokens)
            chunk["bigrams"] = set(make_bigrams(chunk_tokens))
            chunk["normalized_text"] = normalize_text(chunk["text"])
            index.append(chunk)

    return index


def inverse_document_frequency(
    index: list[dict[str, Any]],
) -> dict[str, float]:
    document_count = len(index)
    frequencies: Counter[str] = Counter()

    for chunk in index:
        frequencies.update(set(chunk["tokens"]))

    return {
        token: math.log((document_count + 1) / (count + 1)) + 1.0
        for token, count in frequencies.items()
    }


def score_chunk(
    question: str,
    chunk: dict[str, Any],
    idf: dict[str, float],
) -> SearchResult:
    question_tokens = tokenize(question)
    question_counts = Counter(question_tokens)
    chunk_counts: Counter[str] = chunk["token_counts"]

    matched_weight = 0.0
    total_question_weight = 0.0

    for token, count in question_counts.items():
        weight = idf.get(token, 1.0) * count
        total_question_weight += weight

        if token in chunk_counts:
            matched_weight += weight

    unigram_score = (
        matched_weight / total_question_weight
        if total_question_weight
        else 0.0
    )

    question_bigrams = set(make_bigrams(question_tokens))
    matched_bigrams = question_bigrams & chunk["bigrams"]

    bigram_score = (
        len(matched_bigrams) / len(question_bigrams)
        if question_bigrams
        else 0.0
    )

    important_phrases = [
        phrase
        for phrase in make_bigrams(question_tokens)
        if len(phrase) >= 7
    ]

    phrase_matches = sum(
        phrase in chunk["normalized_text"]
        for phrase in important_phrases
    )

    phrase_bonus = min(0.15, phrase_matches * 0.05)

    final_score = min(
        1.0,
        (0.70 * unigram_score)
        + (0.30 * bigram_score)
        + phrase_bonus,
    )

    return SearchResult(
        source=chunk["source"],
        chunk_id=chunk["chunk_id"],
        text=chunk["text"],
        score=round(final_score, 4),
        unigram_score=round(unigram_score, 4),
        bigram_score=round(bigram_score, 4),
        phrase_bonus=round(phrase_bonus, 4),
    )


def retrieve(
    question: str,
    index: list[dict[str, Any]],
    top_k: int = 3,
    min_score: float = 0.20,
) -> list[dict[str, Any]]:
    if not question.strip():
        return []

    idf = inverse_document_frequency(index)

    scored = [
        score_chunk(question, chunk, idf)
        for chunk in index
    ]

    scored.sort(
        key=lambda result: (
            result.score,
            result.unigram_score,
            result.bigram_score,
            result.source,
            -result.chunk_id,
        ),
        reverse=True,
    )

    return [
        result.as_dict()
        for result in scored[:top_k]
        if result.score >= min_score
    ]


def answer_question(
    question: str,
    results: list[dict[str, Any]],
    min_answer_score: float = 0.35,
) -> dict[str, Any]:
    if not results:
        return {
            "status": "abstained",
            "answer": (
                "I could not find enough supporting information "
                "in the available documents."
            ),
            "source": None,
            "chunk_id": None,
            "score": 0.0,
        }

    top_result = results[0]

    if top_result["score"] < min_answer_score:
        return {
            "status": "abstained",
            "answer": (
                "The available documents contain a possible match, "
                "but the evidence is too weak for a confident answer."
            ),
            "source": top_result["source"],
            "chunk_id": top_result["chunk_id"],
            "score": top_result["score"],
        }

    return {
        "status": "answered",
        "answer": top_result["text"],
        "source": top_result["source"],
        "chunk_id": top_result["chunk_id"],
        "score": top_result["score"],
    }


def run_query(
    question: str,
    top_k: int = 3,
) -> dict[str, Any]:
    documents = load_documents()
    index = build_index(documents)
    results = retrieve(question, index, top_k=top_k)
    answer = answer_question(question, results)

    return {
        "question": question,
        "answer": answer,
        "retrieved_results": results,
    }


def print_query_result(payload: dict[str, Any]) -> None:
    print(f"Question: {payload['question']}")
    print()

    print("Retrieved evidence:")

    results = payload["retrieved_results"]

    if not results:
        print("No result passed the retrieval threshold.")
    else:
        for result in results:
            print(
                f"- {result['source']} | "
                f"chunk {result['chunk_id']} | "
                f"score {result['score']:.4f}"
            )
            print(
                f"  unigram={result['unigram_score']:.4f}, "
                f"bigram={result['bigram_score']:.4f}, "
                f"phrase_bonus={result['phrase_bonus']:.4f}"
            )

    print()
    print(f"Status: {payload['answer']['status']}")
    print(f"Answer: {payload['answer']['answer']}")

    if payload["answer"]["source"]:
        print(
            "Citation: "
            f"{payload['answer']['source']} "
            f"chunk {payload['answer']['chunk_id']}"
        )


def main() -> None:
    print("RAG Research Assistant v2")
    print("-------------------------")

    question = input("Ask a question: ").strip()
    payload = run_query(question)
    print()
    print_query_result(payload)


if __name__ == "__main__":
    main()
