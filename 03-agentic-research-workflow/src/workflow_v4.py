from __future__ import annotations

from typing import Any

from workflow_v3 import run_grounded_agent


ROUTE_KEYWORDS = {
    "research_summary": {
        "summarize",
        "summary",
        "research",
        "notes",
        "evidence",
        "source",
    },
    "checklist": {
        "checklist",
        "review",
        "steps",
        "verify",
        "inspect",
    },
    "project_update": {
        "status",
        "update",
        "progress",
        "report",
        "draft",
    },
}

SAFETY_TERMS = {
    "api key",
    "password",
    "secret",
    "token",
    "credential",
    "private data",
    "system prompt",
    "previous instructions",
}


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def deterministic_route(query: str) -> dict[str, Any]:
    """Choose a route using transparent keyword scores."""

    normalized = _normalize(query)

    if any(term in normalized for term in SAFETY_TERMS):
        return {
            "route": "safety_review",
            "confidence": 1.0,
            "reason": "The query contains a possible secret, private-data, or prompt-injection risk.",
            "method": "deterministic_safety_rule",
            "scores": {},
        }

    scores = {
        route: sum(1 for word in words if word in normalized)
        for route, words in ROUTE_KEYWORDS.items()
    }

    best_route = max(scores, key=scores.get)
    best_score = scores[best_route]

    if best_score == 0:
        return {
            "route": "research_summary",
            "confidence": 0.35,
            "reason": "No strong route signal was found, so the workflow used the safe default route.",
            "method": "deterministic_fallback",
            "scores": scores,
        }

    total_score = sum(scores.values())
    confidence = best_score / max(total_score, 1)

    return {
        "route": best_route,
        "confidence": round(confidence, 3),
        "reason": f"The query matched the strongest signals for {best_route}.",
        "method": "deterministic_keyword_router",
        "scores": scores,
    }


def run_agent_v4(query: str) -> dict[str, Any]:
    """Run the grounded v3 workflow and attach an explainable v4 route decision."""

    route_decision = deterministic_route(query)
    output = run_grounded_agent(query)

    output["router_v4"] = route_decision

    existing_route = output.get("route")
    if existing_route != route_decision["route"]:
        output["router_v4"]["v3_route"] = existing_route
        output["router_v4"]["route_disagreement"] = True
    else:
        output["router_v4"]["route_disagreement"] = False

    return output


def main() -> None:
    print("Agentic Research Workflow v4")
    query = input("What should the workflow do? ").strip()
    output = run_agent_v4(query)

    print(f"Route: {output.get('route')}")
    print(f"Router method: {output['router_v4']['method']}")
    print(f"Router confidence: {output['router_v4']['confidence']}")
    print(f"Router reason: {output['router_v4']['reason']}")
    print(f"Human review required: {output.get('human_review_required')}")
    print()
    print(output.get("answer", output.get("draft_update", "")))


if __name__ == "__main__":
    main()
