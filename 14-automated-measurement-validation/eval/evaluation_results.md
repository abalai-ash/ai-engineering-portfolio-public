# Measurement Evaluation Results

Cases: 11
Passed: 2
Warnings: 2
Failed: 7
Instrument errors: 4

| Case | Status | Samples | Errors | Drift | Summary |
|---|---|---:|---:|---:|---|
| nominal-voltage | pass | 8/8 | 0 | -0.040169 | The test passed because all readings stayed within the allowed limits. |
| temperature-warning | warning | 10/10 | 0 | 2.032733 | The test needs review because the readings showed measurable drift. |
| current-failure | fail | 10/10 | 0 | 0.420837 | The test failed because one or more readings exceeded the failure tolerance. |
| frequency-outlier | fail | 9/9 | 0 | 0.69158 | The test failed because one or more readings exceeded the failure tolerance. |
| stable-signal | pass | 12/12 | 0 | 0.046802 | The test passed because all readings stayed within the allowed limits. |
| instrument-connection-failure | fail | 0/6 | 1 | 0.0 | The test failed because the instrument connection could not be established. |
| instrument-timeout | fail | 6/7 | 1 | 0.004671 | The test failed because one or more instrument responses were missing or invalid. |
| invalid-instrument-response | fail | 6/7 | 1 | 0.047716 | The test failed because one or more instrument responses were missing or invalid. |
| conductivity-drift-warning | warning | 9/9 | 0 | 0.280676 | The test needs review because the readings showed measurable drift. |
| moisture-timeout-failure | fail | 7/8 | 1 | -0.02689 | The test failed because one or more instrument responses were missing or invalid. |
| temperature-outlier-failure | fail | 10/10 | 0 | 0.794592 | The test failed because one or more readings exceeded the failure tolerance. |

Expected checks passed: True

Synthetic measurement data used for a portfolio-scale engineering workflow.
