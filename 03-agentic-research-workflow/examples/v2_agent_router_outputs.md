# Agent Router v2 Example Outputs

This file keeps a few examples from the second version of the Agentic Research Workflow.

## What changed in v2

Version 2 adds a simple router. The workflow now chooses a route before creating the output.

Current routes:

```text
research_summary
checklist
project_update
safety_review
```

## Example 1: checklist route

Query:

```text
make a checklist for agentic workflow review
```

Output:

```text
Route: checklist

Checklist:
- Check that the result is supported by the notes.
- Check that no private data or secrets are included.
- Check that the workflow route makes sense for the query.
- Check that a human can review the output before sharing.

Human review required: yes
```

## Example 2: research summary route

Query:

```text
summarize agentic workflow tools and human review
```

Output:

```text
Route: research_summary

Research summary: Agentic workflows break a task into smaller steps, use tools like search and summarization, and still need human review.

Human review required: yes
```

## Example 3: safety review route

Query:

```text
check if this API key should be included
```

Output:

```text
Route: safety_review

Safety review: this query may involve private data or secrets. Do not include passwords, API keys, tokens, or private files in the output.

Human review required: yes
```

## Current v2 test result

```text
Evaluation complete: 4/4 passed
```

## Notes

This is still a small local demo. The goal is to show the structure of an agent workflow: route the task, use simple tools, check for private-data risk, keep a small memory file, and require human review.
