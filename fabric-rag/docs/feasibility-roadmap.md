# Fabric RAG Feasibility & Requirements Route

_Last updated: 2026-03-22_

This document summarizes the inferred feasibility path for the fabric retrieval initiative, drawing on public predictive-model patterns (CLIP-style embeddings + vector search) and our current constraints.

## 1. Signals from Existing Predictive Models

| Signal | Implication for Fabric-RAG | Action |
| --- | --- | --- |
| OpenCLIP ViT-B/32 embeddings work well on heterogeneous texture datasets (per LAION + OpenCLIP papers). | Using the same backbone should capture most fabric-level semantics without custom training initially. | Proceed with OpenCLIP baseline; record embedding quality metrics (recall@k, mAP) on public texture sets. |
| FAISS IVF+PQ indexes remain the industry default for million-scale similarity search. | Low-risk choice for first release; GPU optional but not required for pilot. | Implement IVF4096,PQ64 baseline with nprobe tuning and log latency vs. quality trade-offs. |
| Retrieval quality improves significantly once domain-specific negatives/positives are included (cf. DeepFashion2, product search literature). | Fabric-specific datasets (Kaggle, VisTex, defect sets) must be curated before we can benchmark against Baidu Cloud. | Prioritize ≤10 GB bootstrap pack; log metadata (pattern, weave, lighting) for filtering. |
| Hybrid text+image queries (CLIP text encoder) enable attribute search with minimal extra compute. | Supporting text prompts (“striped denim”, “woven twill defect”) increases usability without bespoke training. | Add text encoder endpoints in API plan and evaluate cross-modal recall. |

## 2. Feasibility Route (Phased)

1. **Bootstrap Dataset Ingestion (Week 1)**
   - Download + verify DTD, VisTex, a Kaggle fabric set, Kylberg, and an AITEX subset (≤10 GB total).
   - Preserve metadata (class names, uploader notes, defect tags) for filtering.

2. **Baseline Pipeline (Week 1-2)**
   - Implement `src/pipeline/openclip_faiss.py` build/query commands.
   - Persist FAISS index + `index_meta.parquet` summarizing dataset, label, path, capture conditions.
   - Record build stats in `logs/index-build/` (size, duration, GPU usage).

3. **Evaluation + Logging (Week 2)**
   - Draft `notebooks/01_baseline_eval.ipynb` to measure recall@5/10 on held-out query sets.
   - Compare text vs. image query behavior; log examples in `logs/`.

4. **API Layer (Week 3)**
   - Scaffold FastAPI app with `/search/image`, `/search/text`, `/healthz`, and metadata filtering.
   - Integrate structured logging for latency + top hits.

5. **Extended Data & Fine-Tuning (Week 4+)**
   - Submit approvals for DeepFashion2, CUReT, AITEX full set.
   - Explore LoRA / adapter fine-tunes once internal samples become available.

## 3. Requirements Snapshot

| Area | Requirement | Status |
| --- | --- | --- |
| Data | ≤10 GB public bootstrap with clear licenses | In progress (Bootstrap Pack defined) |
| Compute | Single GPU (optional) or CPU-only fallback | Viable (OpenCLIP supports CPU, albeit slower) |
| Storage | Local SSD capable of ~20 GB (data + indexes) | Available |
| Metrics | Recall@k ≥ Baidu Cloud baseline on shared queries | To be measured |
| Logging | Structured build/query logs for reproducibility | Partially in place (logs directory) |
| Privacy | Keep proprietary textile images local; public datasets only for demos | Enforced |

## 4. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Dataset licensing delays (DeepFashion2, CUReT) | Medium | Slows domain adaptation | Use open CC datasets first; prep approval files early. |
| Embedding dimensionality mismatch (FAISS config vs. model output) | Low | Build failure | Validate config (`dim=512` for ViT-B/32) in unit tests before large runs. |
| Insufficient anomaly samples for defect search | Medium | Lower recall on defect queries | Integrate AITEX subset and augment with synthetic defect crops. |
| CPU-only performance too slow for demo | Medium | Demo latency | Add optional GPU path + pre-compute small subset for live demos. |

## 5. Next Documentation Tasks

- Fill `docs/approvals.md` once request forms submitted.
- Expand `docs/baseline-pipeline.md` with concrete CLI usage once pipeline script is implemented.
- Add benchmarking appendix comparing to Baidu Cloud once shared test cases are available.
