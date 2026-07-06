# RAG Evaluation Results

Passed: 5/5

| Question | Expected source | Top source | Score | Result |
|---|---|---|---:|---|
| Why should conclusions stay cautious when evidence is incomplete? | public_science_notes.txt | public_science_notes.txt | 5 | PASS |
| Why is it useful to check sensor data before using it? | sensor_notes.txt | sensor_notes.txt | 5 | PASS |
| Why should API keys not be committed to GitHub? | cloud_notes.txt | cloud_notes.txt | 6 | PASS |
| Why are visual checks useful for sensor data? | sensor_notes.txt | sensor_notes.txt | 4 | PASS |
| What makes cloud deployment useful for AI projects? | cloud_notes.txt | cloud_notes.txt | 4 | PASS |

## Notes

This checks whether the top retrieved chunk came from the expected source file.
It does not check the quality of the final answer yet.