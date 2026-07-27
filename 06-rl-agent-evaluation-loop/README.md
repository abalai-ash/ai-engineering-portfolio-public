# RL Agent Evaluation Loop

This project is a small reinforcement-learning-style agent evaluation demo.

The goal is not to train a large RL model. The goal is to show the structure of an agent behavior loop:

1. define scenarios
2. choose an action
3. assign a reward
4. evaluate whether the agent made the expected decision

This connects to reinforcement learning systems, agent evaluation, reward modeling basics, and safety-aware AI behavior.

## What the project does

The demo defines a few simple user-request scenarios. Each scenario includes:

- a user request
- a risk level
- whether clarification is needed
- the expected agent action

The agent can choose from these actions:

```text
answer_directly
ask_clarifying_question
safety_review
escalate_to_human
```

A reward function scores the chosen action. Correct actions receive positive reward, while risky or incorrect behavior is penalized.

## Current evaluation result

```text
Evaluation complete: 4/4 passed
Total reward: 40
```

## Why this matters

Many AI assistant systems need more than a generated answer. They need behavior checks:

- Should the assistant answer directly?
- Should it ask a clarifying question?
- Should it route the request to safety review?
- Should it escalate to a human?

This project shows a small version of that decision loop.

## What this project does not claim

This is not a production reinforcement learning system. It does not train a neural network, run distributed GPU jobs, or implement RLHF. It is a small, readable demo that shows reward-style scoring and agent behavior evaluation.

## Future improvements

- Expand the scenario suite
- Add a simple training loop
- Add more detailed decision logging
- Add cloud or container deployment notes

## Version 2: research-run reliability infrastructure

Version 2 adds a small reliability layer without replacing the original
decision-loop demo.

It includes:

- deterministic experiment settings and seeds
- run identifiers
- structured JSON episode records
- timing and summary metrics
- retries for temporary failures
- periodic checkpoints
- resumable runs
- automated reliability checks

Run the original evaluation:

    python eval/evaluate.py

Run the infrastructure evaluation:

    python eval/evaluate_v2.py

Current results:

    Original evaluation: 4/4 passed
    Infrastructure evaluation: 6/6 passed

This is still a small local research-engineering project. It does not claim to
provide large-scale distributed RL training, GPU orchestration, or production
RL infrastructure.

## Policy comparison benchmark

The project compares the current safety-aware policy with a simpler risk-only baseline across eight synthetic scenarios.

The benchmark measures:

- correct decision rate
- total and average reward
- unsafe actions
- missed clarification requests
- missed medium-risk escalations

Current comparison:

```text
risk_only_baseline: 4/8 passed, total reward 10
safety_aware_policy: 8/8 passed, total reward 80
```

Run the comparison:

```bash
python eval/evaluate_policy_comparison.py
```

The comparison is local and deterministic. It uses synthetic requests and a hand-written reward function rather than a learned reward model.
