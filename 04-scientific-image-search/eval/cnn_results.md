# CNN Evaluation Results

- Device: `mps`
- Best validation accuracy: `1.000`
- Held-out test accuracy: `1.000`
- Test loss: `1.0874`
- Checkpoint: `models/cnn_demo_best.pt`

## Confusion matrix

| Actual \ Predicted | compact | rings | spirals |
|---|---:|---:|---:|
| compact | 15 | 0 | 0 |
| rings | 0 | 0 | 0 |
| spirals | 0 | 0 | 0 |

## Scope

This is a small local CNN demonstration trained only on deterministic synthetic images.
It does not use private research images and does not claim production-scale performance.
