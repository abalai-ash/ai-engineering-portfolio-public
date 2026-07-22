# Automated Measurement Validation

This project demonstrates a compact Python workflow for evaluating synthetic
measurement data against engineering limits.

It collects repeatable readings, identifies drift, handles interrupted
measurements, and returns clear pass, review, or fail outcomes.

## Demonstrated work

- deterministic measurement collection;
- threshold-based validation;
- drift detection;
- incomplete-run handling;
- structured evaluation output;
- automated tests for expected behavior.

## Included cases

- stable readings that remain within limits;
- gradual drift that requires review;
- an interrupted measurement that fails safely.

The examples are synthetic and do not represent real hardware or private
research data.

## Run

    python evaluate.py
    python -m unittest discover -s tests -v

This public version is intentionally limited. The broader instrument-control
design, full edge-case suite, and detailed development workflow remain private.
