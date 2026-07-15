# Quickstart

This guide shows how to run the main local examples and evaluations in this portfolio.

All projects use synthetic or public-safe examples. They do not require credentials, private data, or external API access.

## Run all main evaluations

From the repository root:

```bash
python3 run_portfolio_checks.py
```

This runs the primary evaluation script for each project and prints a pass/fail summary.

## Run individual projects

Run each command from the repository root.

### 01. RAG Research Assistant

```bash
python3 01-rag-research-assistant/src/rag_v2.py
python3 01-rag-research-assistant/eval/evaluate_v2.py
```

Demonstrates retrieval scoring, source attribution, grounded answers, and abstention.

### 02. Notification Relevance Ranker

```bash
python3 02-notification-relevance-ranker/src/ranker_v1.py
python3 02-notification-relevance-ranker/eval/evaluate.py
```

Demonstrates explainable ranking using interest, urgency, freshness, and channel preference.

### 03. Agentic Research Workflow

```bash
python3 03-agentic-research-workflow/src/workflow_v4.py
python3 03-agentic-research-workflow/eval/evaluate_v4.py
```

Demonstrates deterministic routing, grounded outputs, safety review, fallback behavior, and human-review controls.

### 04. Scientific Image Search

```bash
python3 04-scientific-image-search/src/search_v2.py
python3 04-scientific-image-search/eval/evaluate_v2.py
```

Demonstrates query-to-feature conversion, weighted similarity, ranking, and match explanations.

### 05. Cloud ML Deployment

```bash
python3 05-cloud-ml-deployment/src/service_v2.py
python3 05-cloud-ml-deployment/eval/evaluate_v2.py
```

Demonstrates request validation, structured responses, health checks, batch handling, and error cases.

### 06. RL Agent Evaluation Loop

```bash
python3 06-rl-agent-evaluation-loop/eval/evaluate_v2.py
```

Demonstrates action evaluation, reward-style scoring, retry handling, structured records, timing information, and checkpoint creation.

Generated run files are ignored by Git.

### 07. Sparse Linear Algebra Engine

```bash
python3 07-sparse-linear-algebra-engine/src/sparse_linear_algebra_v1.py
python3 07-sparse-linear-algebra-engine/src/dense_vs_sparse_compare_v1.py
python3 07-sparse-linear-algebra-engine/eval/evaluate.py
```

Demonstrates sparse storage, matrix-vector multiplication, iterative scoring, convergence checks, and dense comparison.

### 08. LLM Knowledge and Failure Evaluation

```bash
python3 08-llm-knowledge-failure-evaluation/src/compare_responses.py
python3 08-llm-knowledge-failure-evaluation/eval/evaluate.py
python3 08-llm-knowledge-failure-evaluation/eval/evaluate_comparisons.py
```

Demonstrates groundedness checks, unsupported-claim detection, instruction following, uncertainty behavior, and response comparison.

### 09. AI System Readiness and Risk Evaluation

```bash
python3 09-ai-system-readiness-risk-evaluation/src/readiness_evaluator.py
python3 09-ai-system-readiness-risk-evaluation/eval/evaluate.py
```

Demonstrates explainable launch-readiness evaluation, safety and privacy findings, evidence requirements, human-review checks, monitoring, rollback planning, and structured recommendations.

## Notes

These are small local portfolio demonstrations, not production services or trained frontier models. Each project README explains its current scope and limitations.
