from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
NOTES_FILE = BASE_DIR / "data" / "research_notes.txt"


def load_notes():
    return NOTES_FILE.read_text(encoding="utf-8")


def split_notes(text):
    chunks = []

    for paragraph in text.split("\n\n"):
        paragraph = paragraph.strip()

        if paragraph:
            chunks.append(paragraph)

    return chunks


def search_notes(chunks, query):
    query_words = set(query.lower().split())
    results = []

    for chunk in chunks:
        chunk_words = set(chunk.lower().replace(".", "").replace(",", "").split())
        score = len(query_words & chunk_words)

        if score > 0:
            results.append({
                "score": score,
                "text": chunk
            })

    results.sort(key=lambda item: item["score"], reverse=True)
    return results


def summarize_results(results):
    if not results:
        return "No matching notes were found."

    top_text = results[0]["text"]

    if "Agentic workflows" in top_text:
        return "Agentic workflows break a task into smaller steps, use tools like search and summarization, and still need human review."

    if "RAG systems" in top_text:
        return "RAG systems are useful when answers need to stay connected to source material."

    if "Ranking systems" in top_text:
        return "Ranking systems help decide what should be shown first using signals like interest match, urgency, and freshness."

    if "Cloud-ready" in top_text:
        return "Cloud-ready AI projects separate code, settings, and secrets, and include clear run instructions."

    return top_text


def make_checklist(summary):
    checklist = [
        "Check that the answer is supported by the notes.",
        "Check that no private data or secrets are included.",
        "Check that the final update is clear enough for a human reviewer."
    ]

    if "tools" in summary or "steps" in summary:
        checklist.insert(0, "Check that each workflow step has a clear purpose.")

    return checklist


def draft_update(query, summary, checklist):
    lines = [
        "Draft update:",
        "",
        f"Task: {query}",
        "",
        f"Summary: {summary}",
        "",
        "Checklist before sharing:"
    ]

    for item in checklist:
        lines.append(f"- {item}")

    lines.extend([
        "",
        "Human review: required before sending or publishing."
    ])

    return "\n".join(lines)


def run_workflow(query):
    notes = load_notes()
    chunks = split_notes(notes)

    results = search_notes(chunks, query)
    summary = summarize_results(results)
    checklist = make_checklist(summary)
    update = draft_update(query, summary, checklist)

    return {
        "query": query,
        "matches": results,
        "summary": summary,
        "checklist": checklist,
        "draft_update": update
    }


def main():
    print("Agentic Research Workflow v1")
    print()

    query = input("What should the workflow research? ").strip()

    output = run_workflow(query)

    print()
    print("Top matching notes:")
    print()

    for result in output["matches"][:2]:
        print(f"score {result['score']}: {result['text']}")
        print()

    print(output["draft_update"])


if __name__ == "__main__":
    main()
