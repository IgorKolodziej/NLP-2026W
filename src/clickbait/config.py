from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_CONFIG = _REPO_ROOT / "configs" / "experiment.yaml"


def repo_root() -> Path:
    return _REPO_ROOT


def load_config(path: Path | str | None = None) -> dict[str, Any]:
    config_path = Path(path) if path is not None else _DEFAULT_CONFIG
    if not config_path.is_file():
        raise FileNotFoundError(f"Config not found: {config_path}")
    with config_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {config_path}")
    return data
