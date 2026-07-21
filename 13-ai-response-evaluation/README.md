# AI Response Evaluation

This project reviews short technical responses using a small, deterministic
rubric. It focuses on decisions that should be easy to inspect and reproduce.

The public example demonstrates:

- scoring for correctness, evidence, uncertainty, clarity, and safety
- checking that cited records exist
- detecting a direct contradiction
- recognizing when a response should abstain
- flagging reviewer disagreement for follow-up

## Run the tests

From this directory:

    python3 -m unittest discover -s tests -v

## Run the example

    python3 evaluate.py

The command writes a local report to:

    output/evaluation_results.json

## Example outcomes

The included synthetic cases demonstrate three decisions:

- `pass` for a supported answer
- `review` for correct content with an invalid citation
- `fail` for a claim that contradicts the available record

## Scope

The records and responses are synthetic. This is a portfolio-scale evaluation
exercise, not a production safety system or a general natural-language
inference model.

Original portfolio project created and maintained by the author. This
repository is publicly viewable for professional review. No license or reuse
permission is granted.
