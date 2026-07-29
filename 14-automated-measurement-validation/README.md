# Automated Measurement and Validation System

This project is a small Python workflow for collecting simulated instrument
readings, checking them against engineering limits, and reporting problems
that need attention.

The workflow uses synthetic measurements to demonstrate repeatable
collection, validation, fault handling, and reporting.

## What it does

- simulates connecting to measurement instruments;
- collects repeatable synthetic readings across electrical and environmental channels;
- handles connection failures, timeouts, invalid responses, and missing samples;
- checks readings against warning and failure limits;
- detects drift and outliers;
- evaluates conductivity, moisture, and temperature cases alongside the original measurement set;
- writes JSON and Markdown reports with concise case summaries.

## Project structure

- `data/measurement_cases.json` contains synthetic test cases.
- `src/measurement_system.py` contains instrument and validation logic.
- `eval/evaluate.py` runs the full evaluation.
- `tests/test_measurement_system.py` contains unit tests.

## Run the tests

    python -m unittest discover -s tests -v

## Run the evaluation

    python eval/evaluate.py
