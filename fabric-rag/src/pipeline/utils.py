"""Utility helpers for the OpenCLIP + FAISS pipeline."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import numpy as np
import pandas as pd


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def stack_embeddings(chunks: Iterable[np.ndarray]) -> np.ndarray:
    arrays: List[np.ndarray] = []
    for chunk in chunks:
        arrays.append(chunk.astype(np.float32))
    if not arrays:
        return np.zeros((0, 1), dtype=np.float32)
    return np.vstack(arrays)


def save_metadata(records: List[dict], path: Path) -> None:
    if not records:
        return
    df = pd.DataFrame(records)
    ensure_dir(path.parent)
    df.to_parquet(path, index=False)
