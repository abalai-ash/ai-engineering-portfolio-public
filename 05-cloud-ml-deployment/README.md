# Cloud ML Deployment

Goal: Build a small local ML-style app with a cloud-ready project structure.

This project is a simple deployment-style demo. It classifies a fake message as low, medium, or high priority using hand-written scoring rules. The app reads basic settings from environment variables, returns a structured response, and includes a small evaluation script.

## Why this project matters

A useful AI or ML project should be easy to run, test, and move toward deployment. This version keeps the model simple so the focus is on project structure, configuration, evaluation, and clear output.

## Project structure

```text
05-cloud-ml-deployment/
├── README.md
├── config/
│   └── example.env
├── eval/
│   ├── eval_cases.csv
│   ├── eval_results.md
│   └── evaluate.py
├── examples/
│   └── example_outputs.md
└── src/
    └── app_v1.py
```

## Current features

- Classifies fake messages as low, medium, or high priority
- Uses simple scoring signals from the message text
- Reads app settings from environment variables
- Returns a structured response with prediction details
- Includes a small evaluation script
- Avoids private data and external services

## How to run locally

From this folder, run:

```bash
python src/app_v1.py
```

Example message:

```text
urgent model deployment error please check api
```

To run the evaluation:

```bash
python eval/evaluate.py
```

## Current result

```text
Evaluation complete: 4/4 passed
```

## What I am practicing

- Structuring a small ML-style app
- Keeping settings separate from code
- Returning clear prediction output
- Writing a simple evaluation script
- Keeping demo projects safe for a public repo

## Current limitations

- This version uses fake messages.
- The classifier is rule-based, not trained.
- It runs locally and does not deploy to a real cloud service yet.
- It does not use external APIs or private accounts.

## Status

Version 1 complete. The project currently supports local prediction, environment-based settings, structured output, and a basic evaluation script.

## Version 2: local prediction service

Version 2 keeps the original classifier but places it behind a small local HTTP service. This makes it possible to practice request validation, service health checks, batch handling, request IDs, structured responses, and clear error behavior.

### Version 2 routes

- `GET /health`
- `GET /ready`
- `POST /predict`
- `POST /predict/batch`

Run the service:

```bash
python src/service_v2.py
```

Run the service evaluation:

```bash
python eval/evaluate_v2.py
```

The Version 2 evaluation starts the service temporarily and checks:

- health and readiness
- a valid prediction
- rejection of an empty message
- partial success in a mixed batch
- handling of an unknown route

This remains a small local demo. It does not claim to provide a trained production model, autoscaling, distributed inference, authentication, or a real cloud deployment.


## Version 3: operational readiness evaluation

Version 3 adds a separate operational-readiness layer around the local prediction service.

It uses synthetic request observations to measure:

- request volume
- P95 latency
- service error rate
- timeout rate
- dependency failure rate
- liveness and readiness separately
- deployment readiness
- continue, hold, and rollback recommendations
- invalid threshold configuration
- deterministic repeated evaluation

Run the scenario demonstration:

    python3 src/operational_readiness.py

Run the evaluation:

    python3 eval/evaluate_operational_readiness.py

This remains a local deterministic demonstration. It does not claim production deployment, autoscaling, distributed inference, authentication, or use of private infrastructure.
