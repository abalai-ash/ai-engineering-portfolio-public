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

The portfolio check runs the primary local evaluation scripts across the projects using repository data and reports a pass/fail summary.

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

A sparse linear algebra project covering coordinate-format storage, matrix-vector multiplication, PageRank-style scoring, convergence checks, dense-versus-sparse comparison, and a synthetic subsurface inverse problem with regularized reconstruction and numerical evaluation.

### 08. LLM Knowledge and Failure Evaluation

A small evaluation framework for checking whether an AI answer is supported by a provided source. It evaluates grounding, unsupported information, missing evidence, citation consistency, confidence behavior, and common failure modes in systems that rely on retrieved or external knowledge.

### 09. AI System Readiness and Risk Evaluation

A transparent rule-based framework that reviews synthetic AI and machine-learning system proposals for grounding, evidence quality, sensitive-data handling, human review, monitoring, rollback planning, ownership, performance targets, and launch readiness. The evaluation set includes an environmental-monitoring readiness proposal with measurement-quality, uncertainty, escalation, and operational-control checks. It produces explainable `approve`, `needs_review`, or `block` recommendations with structured remediation steps.

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

This repository uses synthetic data, public datasets, and small demonstration examples selected for safe professional review.

The projects are local prototypes and evaluation workflows. Their READMEs describe the implemented scope, evaluation methods, current capabilities, and operating assumptions.

## 10. Enterprise AI Delivery Workflow

A synthetic cross-domain workflow that turns an unclear technical
request into discovery questions, architecture, risk evaluation,
staged deployment decisions, and a stakeholder-facing report.

The included cases cover:

- enterprise retrieval across structured and unstructured data
- environmental-monitoring investigation planning with measurement quality, uncertainty, and escalation checks
- scientific algorithm benchmarking, uncertainty, and reproducibility

The workflow uses synthetic requests and deterministic planning records to demonstrate technical discovery, solution planning, risk review, staged delivery decisions, operational safeguards, evaluation, testing, and stakeholder communication.

See
[`10-enterprise-ai-delivery-workflow/README.md`]
(10-enterprise-ai-delivery-workflow/README.md).

### 11. ML Monitoring and Incident Evaluation

This project compares a set of current model metrics with a saved baseline. It
checks changes in accuracy, precision, recall, latency, error rate, and the
positive-prediction rate. The alerts are then used to choose whether to
continue, review the change, or roll it back.

The example uses synthetic metrics and fixed rules so the same input produces the same result each time. It demonstrates repeatable local monitoring, alert generation, review, and rollback decisions.

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

<!-- portfolio-owner-notice -->
## Portfolio ownership

These original portfolio projects were created and maintained by the
repository owner. This repository is publicly viewable for professional review. No license or reuse permission is granted.

<!-- project-13-entry -->
## 13. AI Response Evaluation

A small deterministic review workflow for checking evidence support, direct
contradictions, invalid citations, appropriate abstention, and reviewer
disagreement.

Project directory: [`13-ai-response-evaluation`](13-ai-response-evaluation)

<!-- project-14-entry -->
## 14. Automated Measurement and Validation

A synthetic multichannel measurement-validation workflow for conductivity, moisture, and temperature data. It validates readings against warning and failure limits and reports drift, outliers, missing samples, connection failures, timeouts, and invalid responses.

The implementation includes 11 deterministic cases, detailed failure handling, generated evaluation summaries, and 16 passing automated tests.

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

A synthetic damped-motion simulation that compares numerical output with an analytical reference solution, measures numerical error, and documents how the same validation structure transfers to environmental and subsurface models.

The implementation includes four validation cases, RK4 integration, invalid-input handling, tolerance-based outcomes, generated reports, and nine passing automated tests.

Project directory:
[`16-simulation-model-validation`](16-simulation-model-validation)

## 17. Systems Traceability

A synthetic environmental-monitoring workflow that connects stakeholder needs, system and subsystem requirements, component allocations, interfaces, verification cases, and recorded evidence.

The implementation checks requirement wording, parent-child relationships, verification coverage, missing links, baseline differences, and the effects of proposed changes. It produces structured JSON, CSV, and Markdown review records.

Project directory: [`17-systems-traceability`](17-systems-traceability)

## 18. System Architecture Review

A synthetic environmental-monitoring architecture model for reviewing system functions, logical components, physical resources, interfaces, dependencies, and design alternatives.

The review identifies incomplete allocations, unsupported interfaces, dependency concerns, and sensitivity to weighting assumptions. It produces structured architecture findings and comparison reports.

Project directory: [`18-system-architecture-review`](18-system-architecture-review)

## 19. Verification Planning and Evidence

A synthetic environmental-monitoring workflow for connecting requirements to verification methods, planned cases, acceptance criteria, recorded evidence, anomalies, retesting, and closure status.

The implementation checks coverage, evidence completeness, unresolved findings, readiness conditions, and requirement-level outcomes. It generates traceable JSON, CSV, and Markdown summaries.

Project directory: [`19-verification-planning-evidence`](19-verification-planning-evidence)

## 20. Engineering Baseline Control

A synthetic environmental-monitoring configuration workflow covering baseline creation, proposed changes, review decisions, approvals, release comparison, and rollback readiness.

The implementation checks record completeness, documented differences, affected items, approval status, release conditions, and rollback artifacts. It produces structured comparison and review reports.

Project directory: [`20-engineering-baseline-control`](20-engineering-baseline-control)

<!-- project-21-entry -->
## 21. Embedded Sensor Fault Management

A deterministic C++17 host simulation of an embedded-style sensor controller covering measurement validation, watchdog timing, fault latching, safe-state entry, and controlled recovery.

The implementation includes structured requirements, design notes, an Agile backlog, requirement-to-test mappings, verification records, and 36 passing automated checks covering nominal behavior, boundary conditions, invalid and non-finite data, watchdog faults, safe-state blocking, and recovery behavior.

Project directory:
[`21-embedded-sensor-fault-management`](21-embedded-sensor-fault-management)
