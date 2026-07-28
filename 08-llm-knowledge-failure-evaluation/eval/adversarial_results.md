# Adversarial Evaluation Results

Passed: **6/6 cases** and **24/24 checks**

| Case | Result | Grounded | Unsupported claim | Format | Uncertainty |
|---|---|---|---|---|---|
| supported_date | PASS | True | False | True | False |
| fabricated_name | PASS | False | True | True | False |
| fabricated_date | PASS | False | True | True | False |
| appropriate_abstention | PASS | True | False | True | True |
| one_sentence_violation | PASS | False | True | False | False |
| meaning_reversal | PASS | False | True | True | False |

## Coverage

The cases test supported answers, fabricated names, fabricated dates, missing-evidence responses, format violations, and a simple meaning reversal.

## Scope

The cases are synthetic and the checks are local and rule-based. This evaluation does not use a trained language model or claim complete semantic understanding.
