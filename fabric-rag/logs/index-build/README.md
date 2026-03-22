# Index Build Logs

Store JSON summaries for each index build here. Suggested schema:

```json
{
  "name": "baseline-local",
  "num_vectors": 2500,
  "dimension": 512,
  "factory": "IVF4096,PQ64",
  "duration_sec": 120.5,
  "device": "cuda",
  "datasets": ["local"],
  "notes": "first MVP run"
}
```
