# Sparse Systems Notes

## Why sparse matrices matter

Many ML and data systems use matrices where most values are zero. Examples include user-item recommendation matrices, search/query-document graphs, feature matrices, and graph adjacency matrices.

A dense matrix stores every value. A sparse matrix stores only the nonzero values. This can reduce memory use and make computation more practical.

## Connection to ranking systems

This project uses a small PageRank-style loop. A score vector is repeatedly multiplied by a sparse link matrix. After each step, the vector is normalized and checked for convergence.

This is related to ranking systems because the final scores depend on graph structure, repeated updates, and convergence behavior.

## Connection to ML engineering

Sparse linear algebra shows up in ML engineering when systems need to work with large but mostly empty data structures. Common examples include:

- recommendation features
- document-term matrices
- graph-based ranking
- retrieval systems
- user-item interactions
- scientific computing workflows

## Engineering choices in this project

This project intentionally uses plain Python instead of a specialized library. That makes the logic easier to inspect:

- entries are stored as row, column, value tuples
- matrix-vector multiplication loops over stored entries
- convergence is measured with L1 distance
- evaluation checks expected numerical behavior

## Limitations

This is a small demo. It is not optimized for speed and does not use compressed sparse row format, SciPy, GPU acceleration, batching, or distributed processing.

A stronger production version would add:

- CSR or CSC sparse matrix storage
- larger benchmark graphs
- performance timing
- comparison against dense multiplication
- tests for edge cases
- integration with a real ranking or retrieval dataset
