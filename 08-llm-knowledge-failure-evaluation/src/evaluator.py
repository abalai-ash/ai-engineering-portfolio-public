from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = PROJECT_ROOT / "data" / "evaluation_cases.json"


UNCERTAINTY_PHRASES = (
    "does not say",
    "not provided",
    "not enough information",
    "cannot determine",
    "unclear from the source",
)

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "did",
    "do",
    "does",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "this",
    "to",
    "was",
    "what",
    "when",
    "who",
}


@dataclass
class EvaluationResult:
    case_id: str
    grounded: bool
    has_unsupported_claim: bool
    follows_instruction: bool
    expresses_uncertainty: bool
    score: int
    max_score: int
    reasons: list[str]


def tokenize(text: str) -> set[str]:
    words = re.findall(r"[A-Za-z0-9]+", text.lower())
    return {word for word in words if word not in STOPWORDS and len(word) > 1}


def sentence_count(text: str) -> int:
    sentences = [
        item.strip()
        for item in re.split(r"[.!?]+", text)
        if item.strip()
    ]
    return len(sentences)


def extract_numbers(text: str) -> set[str]:
    return set(re.findall(r"\b\d+(?:\.\d+)?\b", text))


def extract_named_phrases(text: str) -> set[str]:
    phrases = set(
        re.findall(
            r"\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b",
            text,
        )
    )

    cleaned = set()
    for phrase in phrases:
        if phrase.startswith("The "):
            phrase = phrase[4:]
        cleaned.add(phrase.lower())

    return cleaned


def expresses_uncertainty(response: str) -> bool:
    lowered = response.lower()
    return any(phrase in lowered for phrase in UNCERTAINTY_PHRASES)


def follows_instruction(prompt: str, response: str) -> bool:
    lowered = prompt.lower()

    if "one sentence" in lowered:
        return sentence_count(response) == 1

    return True


def source_support_score(source: str, response: str) -> float:
    source_tokens = tokenize(source)
    response_tokens = tokenize(response)

    if not response_tokens:
        return 0.0

    overlap = source_tokens & response_tokens
    return len(overlap) / len(response_tokens)


def evaluate_case(case: dict[str, Any]) -> EvaluationResult:
    source = case["source"]
    response = case["response"]
    prompt = case["prompt"]

    uncertainty = expresses_uncertainty(response)
    support = source_support_score(source, response)
    instruction_ok = follows_instruction(prompt, response)

    source_tokens = tokenize(source)
    response_tokens = tokenize(response)
    unsupported_tokens = sorted(response_tokens - source_tokens)

    source_numbers = extract_numbers(source)
    response_numbers = extract_numbers(response)
    unsupported_numbers = sorted(response_numbers - source_numbers)

    source_names = extract_named_phrases(source)
    response_names = extract_named_phrases(response)
    unsupported_names = sorted(response_names - source_names)

    if uncertainty:
        grounded = True
        unsupported = False
    else:
        grounded = (
            support >= 0.75
            and not unsupported_numbers
            and not unsupported_names
        )
        unsupported = not grounded

    reasons: list[str] = []

    if grounded:
        reasons.append("Response is supported by the provided source.")
    else:
        reasons.append(
            "Response includes content that is not sufficiently supported by the source."
        )

    if unsupported_tokens and not uncertainty:
        reasons.append(
            "Possible unsupported terms: " + ", ".join(unsupported_tokens)
        )

    if unsupported_numbers and not uncertainty:
        reasons.append(
            "Numbers not found in the source: " + ", ".join(unsupported_numbers)
        )

    if unsupported_names and not uncertainty:
        reasons.append(
            "Names not found in the source: " + ", ".join(unsupported_names)
        )

    if instruction_ok:
        reasons.append("The response follows the requested format.")
    else:
        reasons.append("The response does not follow the requested format.")

    if uncertainty:
        reasons.append("The response clearly states that evidence is missing.")

    score = 0
    score += 1 if grounded else 0
    score += 1 if not unsupported else 0
    score += 1 if instruction_ok else 0

    expected_uncertainty = case["expected"]["expresses_uncertainty"]
    score += 1 if uncertainty == expected_uncertainty else 0

    return EvaluationResult(
        case_id=case["case_id"],
        grounded=grounded,
        has_unsupported_claim=unsupported,
        follows_instruction=instruction_ok,
        expresses_uncertainty=uncertainty,
        score=score,
        max_score=4,
        reasons=reasons,
    )


def load_cases(path: Path = DEFAULT_CASES) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_all(
    path: Path = DEFAULT_CASES,
) -> list[EvaluationResult]:
    return [evaluate_case(case) for case in load_cases(path)]


def write_results(
    results: list[EvaluationResult],
    path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [asdict(result) for result in results]
    path.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    results = evaluate_all()

    for result in results:
        print(f"Case: {result.case_id}")
        print(f"Grounded: {result.grounded}")
        print(f"Unsupported claim: {result.has_unsupported_claim}")
        print(f"Instruction followed: {result.follows_instruction}")
        print(f"Uncertainty expressed: {result.expresses_uncertainty}")
        print(f"Score: {result.score}/{result.max_score}")
        print()

    output = PROJECT_ROOT / "results" / "evaluation_results.json"
    write_results(results, output)
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
