# v3 Grounded Agent Outputs

## Example run

```text
Agentic Research Workflow v3

Route: research_summary
Private risk: False

Source snippets:
- note_1 | score 5: Agentic workflows break a task into smaller steps. A tool-using assistant may search notes, summarize findings, create a checklist, and draft an update. Human review is important before sending or publishing the final result.
- note_2 | score 3: RAG systems work better when answers stay connected to source material. A useful workflow should retrieve notes, summarize only the relevant parts, and avoid making unsupported claims.

Grounded summary: Agentic workflows break a task into smaller steps, use tools like search and summarization, and still need human review.

Human review required: yes
```

## Evaluation result

```text
Evaluation complete: 4/4 passed
```

## What v3 demonstrates

- agent route selection
- source-grounded output
- safety routing
- fake local note retrieval
- human review requirement
- simple evaluation of expected behavior
