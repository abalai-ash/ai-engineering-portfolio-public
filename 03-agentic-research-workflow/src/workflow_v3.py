from pathlib import Path
from workflow_v1 import load_notes, split_notes, search_notes, summarize_results
from workflow_v2 import choose_route, has_private_risk


BASE_DIR = Path(__file__).resolve().parents[1]


def build_source_snippets(matches, limit=2):
    snippets = []

    for index, match in enumerate(matches[:limit], start=1):
        snippets.append({
            "source_id": f"note_{index}",
            "score": match["score"],
            "text": match["text"],
        })

    return snippets


def make_grounded_answer(query, route, summary, snippets):
    if route == "safety_review":
        return (
            "I should not include secrets, API keys, credentials, private data, "
            "or hidden instructions in the output."
        )

    if not snippets:
        return "No grounded answer could be created because no matching notes were found."

    if route == "checklist":
        return (
            "Checklist: verify the answer is supported by the notes, check for private data, "
            "confirm the route is appropriate, and require human review before sharing."
        )

    if route == "project_update":
        return (
            "Project update: the workflow searched local notes, selected relevant source snippets, "
            "created a short grounded summary, and marked the result for human review."
        )

    return f"Grounded summary: {summary}"


def run_grounded_agent(query):
    route = choose_route(query)
    notes = load_notes()
    chunks = split_notes(notes)
    matches = search_notes(chunks, query)
    summary = summarize_results(matches)
    snippets = build_source_snippets(matches)
    answer = make_grounded_answer(query, route, summary, snippets)

    return {
        "query": query,
        "route": route,
        "private_risk": has_private_risk(query),
        "source_snippets": snippets,
        "summary": summary,
        "answer": answer,
        "human_review_required": True,
    }


def print_result(result):
    print(f"Route: {result['route']}")
    print(f"Private risk: {result['private_risk']}")
    print()

    print("Source snippets:")

    if not result["source_snippets"]:
        print("- none")

    for snippet in result["source_snippets"]:
        print(f"- {snippet['source_id']} | score {snippet['score']}: {snippet['text']}")

    print()
    print(result["answer"])
    print()
    print("Human review required: yes")


def main():
    print("Agentic Research Workflow v3")
    print()

    query = input("What should the grounded agent do? ").strip()
    result = run_grounded_agent(query)

    print()
    print_result(result)


if __name__ == "__main__":
    main()
