"""Generic dataset loader utilities for Fabric RAG."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, List, Optional

import yaml


@dataclass
class DatasetConfig:
    name: str
    root: Path
    glob: str = "**/*"
    label_key: Optional[str] = None
    split: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "DatasetConfig":
        return cls(
            name=data["name"],
            root=Path(data["root"]),
            glob=data.get("glob", "**/*"),
            label_key=data.get("label_key"),
            split=data.get("split"),
            metadata=data.get("metadata"),
        )


def load_dataset_configs(path: Path) -> List[DatasetConfig]:
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    datasets = config.get("datasets", [])
    return [DatasetConfig.from_dict(item) for item in datasets]


def iter_dataset_entries(ds_cfg: DatasetConfig) -> Iterator[Dict]:
    root = ds_cfg.root
    if not root.exists():
        return iter([])

    files = sorted(root.glob(ds_cfg.glob))

    def _iterator() -> Iterator[Dict]:
        for path in files:
            if not path.is_file():
                continue
            label = path.parent.name if ds_cfg.label_key else None
            yield {
                "path": path,
                "label": label,
                "dataset": ds_cfg.name,
                "metadata": ds_cfg.metadata or {},
            }

    return _iterator()
