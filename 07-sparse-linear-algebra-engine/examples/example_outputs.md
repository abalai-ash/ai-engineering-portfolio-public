# Example Outputs

## Demo run

```text
Sparse Linear Algebra Demo
--------------------------
Matrix shape: 4 x 4
Stored entries: 6
Density: 0.375
Converged: True
Steps: 17

Final ranking:
node_0: 0.3246
node_2: 0.3246
node_1: 0.1754
node_3: 0.1754
```

## Evaluation run

```text
Evaluation complete: 4/4 checks passed
```

## Interpretation

The matrix has 16 possible cells, but only 6 stored entries. This makes it sparse.

The ranking loop converges in 17 steps. Nodes 0 and 2 finish with the highest scores in this small graph, which matches the expected behavior for the demo.

## Dense vs sparse comparison

```text
Dense vs Sparse Comparison
--------------------------
Dense stored cells: 16
Sparse stored entries: 6
Storage reduction: 10 fewer stored values

Sparse result: [0.375, 0.125, 0.375, 0.125]
Dense result:  [0.375, 0.125, 0.375, 0.125]
Results match: True
```
