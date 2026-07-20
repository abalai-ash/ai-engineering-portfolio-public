# Hybrid Knowledge Search

This project explores a small local search system that combines text matching
with links between related records.

The example collection contains synthetic service descriptions, incident
summaries, and operational notes. Results include evidence references, and the
response layer can decline to answer when the available records do not support
a question.

## Included in this public example

- a compact synthetic record collection
- lexical retrieval
- relationship-aware reranking
- evidence references
- cautious insufficient-evidence behavior
- a runnable demonstration

## Run

From this directory:

    python3 run_demo.py

## Selected evaluation summary

The private evaluation set includes supported and unsupported questions.

- supported-answer rate: 1.00
- abstention accuracy: 1.00
- false answers: 0
- false abstentions: 0
- retrieval recall at three results: 0.9375

These results describe the included deterministic synthetic example. They do
not represent production performance or a general language-model benchmark.

## Scope

This is a local prototype built to make retrieval behavior easier to inspect.
The public version intentionally leaves out the full evaluation suite, detailed
development history, experimental variants, and internal tuning notes.
