# v2 Scientific Image Search Outputs

## Example query

```text
bright ring disk
```

## Example output

```text
Scientific Image Search v2

Query: bright ring disk

Query interpretation:
- bright -> higher brightness
- ring/disk -> high roundness and ring score

Target vector:
- brightness: 8
- contrast: 7
- roundness: 9
- ring_score: 9
- edge_score: 5

Closest matches:

img1 | similarity 0.467 | distance 1.14 | bright ring disk
type: disk
reason: brightness close by 0.0; contrast close by 0.0

img2 | similarity 0.123 | distance 7.13 | faint smooth disk
type: disk
reason: roundness close by 1.0; ring_score close by 2.0

img6 | similarity 0.102 | distance 8.80 | edge-on disk
type: disk
reason: contrast close by 0.0; brightness close by 3.0
```

## Evaluation result

```text
Evaluation complete: 3/3 passed
```

## What v2 demonstrates

- scientific-feature search
- weighted distance scoring
- similarity ranking
- query-to-feature mapping
- match explanation
- evaluation of expected top result

The data is synthetic and does not include private research images.
