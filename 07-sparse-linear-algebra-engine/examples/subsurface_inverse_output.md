# Synthetic Subsurface Inverse Example

This example uses five synthetic measurements to estimate values in four
subsurface cells.

The sensitivity matrix is sparse, so only the nonzero connections between
measurements and cells are stored. The solver starts with all cell values set
to zero and updates them until the predicted measurements are close to the
synthetic measurements.

The evaluation checks that:

- the matrix uses sparse storage;
- the strongest cell is identified correctly;
- the measurement residual stays small;
- the objective decreases during the solve;
- repeated runs return the same result.

The example is deliberately small so the sparse matrix, solver updates, and
residual checks are easy to inspect.
