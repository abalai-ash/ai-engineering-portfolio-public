# AI System Readiness and Risk Evaluation

This project is a small local framework for reviewing whether a proposed AI or machine-learning system is ready for launch.

It uses transparent rule-based checks rather than a trained model. The goal is to practice evaluation design, failure analysis, launch criteria, reliability thinking, and technical communication.

## What it checks

The evaluator reviews synthetic system proposals for:

- source grounding and evidence quality
- abstention and uncertainty behavior
- prompt-injection safeguards
- sensitive-data handling
- access controls
- human-review requirements
- monitoring and rollback plans
- ownership and incident responsibility
- latency targets
- operational readiness

## Recommendations

Each proposal receives one recommendation:

- `approve`: no important launch gaps were found by the current checks
- `needs_review`: meaningful gaps remain, but no immediate critical blocker was found
- `block`: one or more critical risks or several serious readiness gaps were found

The report includes a risk score, categorized findings, severity levels, and recommended actions.

## Synthetic cases

The included examples cover:

1. a grounded research assistant
2. a clinical-style summarization helper
3. an automated financial decision system
4. a multi-step support agent
5. an environmental-monitoring review assistant

The environmental case compares synthetic sensor readings, model estimates,
and historical records. It requires source evidence, uncertainty handling,
human review, monitoring, rollback planning, and clear ownership.

All examples use synthetic configuration data.

## Run the evaluator

From the repository root:

```bash
python3 09-ai-system-readiness-risk-evaluation/src/readiness_evaluator.py
```

This writes:

- `examples/readiness_report.json`
- `examples/example_report.md`

## Run the evaluation

```bash
python3 09-ai-system-readiness-risk-evaluation/eval/evaluate.py
```

Current result:

```text
Evaluation complete: 5/5 passed
```

## Project structure

```text
09-ai-system-readiness-risk-evaluation/
├── data/
│   └── system_proposals.json
├── eval/
│   ├── evaluate.py
│   └── eval_results.md
├── examples/
│   ├── example_report.md
│   └── readiness_report.json
├── src/
│   └── readiness_evaluator.py
└── README.md
```

## What this demonstrates

- explainable evaluation logic
- structured risk findings
- safety and reliability checks
- launch-readiness criteria
- evidence and human-review requirements
- synthetic healthcare and financial caution cases
- operational and product tradeoffs
- JSON and Markdown report generation
- automated behavior evaluation

## Scope

The current scoring rules are hand-written and intentionally small. The
project focuses on transparent findings, repeatable behavior, and review
criteria that can be inspected directly.

## Version 2: Controlled stress testing

Version 2 extends the original readiness review with controlled before-and-after tests.
It checks whether adding or removing specific safeguards changes the recommendation
and risk score in the expected direction.

It includes:

- controlled safeguard changes
- before-and-after risk comparisons
- malformed-input handling
- deterministic repeat checks
- recommendation counts
- severity summaries
- common risk-category summaries
- separate JSON and Markdown reports

Run Version 2 from the repository root:

```bash
python3 09-ai-system-readiness-risk-evaluation/src/stress_test_v2.py
python3 09-ai-system-readiness-risk-evaluation/eval/evaluate_v2.py
```

Version 2 uses the same synthetic proposals and adds controlled safeguard
changes, malformed-input checks, and repeatability tests.
