# Cloud ML Deployment v2 Example

Start the local service:

```bash
python src/service_v2.py
The default address is:

```text
http://127.0.0.1:8085
```

Check service health:

```bash
curl http://127.0.0.1:8085/health
```

Send one prediction request:

```bash
curl   -X POST   -H "Content-Type: application/json"   -d '{"message":"urgent model deployment error please check api"}'   http://127.0.0.1:8085/predict
```

Send a batch request:

```bash
curl   -X POST   -H "Content-Type: application/json"   -d '{"messages":["general newsletter for later","urgent security failure blocked deployment"]}'   http://127.0.0.1:8085/predict/batch
```

This is still a local demonstration. It does not call an external model or cloud account.
