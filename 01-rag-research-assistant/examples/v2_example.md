# RAG v2 Example

Version 2 keeps the original project intact and adds a stronger local retrieval
path.

It uses:

- overlapping chunks
- weighted unigram matching
- bigram matching
- phrase bonuses
- normalized retrieval scores
- evidence thresholds
- explicit abstention

Run it with:

    python src/rag_v2.py

Run the v2 evaluation with:

    python eval/evaluate_v2.py

The evaluator includes answerable questions and one question that is not
supported by the sample documents.
