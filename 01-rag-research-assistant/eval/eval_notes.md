# RAG Evaluation Notes

This file keeps a short review of the first RAG evaluation.

## What the current eval checks

The current evaluation checks whether the system retrieves the expected source document for each question.

Current result:

```text
Evaluation complete: 5/5 passed
```

## What this means

The retrieval step is working for the small demo dataset. For the test questions, the system is able to find the source document that should support the answer.

## What this does not prove yet

This eval does not prove that the generated answer is perfect. It mainly checks source matching. A stronger eval would also check:

- whether the answer only uses retrieved information
- whether the answer avoids unsupported claims
- whether the system says when it does not have enough information
- whether similar documents confuse retrieval

## Possible next improvements

- Add one harder question where two documents share similar words
- Add an unknown-answer case where the system should not guess
- Track the retrieved score for each answer
- Add a short explanation for why the chosen source was used

## Notes

This project is intentionally small. The goal is to show the basic RAG loop: load documents, retrieve a relevant source, answer from that source, and evaluate whether retrieval is working.
