# Agentic Research Workflow

Goal: Build a small workflow that uses simple tools to help with a research-style task.

This project is a basic version of an agentic workflow. It uses fake notes and local Python functions to search notes, summarize the most relevant part, make a checklist, and draft a short update. The final output is not treated as finished until a human reviews it.

## Why this project matters

A lot of AI tools are useful because they do more than answer one question. They break a task into steps, use tools, and make the result easier to check. This project keeps that idea simple and easy to inspect.

## Project structure

```text
03-agentic-research-workflow/
├── README.md
├── data/
│   └── research_notes.txt
├── eval/
│   ├── eval_cases.csv
│   ├── eval_results.md
│   └── evaluate.py
├── examples/
│   └── example_outputs.md
└── src/
    └── workflow_v1.py
```

## Current features

- Loads fake research notes
- Searches notes for relevant sections
- Creates a short summary
- Builds a checklist
- Drafts a structured update
- Marks the output as needing human review
- Includes a small evaluation script

## How to run locally

From this folder, run:

```bash
python src/workflow_v1.py
```

Example query:

```text
agentic workflow tools and human review
```

To run the evaluation:

```bash
python eval/evaluate.py
```

## Current result

```text
Evaluation complete: 5/5 passed
```

## What I am practicing

- Breaking a task into smaller steps
- Connecting simple tools together
- Keeping the output tied to the notes
- Adding a human review step before sharing the result


## Version 2 update

Version 2 adds a simple agent router. Before creating the final output, the workflow chooses a route based on the query.

Current routes:

```text
research_summary
checklist
project_update
safety_review
```

The v2 workflow also keeps a small local memory file of recent query routes and adds a basic safety review path for queries that mention secrets, API keys, tokens, credentials, private data, or prompt-injection style requests.

To run v2 locally:

```bash
python src/workflow_v2.py
```

To run the v2 evaluation:

```bash
python eval/evaluate_v2.py
```

Current v2 result:

```text
Evaluation complete: 5/5 passed
```

## Current limitations

- This version uses fake notes.
- The search is simple keyword matching.
- The summary step is rule-based.
- It does not call external tools or private accounts.

## Status

Version 1 complete. The project currently supports note search, a short summary, checklist creation, draft update generation, and a basic evaluation script.
