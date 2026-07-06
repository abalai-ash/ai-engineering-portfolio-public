# Example Outputs

This file keeps a short example from the first version of the Cloud ML Deployment project.

## Example message

```text
urgent model deployment error please check api
```

## Example output

```text
App: Cloud ML Demo
Environment: local
Prediction: high
Score: 13
Matched signals: {'high_priority': ['error', 'urgent'], 'ai_or_cloud': ['api', 'deployment', 'model'], 'action_words': ['check']}
Note: This is a local demo response. It does not use private data or external services.
```

## Current test result

```text
Evaluation complete: 4/4 passed
```

## Notes

This version is intentionally simple. It shows the app structure, config handling, prediction response, and evaluation before adding a real model or real deployment.
