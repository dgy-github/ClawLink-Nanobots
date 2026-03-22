"""OpenCLIP + FAISS pipeline utilities for Fabric RAG MVP."""
from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

import faiss
import numpy as np
import open_clip
import pandas as pd
import torch
import torch.nn.functional as F
import yaml
from PIL import Image, ImageFile

from . import utils
from ..data.loader import DatasetConfig, iter_dataset_entries, load_dataset_configs

ImageFile.LOAD_TRUNCATED_IMAGES = True


@dataclass
class EmbeddingConfig:
    model_name: str
    pretrained: str
    batch_size: int = 32
    device: str = "auto"

    @property
    def resolved_device(self) -> torch.device:
        if self.device == "auto":
            return torch.device("cuda" if torch.cuda.is_available() else "cpu")
        return torch.device(self.device)


@dataclass
class FaissConfig:
    dim: int
    factory: str
    nprobe: int = 16


@dataclass
class IndexConfig:
    output_dir: Path
    metadata_path: Path

    @property
    def index_path(self) -> Path:
        return self.output_dir / "index.faiss"


@dataclass
class PipelineConfig:
    embedding: EmbeddingConfig
    faiss: FaissConfig
    index: IndexConfig
    datasets: List[DatasetConfig]
    log_dir: Path
    summary_file: Path

    @classmethod
    def from_yaml(cls, path: Path, *, override_dataset: Optional[DatasetConfig] = None) -> "PipelineConfig":
        with open(path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        embedding = EmbeddingConfig(**config["embedding"])
        faiss_cfg = FaissConfig(**config["faiss"])
        index_cfg = config.get("index", {})
        index = IndexConfig(
            output_dir=Path(index_cfg.get("output_dir", "data/indexes/baseline")),
            metadata_path=Path(index_cfg.get("metadata_path", "data/indexes/baseline/index_meta.parquet")),
        )
        datasets = [override_dataset] if override_dataset else load_dataset_configs(path)
        logging_conf = config.get("logging", {})
        log_dir = Path(logging_conf.get("log_dir", "logs"))
        summary_file = Path(logging_conf.get("summary_file", str(log_dir / "summary.json")))
        return cls(
            embedding=embedding,
            faiss=faiss_cfg,
            index=index,
            datasets=datasets,
            log_dir=log_dir,
            summary_file=summary_file,
        )


def gather_entries(datasets: Sequence[DatasetConfig]) -> List[Dict]:
    entries: List[Dict] = []
    for ds_cfg in datasets:
        ds_entries = list(iter_dataset_entries(ds_cfg))
        if not ds_entries:
            print(f"[warn] dataset '{ds_cfg.name}' at {ds_cfg.root} yielded 0 files")
        entries.extend(ds_entries)
    return entries


def chunked(seq: Sequence, size: int) -> Iterable[Sequence]:
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def load_clip_components(cfg: EmbeddingConfig):
    device = cfg.resolved_device
    model, _, preprocess = open_clip.create_model_and_transforms(cfg.model_name, pretrained=cfg.pretrained)
    tokenizer = open_clip.get_tokenizer(cfg.model_name)
    model = model.to(device)
    model.eval()
    return model, preprocess, tokenizer, device


def embed_batch(model, preprocess, device, batch_entries: Sequence[Dict]):
    images = []
    valid_entries = []
    for entry in batch_entries:
        try:
            img = Image.open(entry["path"]).convert("RGB")
        except Exception as err:  # pragma: no cover
            print(f"[warn] failed to open {entry['path']}: {err}")
            continue
        tensor = preprocess(img)
        images.append(tensor)
        valid_entries.append(entry)
    if not images:
        return None, []
    batch = torch.stack(images).to(device)
    with torch.no_grad():
        feats = model.encode_image(batch)
        feats = F.normalize(feats, dim=-1)
    embeddings = feats.cpu().numpy().astype(np.float32)
    return embeddings, valid_entries


def build_index(cfg: PipelineConfig, *, max_images: Optional[int] = None) -> Dict:
    entries = gather_entries(cfg.datasets)
    if not entries:
        raise RuntimeError("No dataset entries found. Check dataset paths or use --input-dir.")
    if max_images:
        entries = entries[:max_images]
    print(f"[info] Building index from {len(entries)} images ...")

    model, preprocess, _, device = load_clip_components(cfg.embedding)

    embedding_chunks: List[np.ndarray] = []
    metadata_records: List[Dict] = []
    next_id = 0
    start = time.time()

    for batch_entries in chunked(entries, cfg.embedding.batch_size):
        batch_embeddings, valid_entries = embed_batch(model, preprocess, device, batch_entries)
        if batch_embeddings is None:
            continue
        embedding_chunks.append(batch_embeddings)
        for entry in valid_entries:
            metadata_records.append(
                {
                    "image_id": next_id,
                    "dataset": entry.get("dataset"),
                    "label": entry.get("label"),
                    "path": str(entry.get("path")),
                    "meta_json": json.dumps(entry.get("metadata", {}), ensure_ascii=False),
                }
            )
            next_id += 1

    if not embedding_chunks:
        raise RuntimeError("No embeddings were produced. Ensure images are valid.")

    embeddings = np.vstack(embedding_chunks)
    feature_dim = embeddings.shape[1]
    if cfg.faiss.dim != feature_dim:
        print(f"[info] Adjusting FAISS dim from {cfg.faiss.dim} -> {feature_dim}")
        cfg.faiss.dim = feature_dim

    utils.ensure_dir(cfg.index.output_dir)
    utils.ensure_dir(cfg.index.metadata_path.parent)
    utils.ensure_dir(cfg.log_dir)
    utils.ensure_dir(cfg.summary_file.parent)

    index = faiss.index_factory(cfg.faiss.dim, cfg.faiss.factory)
    fallback_to_flat = False
    if isinstance(index, faiss.IndexIVF):
        if embeddings.shape[0] < index.nlist:
            print(
                f"[warn] dataset size ({embeddings.shape[0]}) < nlist ({index.nlist}); falling back to IndexFlatIP"
            )
            fallback_to_flat = True
        else:
            index.nprobe = cfg.faiss.nprobe
    if fallback_to_flat:
        index = faiss.IndexFlatIP(cfg.faiss.dim)
    if not index.is_trained:
        index.train(embeddings)
    index.add(embeddings)
    faiss.write_index(index, str(cfg.index.index_path))

    utils.save_metadata(metadata_records, cfg.index.metadata_path)

    duration = time.time() - start
    summary = {
        "num_vectors": int(index.ntotal),
        "dimension": int(cfg.faiss.dim),
        "factory": cfg.faiss.factory,
        "index_path": str(cfg.index.index_path),
        "metadata_path": str(cfg.index.metadata_path),
        "datasets": [ds.name for ds in cfg.datasets],
        "duration_sec": duration,
        "device": str(cfg.embedding.resolved_device),
    }
    with open(cfg.summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"[done] Saved index to {cfg.index.index_path} (took {duration:.1f}s)")
    return summary


def load_index_and_meta(cfg: PipelineConfig):
    if not cfg.index.index_path.exists():
        raise FileNotFoundError(f"Missing index at {cfg.index.index_path}")
    if not cfg.index.metadata_path.exists():
        raise FileNotFoundError(f"Missing metadata at {cfg.index.metadata_path}")
    index = faiss.read_index(str(cfg.index.index_path))
    metadata = pd.read_parquet(cfg.index.metadata_path)
    return index, metadata


def embed_query(model, preprocess, tokenizer, device, *, image: Optional[Path], text: Optional[str]):
    if image is None and text is None:
        raise ValueError("Provide --image or --text for querying.")
    with torch.no_grad():
        if image:
            img = Image.open(image).convert("RGB")
            tensor = preprocess(img).unsqueeze(0).to(device)
            feats = model.encode_image(tensor)
        else:
            tokens = tokenizer([text])
            feats = model.encode_text(tokens.to(device))
        feats = F.normalize(feats, dim=-1)
    return feats.cpu().numpy().astype(np.float32)


def query_index(cfg: PipelineConfig, *, image: Optional[Path], text: Optional[str], topk: int) -> List[Dict]:
    index, metadata = load_index_and_meta(cfg)
    model, preprocess, tokenizer, device = load_clip_components(cfg.embedding)
    query_vec = embed_query(model, preprocess, tokenizer, device, image=image, text=text)
    distances, ids = index.search(query_vec, topk)
    hits: List[Dict] = []
    for score, idx in zip(distances[0], ids[0]):
        if idx < 0 or idx >= len(metadata):
            continue
        row = metadata.iloc[int(idx)]
        hit = {
            "score": float(score),
            "image_id": int(row.get("image_id", idx)),
            "dataset": row.get("dataset"),
            "label": row.get("label"),
            "path": row.get("path"),
            "metadata": json.loads(row.get("meta_json", "{}")),
        }
        hits.append(hit)
    return hits


def print_hits(hits: List[Dict]) -> None:
    for idx, hit in enumerate(hits, start=1):
        label = hit.get("label") or "-"
        print(f"#{idx}: score={hit['score']:.4f} label={label} path={hit['path']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OpenCLIP + FAISS MVP pipeline")
    parser.add_argument("--config", type=Path, default=Path("configs/baseline.yaml"), help="Pipeline config path")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Build FAISS index from datasets")
    build_parser.add_argument("--input-dir", type=Path, help="Override to ingest an arbitrary folder (MVP mode)")
    build_parser.add_argument("--input-name", default="local", help="Name for override dataset")
    build_parser.add_argument(
        "--input-glob",
        default="**/*",
        help="Glob pattern for override dataset (default: include all files)",
    )
    build_parser.add_argument("--max-images", type=int, help="Optional limit for debugging")

    query_parser = subparsers.add_parser("query", help="Query existing index")
    query_parser.add_argument("--image", type=Path, help="Image file for search")
    query_parser.add_argument("--text", type=str, help="Text prompt for search")
    query_parser.add_argument("--topk", type=int, default=5, help="Number of results to return")

    return parser.parse_args()


def main():
    args = parse_args()
    override_dataset = None
    if args.command == "build" and args.input_dir:
        override_dataset = DatasetConfig(
            name=args.input_name,
            root=args.input_dir,
            glob=args.input_glob,
            label_key=None,
            metadata={"source": "local"},
        )
    cfg = PipelineConfig.from_yaml(args.config, override_dataset=override_dataset)

    if args.command == "build":
        build_index(cfg, max_images=getattr(args, "max_images", None))
    elif args.command == "query":
        hits = query_index(cfg, image=args.image, text=args.text, topk=args.topk)
        print_hits(hits)
        print(json.dumps(hits, ensure_ascii=False, indent=2))
    else:
        raise ValueError(f"Unknown command {args.command}")


if __name__ == "__main__":
    main()
