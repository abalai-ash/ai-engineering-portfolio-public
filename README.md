# AI Engineering Portfolio

[![Portfolio Checks](https://github.com/abalai-ash/ai-engineering-portfolio-public/actions/workflows/portfolio-checks.yml/badge.svg)](https://github.com/abalai-ash/ai-engineering-portfolio-public/actions/workflows/portfolio-checks.yml)


This repository contains small AI engineering projects I built to practice applied machine learning, scientific computing, ranking, retrieval, agent workflows, evaluation, monitoring, and deployment.

My background is in computational astrophysics, Python research workflows, data analysis, and scientific modeling. I use these projects to practice the full process: define a problem, build a working version, test it, and document what worked and what still needs improvement.

## Quick Review Guide

For a fast review, see [PORTFOLIO_SUMMARY.md](PORTFOLIO_SUMMARY.md).

| Role Direction | Most Relevant Projects |
|---|---|
| AI research engineering | 01, 03, 06, 08, 12 |
| LLM evaluation and agentic AI | 03, 06, 08, 12 |
| ML systems and performance foundations | 05, 06, 07, 11 |
| AI success, technical adoption, and applied AI | 01, 02, 03, 05, 10, 11 |

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
| 10. Enterprise AI Delivery Workflow | Technical delivery planning | Discovery questions, architecture planning, risk review, staged rollout decisions |
| 11. ML Monitoring and Incident Evaluation | Model monitoring and incident response | Baseline comparison, quality and latency alerts, rollback decisions, deterministic evaluation |
| 12. Hybrid Knowledge Search | Grounded retrieval and answer safety | Lexical and hybrid search, evidence paths, citations, and abstention |

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

## 10. Enterprise AI Delivery Workflow

A synthetic cross-domain workflow that turns an unclear technical
request into discovery questions, architecture, risk evaluation,
staged deployment decisions, and a stakeholder-facing report.

The included cases cover:

- enterprise retrieval across structured and unstructured data
- robot localization, calibration, sensor failure, and map mismatch planning
- scientific algorithm benchmarking, uncertainty, and reproducibility

The project demonstrates technical discovery, solution planning,
evaluation, operational safeguards, deterministic testing, and clear
technical communication.

It does not claim a real customer deployment, production SLAM system,
or quantum-hardware implementation.

See
[`10-enterprise-ai-delivery-workflow/README.md`]
(10-enterprise-ai-delivery-workflow/README.md).

### 11. ML Monitoring and Incident Evaluation

This project compares a set of current model metrics with a saved baseline. It
checks changes in accuracy, precision, recall, latency, error rate, and the
positive-prediction rate. The alerts are then used to choose whether to
continue, review the change, or roll it back.

The example uses synthetic metrics and fixed rules so the same input produces
the same result each time. It is a local exercise, not a live monitoring
service.

See
[`11-ml-monitoring-incident-evaluation/README.md`](11-ml-monitoring-incident-evaluation/README.md).

### 12. Hybrid Knowledge Search

This project searches a small collection of service notes, incident reports,
and runbooks. It combines direct word matching with links between related
records, then shows which records supported the answer.

I also added checks for questions that the records cannot answer. In those
cases, the program returns an insufficient-evidence response instead of
filling in a missing detail.

The private project contains the full evaluation set. The public repository
contains a smaller runnable example with the same main behavior.

See
[`12-hybrid-knowledge-search/README.md`](12-hybrid-knowledge-search/README.md).

## 17. Systems Traceability

A compact requirements-traceability demonstration for a synthetic monitoring system. It connects stakeholder needs, system requirements, subsystem requirements, verification cases, and recorded outcomes while identifying missing links and incomplete coverage.

Project directory: [`17-systems-traceability`](17-systems-traceability)

## 18. System Architecture Review

A synthetic architecture-review example that maps system functions to logical components and physical resources. It checks component allocations, interfaces, dependencies, and incomplete architecture records.

Project directory: [`18-system-architecture-review`](18-system-architecture-review)

## 19. Verification Planning and Evidence

A compact verification workflow connecting requirements to methods, planned cases, acceptance criteria, observations, anomalies, and closure status. It reports unresolved evidence and incomplete verification work.

Project directory: [`19-verification-planning-evidence`](19-verification-planning-evidence)

## 20. Engineering Baseline Control

A synthetic configuration-control example that compares an approved baseline with a proposed release. It checks changed items, affected records, required approvals, rollback readiness, and release status.

Project directory: [`20-engineering-baseline-control`](20-engineering-baseline-control)


<!-- portfolio-owner-notice -->
## Portfolio ownership

These original portfolio projects were created and maintained by the
repository owner. This repository is publicly viewable for professional review. No license or reuse permission is granted.

<!-- day-13-project-entry -->
## 13. AI Response Evaluation

A small deterministic review workflow for checking evidence support, direct
contradictions, invalid citations, appropriate abstention, and reviewer
disagreement.

Project directory: [`13-ai-response-evaluation`](13-ai-response-evaluation)

<!-- day-14-project-entry -->
## 14. Automated Measurement Validation

A compact synthetic measurement-validation example that classifies stable
readings, identifies gradual drift, and fails safely when a measurement is
interrupted.

The public version is intentionally limited and demonstrates deterministic
collection, engineering limits, structured outcomes, and automated testing
without exposing the complete instrument-control design or full validation
process.

Project directory:
[`14-automated-measurement-validation`](14-automated-measurement-validation)

<!-- project-15-entry -->
## 15. Engineering Test and Verification

A compact synthetic example that links engineering requirements to test
results and classifies outcomes as pass, review, or fail.

The public version demonstrates traceability, configuration checking, and
missing-test handling without exposing the full private verification workflow.

Project directory:
[`15-engineering-test-verification`](15-engineering-test-verification)

<!-- project-16-entry -->
## 16. Simulation Model Validation

A compact synthetic example that compares a numerical damped-motion simulation
with a reference solution and classifies the result as pass, review, or fail.

The public version demonstrates deterministic simulation, numerical error
measurement, invalid-input handling, and automated testing.

Project directory:
[`16-simulation-model-validation`](16-simulation-model-validation)
