# Cloud ML Deployment Evaluation Results

Passed: 4/4

| Message | Expected label | Actual label | Result |
|---|---|---|---|
| urgent model deployment error please check api | high | high | PASS |
| please review cloud pipeline update | medium | medium | PASS |
| general newsletter for later | low | low | PASS |
| security failure blocked deployment | high | high | PASS |

## Notes

This checks whether the demo classifier returns the expected priority label.
The app uses fake messages and simple hand-written scoring. It does not use private data or external services.