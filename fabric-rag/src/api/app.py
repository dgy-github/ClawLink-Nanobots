"""Minimal FastAPI demo for Fabric RAG MVP."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from ..pipeline.openclip_faiss import PipelineConfig, embed_query, load_clip_components, load_index_and_meta

app = FastAPI(title="Fabric RAG MVP")
CONFIG_PATH = Path("configs/baseline.yaml")
_cfg = PipelineConfig.from_yaml(CONFIG_PATH)
_index, _meta = load_index_and_meta(_cfg)
_model, _preprocess, _tokenizer, _device = load_clip_components(_cfg.embedding)


@app.get("/healthz")
def healthz():
    return {"status": "ok", "vectors": int(_index.ntotal)}


@app.post("/search/image")
def search_image(file: UploadFile = File(...), topk: int = 5):
    try:
        data = file.file.read()
        path = Path("/tmp/uploaded_image.jpg")
        path.write_bytes(data)
    finally:
        file.file.close()
    query_vec = embed_query(_model, _preprocess, _tokenizer, _device, image=path, text=None)
    distances, ids = _index.search(query_vec, topk)
    hits = []
    for score, idx in zip(distances[0], ids[0]):
        if idx < 0 or idx >= len(_meta):
            continue
        row = _meta.iloc[int(idx)]
        hits.append(
            {
                "score": float(score),
                "path": row.get("path"),
                "label": row.get("label"),
                "metadata": json.loads(row.get("meta_json", "{}")),
            }
        )
    return {"results": hits}


@app.post("/search/text")
def search_text(query: str, topk: int = 5):
    if not query:
        raise HTTPException(status_code=400, detail="query text required")
    query_vec = embed_query(_model, _preprocess, _tokenizer, _device, image=None, text=query)
    distances, ids = _index.search(query_vec, topk)
    hits = []
    for score, idx in zip(distances[0], ids[0]):
        if idx < 0 or idx >= len(_meta):
            continue
        row = _meta.iloc[int(idx)]
        hits.append(
            {
                "score": float(score),
                "path": row.get("path"),
                "label": row.get("label"),
                "metadata": json.loads(row.get("meta_json", "{}")),
            }
        )
    return {"results": hits}
