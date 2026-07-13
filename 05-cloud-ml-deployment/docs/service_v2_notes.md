# Service v2 Notes

Version 2 places the original priority classifier behind a small local HTTP service.

## Added behavior

- health and readiness routes
- single-message prediction
- batch prediction
- request validation
- request IDs
- structured JSON output
- clear 400, 404, and 500 responses
- structured access logs
- an automated service evaluation

## Why this was added

The first version focused on project layout, environment settings, prediction output, and a basic evaluation. The second version practices the parts around a model that make an application easier to run and inspect.

The classifier remains deliberately simple. The project does not claim to be a trained model, distributed inference system, or production cloud deployment.

## Current limitations

- the service runs on one local process
- it uses a hand-written classifier
- it has no authentication
- it does not use a database or queue
- it does not autoscale
- it does not collect production monitoring data
- it has not been load tested
