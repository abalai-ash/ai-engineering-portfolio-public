# Sparse Linear Algebra Engine

This project is a small sparse linear algebra and ranking-system demo. It shows how a sparse matrix can be stored compactly, used for matrix-vector multiplication, and applied in a PageRank-style iterative ranking loop.

The goal is not to build a production search engine. The goal is to show the core structure behind many ranking, recommendation, graph, and scientific-computing systems.

## What this project demonstrates

- sparse matrix representation using coordinate format
- matrix-vector multiplication
- iterative ranking with a damping factor
- convergence checking
- simple evaluation tests
- documentation of assumptions and limitations

## Why this matters

Sparse linear algebra appears in many applied ML and engineering systems:

- search ranking
- recommendation systems
- graph algorithms
- scientific computing
- retrieval systems
- large-scale feature matrices
- numerical simulation workflows

Many real systems are too large to store as dense matrices. Sparse representation keeps only the nonzero entries, which makes the computation more efficient and easier to reason about.

## Project structure

```text
07-sparse-linear-algebra-engine/
  src/
    sparse_linear_algebra_v1.py
  eval/
    evaluate.py
    eval_results.md
  examples/
    example_outputs.md
  docs/
    sparse_systems_notes.md
```

## How it works

The demo builds a small sparse link matrix. Each nonzero entry represents a connection from one node to another. The ranking loop starts with equal scores for all nodes, repeatedly applies sparse matrix-vector multiplication, adds a damping/random-jump term, and stops when the score change is small.

## Run the demo

```bash
python src/sparse_linear_algebra_v1.py
```


## Dense vs sparse comparison

This project also includes a small dense-vs-sparse comparison script. It converts the sparse matrix into a dense matrix, runs matrix-vector multiplication both ways, and checks that the results match.

```bash
python src/dense_vs_sparse_compare.py
```

The comparison shows why sparse storage matters: the dense version stores every cell, while the sparse version stores only the nonzero entries.

## Run evaluation

```bash
python eval/evaluate.py
```

## Current result

The evaluation checks that:

- the matrix is actually sparse
- the final rank vector sums to 1
- the iterative solver converges
- the expected top-ranked nodes are returned

Current evaluation result:

```text
Passed 4/4 checks.
```

## What this project does not claim

This is not a production search engine, recommendation engine, or optimized numerical library. It does not use SciPy, GPU acceleration, distributed computation, or a large dataset. It is a small educational engineering demo showing the basic structure of sparse matrix computation and iterative ranking.
