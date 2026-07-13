# Limitations

This project uses simple token overlap and rule-based checks.

That makes the evaluation easy to understand, but it also has limits:

- matching words does not always mean a claim is supported
- paraphrases may be scored incorrectly
- unsupported claims can sometimes reuse source words
- the uncertainty check depends on a small phrase list
- the evaluator does not yet compare real model providers
- the evaluator does not perform semantic entailment

The current version is meant to show the structure of an evaluation workflow,
not to claim that groundedness is fully solved.
