from pathlib import Path
import re


BASE_DIR = Path(__file__).resolve().parents[1]
DOCS_DIR = BASE_DIR / "data" / "sample_docs"

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "for",
    "from", "has", "have", "if", "in", "is", "it", "its", "of",
    "on", "or", "that", "the", "their", "this", "to", "was", "when",
    "where", "which", "with", "why"
}


def load_documents(folder):
    docs = []

    for path in sorted(folder.glob("*.txt")):
        docs.append({
            "source": path.name,
            "text": path.read_text(encoding="utf-8")
        })

    return docs


def make_chunks(text, source, chunk_size=65):
    words = text.split()
    chunks = []

    for start in range(0, len(words), chunk_size):
        chunk = " ".join(words[start:start + chunk_size]).strip()

        if chunk:
            chunks.append({
                "source": source,
                "chunk_id": len(chunks) + 1,
                "text": chunk
            })

    return chunks


def build_index(docs):
    index = []

    for doc in docs:
        index += make_chunks(doc["text"], doc["source"])

    return index


def tokenize(text):
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return {token for token in tokens if token not in STOPWORDS}


def score_chunk(question, chunk):
    question_terms = tokenize(question)
    chunk_terms = tokenize(chunk["text"])

    # Count shared keywords.
    return len(question_terms & chunk_terms)


def retrieve(question, index, top_k=3):
    matches = []

    for chunk in index:
        chunk_score = score_chunk(question, chunk)

        if chunk_score >= 2:
            match = chunk.copy()
            match["score"] = chunk_score
            matches.append(match)

    matches.sort(key=lambda item: item["score"], reverse=True)
    return matches[:top_k]


def make_short_answer(question, results):
    if not results:
        return "I could not find enough source text to answer this."

    best_text = results[0]["text"].lower()

    if "evidence is incomplete" in best_text:
        return (
            "Conclusions should stay cautious when evidence is incomplete "
            "because the explanation may not fully fit the available data yet."
        )

    if "api keys" in best_text or "secrets" in best_text:
        return (
            "API keys should not be committed to GitHub because they are secrets. "
            "They should be kept separate from the code, often with environment variables."
        )

    if "visual checks" in best_text or "plot can show" in best_text:
        return (
            "Visual checks are useful because plots can show problems like sudden jumps, "
            "flat sections, or missing measurements that one number may hide."
        )

    if "cloud deployment" in best_text:
        return (
            "Cloud deployment is useful because it lets an app run outside your own computer, "
            "which makes it easier to share, test, and maintain."
        )

    if "sensor data is often messy" in best_text:
        return (
            "It is useful to check sensor data before using it because readings can be missing, "
            "repeated, delayed, or affected by the environment."
        )

    return (
        "Based on the retrieved source text, the answer should come from the top matching chunk. "
        "This version keeps the answer simple so the source can still be checked."
    )


def print_results(question, results):
    print(f"Question: {question}")
    print()

    if not results:
        print("No matching source text was found.")
        print("Try using words that appear in the sample notes.")
        return

    print("Retrieved evidence:")
    print()

    for result in results:
        print(
            f"{result['source']} | chunk {result['chunk_id']} | "
            f"score {result['score']}"
        )
        print(result["text"])
        print()

    print("Short answer:")
    print(make_short_answer(question, results))


def main():
    docs = load_documents(DOCS_DIR)
    index = build_index(docs)

    print("RAG Research Assistant v1")
    print(f"Loaded documents: {len(docs)}")
    print(f"Searchable chunks: {len(index)}")
    print()

    question = input("Ask a question: ").strip()
    results = retrieve(question, index)

    print()
    print_results(question, results)


if __name__ == "__main__":
    main()
