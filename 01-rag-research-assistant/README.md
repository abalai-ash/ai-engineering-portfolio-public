# RAG Research Assistant

Goal: Build a small assistant that answers questions from source documents instead of guessing from memory.

This project is my first portfolio project in the AI Engineering Portfolio. I am using it to practice the main pieces of a retrieval-augmented generation system: loading documents, splitting text into chunks, retrieving useful context, and checking whether the answer is supported by the right source text.

## What RAG means

RAG stands for retrieval-augmented generation. In simple terms, the system searches source documents first, finds relevant text, and then uses that text to answer a question.

## Why this project matters

Many AI tools are useful only when they can work with documents, notes, reports, or internal knowledge. A RAG system is one way to do that.

## Project structure

```text
01-rag-research-assistant/
├── README.md
├── data/
│   └── sample_docs/
│       ├── cloud_notes.txt
│       ├── public_science_notes.txt
│       └── sensor_notes.txt
├── eval/
│   ├── eval_questions.csv
│   ├── eval_results.md
│   └── evaluate.py
├── examples/
│   └── example_outputs.md
└── src/
    └── rag_v1.py
```

## Evaluation

This project has a small evaluation script:

```bash
python eval/evaluate.py
```

The script reads test questions from:

```text
eval/eval_questions.csv
```

It checks whether the top retrieved chunk came from the expected source file and writes the results to:

```text
eval/eval_results.md
```

Current result:

```text
5/5 test questions passed
```

## Current features

- Loads a small set of demo text files
- Splits the text into smaller chunks
- Scores chunks using simple keyword overlap
- Returns the most relevant chunks for a question
- Shows the source file, chunk number, and score
- Builds a short answer from the top retrieved source chunk
- Includes a small evaluation script for testing retrieval

## How to run locally

From this folder, run:

```bash
python src/rag_v1.py
```

To run the evaluation:

```bash
python eval/evaluate.py
```

## Example questions

```text
Why should conclusions stay cautious when evidence is incomplete?
```

```text
Why should API keys not be committed to GitHub?
```

```text
Why are visual checks useful for sensor data?
```

## What I am learning

- How document chunking affects retrieval
- How simple search works before adding embeddings
- How to keep answers tied to source text
- How to test whether retrieval found the right information
- How to document limits clearly

## Current limitations

- This version uses keyword matching, not embeddings.
- The short-answer step is simple and rule-based.
- It uses small demo documents, not private research data.
- It checks whether the top source is correct, but it does not fully score answer quality yet.

## Status

Version 1 complete. The project currently supports simple keyword retrieval, source checking, short source-based answers, and a basic evaluation script.

## Version 2: stronger local retrieval

Version 1 remains available in `src/rag_v1.py`.

Version 2 adds a separate retrieval path with:

- overlapping chunks so information near a chunk boundary is less likely to be lost
- weighted unigram and bigram matching
- exact-phrase bonuses
- normalized retrieval scores
- a minimum evidence threshold
- explicit abstention when the documents do not support an answer
- harder evaluation cases, including an unanswerable question

Version 2 still uses only local, public-safe sample documents and does not
require an API key.

Run version 2:

    python src/rag_v2.py

Run its evaluation:

    python eval/evaluate_v2.py
