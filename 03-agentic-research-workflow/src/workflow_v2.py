from pathlib import Path
from workflow_v1 import load_notes, split_notes, search_notes, summarize_results


BASE_DIR = Path(__file__).resolve().parents[1]
MEMORY_FILE = BASE_DIR / "data" / "workflow_memory.txt"


PRIVATE_WORDS = {
    "password",
    "secret",
    "api key",
    "credential",
    "private data",
    "ssn",
    "token",
    "ignore previous instructions",
    "system prompt",
    "hidden instructions",
    "bypass",
    "leak"
}


def load_memory():
    if not MEMORY_FILE.exists():
        return []

    text = MEMORY_FILE.read_text(encoding="utf-8").strip()

    if not text:
        return []

    return text.splitlines()


def save_memory(query, route):
    old_lines = load_memory()
    new_line = f"query={query} | route={route}"

    all_lines = old_lines + [new_line]
    MEMORY_FILE.write_text("\n".join(all_lines[-10:]), encoding="utf-8")


def has_private_risk(query):
    query_lower = query.lower()

    for word in PRIVATE_WORDS:
        if word in query_lower:
            return True

    return False


def choose_route(query):
    query_lower = query.lower()

    if has_private_risk(query):
        return "safety_review"

    if "summarize" in query_lower or "summary" in query_lower:
        return "research_summary"

    if "checklist" in query_lower:
        return "checklist"

    if "update" in query_lower or "status" in query_lower:
        return "project_update"

    if "review" in query_lower:
        return "checklist"

    return "research_summary"


def make_checklist(summary):
    return [
        "Check that the result is supported by the notes.",
        "Check that no private data or secrets are included.",
        "Check that the workflow route makes sense for the query.",
        "Check that a human can review the output before sharing."
    ]


def run_agent(query):
    route = choose_route(query)
    notes = load_notes()
    chunks = split_notes(notes)
    matches = search_notes(chunks, query)
    summary = summarize_results(matches)
    memory = load_memory()

    if route == "safety_review":
        output = (
            "Safety review: this query may involve private data or secrets. "
            "Do not include passwords, API keys, tokens, or private files in the output."
        )

    elif route == "checklist":
        checklist = make_checklist(summary)
        output = "Checklist:\n" + "\n".join(f"- {item}" for item in checklist)

    elif route == "project_update":
        output = (
            "Project update: the workflow searched the notes, created a short summary, "
            "and marked the result for human review before sharing."
        )

    else:
        output = f"Research summary: {summary}"

    save_memory(query, route)

    return {
        "query": query,
        "route": route,
        "summary": summary,
        "matches": matches,
        "memory_before_run": memory,
        "output": output,
        "human_review_required": True
    }


def main():
    print("Agentic Research Workflow v2")
    print()

    query = input("What should the agent do? ").strip()
    result = run_agent(query)

    print()
    print(f"Route: {result['route']}")
    print()
    print(result["output"])
    print()
    print("Human review required: yes")


if __name__ == "__main__":
    main()
