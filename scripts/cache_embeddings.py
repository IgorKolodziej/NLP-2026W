#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import platform
import time
from importlib.metadata import version

import numpy as np
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer

from clickbait.config import load_config, repo_root
from clickbait.embeddings import load_embeddings, save_embeddings
from clickbait.splits import load_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Cache a MiniLM pilot on temporal_main training posts.")
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    parser.add_argument("--sample-size", type=int, default=64)
    args = parser.parse_args()
    if args.sample_size < 1:
        parser.error("--sample-size must be positive")
    if args.device == "cuda" and not torch.cuda.is_available():
        parser.error("CUDA is unavailable; use --device cpu")

    cfg = load_config()
    root = repo_root()
    settings = cfg["embeddings"]
    source = root / cfg["paths"]["data_processed"] / "posts.parquet"
    manifest = load_manifest(root / cfg["paths"]["splits"] / "temporal_main.json")
    posts = pd.read_parquet(source, columns=["post_id", "post_text"])
    train = posts.set_index("post_id").loc[manifest.train_ids].reset_index()
    sample = train.sample(n=args.sample_size, random_state=int(cfg["random_seed"]))

    start = time.perf_counter()
    model = SentenceTransformer(
        cfg["embedding_model"],
        revision=settings["revision"],
        device=args.device,
        cache_folder=str(root / cfg["paths"]["cache"] / "models"),
    ).float()
    model.requires_grad_(False)
    model.max_seq_length = int(settings["max_seq_length"])
    load_seconds = time.perf_counter() - start

    start = time.perf_counter()
    vectors = model.encode(
        sample["post_text"].tolist(),
        batch_size=int(settings["batch_size"]),
        precision="float32",
        normalize_embeddings=bool(settings["normalize_embeddings"]),
        convert_to_numpy=True,
        show_progress_bar=True,
    )
    encode_seconds = time.perf_counter() - start

    metadata = {
        "scope": "temporal_main/train/pilot",
        "sample_seed": int(cfg["random_seed"]),
        "model_id": cfg["embedding_model"],
        "model_revision": settings["revision"],
        "max_seq_length": model.max_seq_length,
        "normalize_embeddings": bool(settings["normalize_embeddings"]),
        "batch_size": int(settings["batch_size"]),
        "device": str(model.device),
        "torch_threads": torch.get_num_threads(),
        "python_version": platform.python_version(),
        "package_versions": {
            name: version(name)
            for name in ("numpy", "pandas", "torch", "sentence-transformers", "transformers", "tokenizers", "huggingface-hub")
        },
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "uv_lock_sha256": hashlib.sha256((root / "uv.lock").read_bytes()).hexdigest(),
        "timing_seconds": {"model_load": load_seconds, "encode": encode_seconds},
    }
    output = root / cfg["paths"]["cache"] / "embeddings" / "pilot"
    save_embeddings(output, sample, vectors, metadata)
    np.testing.assert_array_equal(load_embeddings(output, sample), vectors)
    print(f"Saved and reloaded {len(sample)} embeddings with shape {vectors.shape} on {model.device}")
    print(f"Encoding: {encode_seconds:.3f} s; cache: {output.relative_to(root)}")


if __name__ == "__main__":
    main()
