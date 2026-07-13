# Response Comparison Example

The comparison layer checks whether the evaluator can choose a stronger answer
when given two candidate responses.

It currently tests:

- a supported answer against a hallucinated answer
- a concise answer against one with an extra unsupported claim
- a correct date against an incorrect date

Expected result:

    Evaluation complete: 3/3 passed

This is still a simple local evaluator. The goal is to make the scoring process
easy to inspect before adding real model-generated responses.
