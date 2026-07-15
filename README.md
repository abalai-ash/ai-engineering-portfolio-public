# AI Engineering Portfolio

[![Portfolio Checks](https://github.com/abalai-ash/ai-engineering-portfolio-public/actions/workflows/portfolio-checks.yml/badge.svg)](https://github.com/abalai-ash/ai-engineering-portfolio-public/actions/workflows/portfolio-checks.yml)


This repo is a collection of small AI engineering projects I am building to practice and show applied machine learning, scientific computing, ranking systems, RAG, agentic workflows, evaluation, and cloud deployment.

My background is in computational astrophysics, Python-based research workflows, data analysis, and scientific modeling. The goal of this portfolio is to show how I build practical AI systems step by step: define the problem, make a working prototype, test the result, and write down what worked and what still needs improvement.

## Quick Review Guide

For a fast review, see [PORTFOLIO_SUMMARY.md](PORTFOLIO_SUMMARY.md).

| Role Direction | Most Relevant Projects |
|---|---|
| AI research engineering | 01, 03, 06, 08 |
| LLM evaluation and agentic AI | 03, 06, 08 |
| ML systems and performance foundations | 05, 06, 07 |
| AI success, technical adoption, and applied AI | 01, 02, 03, 05 |

## Project Map

| Project | Main Focus | What it Demonstrates |
|---|---|---|
| 01. RAG Research Assistant | Retrieval and grounded answers | Chunking, retrieval scoring, source attribution, abstention, evaluation |
| 02. Notification Relevance Ranker | Ranking systems | Explainable scoring, user-interest matching, urgency/freshness signals |
| 03. Agentic Research Workflow | Agentic routing and research workflows | Route selection, source snippets, safety checks, deterministic fallback |
| 04. Scientific Image Search | Similarity search | Query-to-feature mapping, weighted similarity, top-k ranking |
| 05. Cloud ML Deployment | Service reliability | Health checks, request validation, batch prediction, error handling |
| 06. RL Agent Evaluation Loop | Agent behavior evaluation | Reward scoring, action selection, safety-aware behavior checks |
| 07. Sparse Linear Algebra Engine | Numerical computing and performance foundations | Sparse storage, matrix-vector multiplication, iterative scoring, convergence |
| 08. LLM Knowledge and Failure Evaluation | LLM reliability | Groundedness checks, unsupported-claim detection, response comparison |
| 09. AI System Readiness and Risk Evaluation | AI safety and launch readiness | Evidence, privacy, human review, monitoring, rollback, and risk recommendations |

## Portfolio Checks

Run the main local evaluation checks from the repository root:

```bash
python3 run_portfolio_checks.py
```

This runs the primary public-safe evaluation scripts across the projects and reports a pass/fail summary. It does not call external APIs, use credentials, or require private data.

## Projects

### 01. RAG Research Assistant

A source-grounded research assistant that answers questions using a collection of documents. The project includes document chunking, retrieval scoring, source attribution, abstention when evidence is insufficient, grounded answers, and retrieval evaluation.

### 02. Notification Relevance Ranker

An explainable ranking system that decides which notification or message is most relevant to a user. It scores user-interest match, urgency, freshness, and channel preference, then returns a per-signal score breakdown that can be inspected and evaluated.

### 03. Agentic Research Workflow

A source-grounded agentic workflow for research-style tasks such as searching notes, summarizing relevant material, creating checklists, and drafting structured updates. It includes route selection, source snippets, safety checks, deterministic fallback behavior, human-review requirements, and explainable routing scores.

### 04. Scientific Image Search

A scientific image-retrieval prototype using weighted feature similarity. It converts a text query into a target feature vector, ranks synthetic scientific-image records, returns top matches with similarity scores, and explains which features contributed to each result.

### 05. Cloud ML Deployment

A small ML-style service built with cloud deployment in mind. It includes environment-based configuration, structured prediction responses, health and readiness endpoints, request validation, batch processing, error handling, evaluation, logging notes, and deployment-oriented documentation.

### 06. RL Agent Evaluation Loop

A reinforcement-learning-style agent evaluation demo focused on action selection, reward scoring, safety-aware behavior checks, and evaluation of expected agent decisions. It demonstrates the structure of an agent behavior loop without claiming to be a production-trained RL model.

### 07. Sparse Linear Algebra Engine

A sparse matrix and iterative ranking project covering coordinate-format storage, matrix-vector multiplication, PageRank-style scoring, convergence checks, dense-versus-sparse comparison, and evaluation of numerical behavior.

### 08. LLM Knowledge and Failure Evaluation

A small evaluation framework for checking whether an AI answer is supported by a provided source. It evaluates grounding, unsupported information, missing evidence, citation consistency, confidence behavior, and common failure modes in systems that rely on retrieved or external knowledge.

### 09. AI System Readiness and Risk Evaluation

A transparent rule-based framework that reviews synthetic AI and machine-learning system proposals for grounding, evidence quality, sensitive-data handling, human review, monitoring, rollback planning, ownership, performance targets, and launch readiness. It produces explainable `approve`, `needs_review`, or `block` recommendations with structured remediation steps.

## What I am practicing

- Retrieval-augmented generation
- Source-grounded answers and abstention
- Embeddings, retrieval, and search concepts
- Ranking and recommendation logic
- Agentic workflows and tool routing
- Explainable deterministic decision systems
- Evaluation design and failure cases
- LLM grounding and reliability evaluation
- Safety-aware behavior checks
- Scientific machine learning
- Sparse linear algebra
- Cloud-ready application structure
- Clear technical documentation

## Safety and Data Notes

This repo uses synthetic data, public datasets, or small demo examples. Private data, credentials, API keys, unpublished research files, and private account information are intentionally kept out.

The projects are learning and portfolio demonstrations. Their READMEs document current limitations and distinguish local rule-based prototypes from production-trained models or externally deployed services.
