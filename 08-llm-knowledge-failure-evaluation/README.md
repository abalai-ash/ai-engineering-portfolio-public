# LLM Knowledge and Failure Evaluation

This project is a small evaluation framework for checking whether an AI answer
is supported by a provided source.

The goal is not to train a language model. The goal is to practice evaluating
common failure modes in systems that use external knowledge.

## What it checks

- whether the answer is grounded in the source
- whether the answer adds unsupported information
- whether the response follows a format instruction
- whether the response admits when evidence is missing
- whether stronger and weaker answers are scored differently

## Why this matters

A response can sound confident and still be wrong. Systems that use retrieval
or external documents need checks that look at where the answer came from and
whether the source actually supports it.

## Project structure

```text
08-llm-knowledge-failure-evaluation/
├── data/
│   └── evaluation_cases.json
├── docs/
│   └── limitations.md
├── eval/
│   └── evaluate.py
├── examples/
│   └── example_results.md
├── src/
│   └── evaluator.py
└── README.md

## Response comparison

The project also compares two candidate answers and chooses the stronger one
based on groundedness, unsupported claims, instruction following, and the total
evaluation score.

Run the comparison:

    python src/compare_responses.py

Run the comparison evaluation:

    python eval/evaluate_comparisons.py

Current result:

    Evaluation complete: 3/3 passed
