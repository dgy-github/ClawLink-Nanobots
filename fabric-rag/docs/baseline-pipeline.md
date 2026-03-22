# Baseline Retrieval Pipeline (OpenCLIP + FAISS)

This document tracks the plan for a minimal retrieval stack we can run locally. The goal is to establish a reference implementation that can later ingest internal fabric data.

## Overview

1. **Data ingestion**: load a curated subset of public datasets (see `docs/datasets.md`). Start with DTD + VisTex + 1 Kaggle set to keep storage under ~10 GB.
2. **Feature extraction**: run OpenCLIP to embed all images. Use a ViT-B/32 backbone for speed; upgrade later if needed.
3. **Index building**: store embeddings in FAISS (flat or IVF). Persist `index.faiss` plus metadata (image path, label, optional attributes).
4. **Query API**: expose REST endpoints (FastAPI) for
   - image-to-image search (upload or reference path)
   - text-to-image search (CLIP text encoder)
   - metadata filtering (e.g., only woven fabrics)
5. **Evaluation + logging**: store recall@k and query latency metrics under `logs/`.

## Component Breakdown

### Data Loader (to live under `src/data/loader.py`)
- Accepts dataset configs describing
  ```yaml
  name: dtd
  root: data/dtd
  glob: "**/*.jpg"
  label_key: "class"
  split: train
  metadata: { source: "vgg" }
  ```
- Returns iterator of `{ "path": Path, "label": str, "meta": dict }`.
- Handles train/test splits when available.

### Feature Extractor (`src/pipeline/openclip_faiss.py`)
- Wrap OpenCLIP model loading, preprocessing, batching.
- Outputs normalized embeddings as `np.float32`.
- Keep device selection flexible (`cuda` if available, otherwise `cpu`).

### Index Builder
- Instantiate FAISS index via factory string (e.g., `"IVF4096,Flat"`).
- Maintain sidecar metadata: `index_meta.parquet` storing
  - image_id
  - dataset/source
  - label/attributes
  - path or blob identifier
- Provide CLI entrypoints:
  - `python -m src.pipeline.openclip_faiss build --config configs/baseline.yaml`
  - `python -m src.pipeline.openclip_faiss query --image path/to.jpg --topk 5`

### API Layer (`src/api/app.py` later)
- Use FastAPI; load FAISS index and metadata once at startup.
- Endpoints:
  - `POST /search/image`
  - `POST /search/text`
  - `GET /healthz`
- Add optional filtering via query params or request body (metadata masks, dataset selection).

### Logging & Monitoring
- Every index build writes summary JSON under `logs/index-build/` (size, dims, compression, duration).
- API logs query latency and top hits for manual review.

## Immediate Next Steps

- [x] Finalize bootstrap dataset list + estimated sizes (see `docs/datasets.md`).
- [x] Draft config schema (`configs/baseline.yaml`).
- [x] Create `data/scripts/download_public.sh` placeholder for dataset fetch commands.
- [ ] Implement `src/pipeline/openclip_faiss.py` build/query logic (currently skeleton).
- [ ] Add evaluation notebook (`notebooks/01_baseline_eval.ipynb`).
- [ ] Define metadata schema + persistence policy (`index_meta.parquet`).
- [ ] Scaffold FastAPI app (`src/api/app.py`) once index/query basics run locally.

## Dependencies

- `open-clip-torch`
- `faiss-cpu` (use `faiss-gpu` later if needed)
- `torch`
- `numpy`, `pandas`, `pyarrow` (for metadata)
- `fastapi`, `uvicorn`

Once the baseline is working end-to-end on public data, we can plug in internal samples, tune model choice, and benchmark against Baidu Cloud search.
