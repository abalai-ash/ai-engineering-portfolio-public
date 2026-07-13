# RAG v2 Evaluation Results

Passed: 7/7

| Question | Expected source | Top source | Expected status | Actual status | Score | Result |
|---|---|---|---|---|---:|---|
| Why should conclusions stay cautious when evidence is incomplete? | public_science_notes.txt | public_science_notes.txt | answered | answered | 0.8077 | PASS |
| Why should API keys not be committed to GitHub? | cloud_notes.txt | cloud_notes.txt | answered | answered | 0.9300 | PASS |
| Why are visual checks useful for sensor data? | sensor_notes.txt | sensor_notes.txt | answered | answered | 0.8250 | PASS |
| What can cause missing or delayed sensor readings? | sensor_notes.txt | sensor_notes.txt | answered | answered | 0.6347 | PASS |
| What should good deployment notes explain? | cloud_notes.txt | cloud_notes.txt | answered | answered | 1.0000 | PASS |
| Why should public science examples avoid overstating evidence? | public_science_notes.txt | public_science_notes.txt | answered | answered | 0.7751 | PASS |
| Who founded the North Ridge Observatory? | NONE | NONE | abstained | abstained | 0.0000 | PASS |

## Notes

This evaluation checks source retrieval and whether the system abstains when the documents do not contain enough evidence.
It does not claim that simple local retrieval solves every grounded-answer problem.
