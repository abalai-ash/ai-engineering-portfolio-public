# Scientific Image Search

Goal: Build a small image search demo using simple scientific image features.

This project uses fake image examples and hand-written feature values. The first version does not use real images. It treats each fake image like a small feature vector, then ranks the closest matches for a search query.

## Why this project matters

Scientific image work often starts by comparing shapes, brightness, edges, or other measured features. This project keeps that idea simple so the search logic is easy to inspect.

## Project structure

```text
04-scientific-image-search/
├── README.md
├── data/
│   └── image_features.csv
├── eval/
│   ├── eval_cases.csv
│   ├── eval_results.md
│   └── evaluate.py
├── examples/
└── src/
    └── search_v1.py
```

## Current features

- Loads fake scientific image feature data
- Converts a query into a simple target feature vector
- Compares images using distance between feature values
- Ranks closest image matches first
- Includes a small evaluation script

## How to run locally

From this folder, run:

```bash
python src/search_v1.py
```

Example query:

```text
bright ring disk
```

To run the evaluation:

```bash
python eval/evaluate.py
```

## Current result

```text
Evaluation complete: 3/3 passed
```

## What I am practicing

- Basic feature-based image search
- Similarity ranking
- Simple evaluation for top search results
- Keeping demo data separate from private research data

## Current limitations

- This version uses fake feature values.
- It does not load actual image files yet.
- The query mapping is rule-based.
- The distance metric is simple.

## Status

Version 1 complete. The project currently supports feature-based image search, distance ranking, and a small evaluation script.

## Version 2 update

Version 2 adds a more inspectable scientific image retrieval workflow.

The v2 search now includes:

- weighted feature similarity
- query interpretation
- target feature vector
- top-k ranked results
- similarity score
- match explanation for each result

This keeps the project simple while making the retrieval decision easier to inspect.

To run v2 locally:

```bash
python src/search_v2.py
```

To run the v2 evaluation:

```bash
python eval/evaluate_v2.py
```

Current v2 result:

```text
Evaluation complete: 3/3 passed
```

The v2 evaluation checks the expected top image, object type availability, query interpretation, and match explanation.

This project uses synthetic image features only. It does not include private research images or real scientific image files.

## Version 3: CNN image classification

Version 3 adds a small PyTorch convolutional neural network trained on deterministic synthetic images.

It demonstrates:

- synthetic image-dataset generation
- train, validation, and test separation
- convolutional feature learning
- checkpoint saving
- accuracy and loss reporting
- confusion-matrix evaluation
- deterministic local execution

Run the CNN evaluation:

    python3 eval/evaluate_cnn.py

The generated model checkpoint is excluded from Git. The public project includes the training and evaluation code, compact result reports, and synthetic-data description without including private research images.

This is a local portfolio demonstration rather than a production computer-vision system.

