#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd
from clickbait.config import load_config, repo_root
from clickbait.embeddings import encoding_spec, load_embeddings, save_embeddings, validate_split_coverage
from clickbait.splits import load_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Cache frozen MiniLM embeddings for all processed posts.")
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    parser.add_argument("--sample-size", type=int, help="Encode a training-only pilot instead of the full dataset")
    parser.add_argument("--check", action="store_true", help="Validate the saved cache without loading MiniLM")
    parser.add_argument("--local-files-only", action="store_true", help="Use previously downloaded model files")
    args = parser.parse_args()
    if args.sample_size is not None and args.sample_size < 1:
        parser.error("--sample-size must be positive")

    cfg = load_config()
    root = repo_root()
    settings = cfg["embeddings"]
    source = root / cfg["paths"]["data_processed"] / "posts.parquet"
    splits_dir = root / cfg["paths"]["splits"]
    posts = pd.read_parquet(source, columns=["post_id", "post_text"])
    coverage = validate_split_coverage(posts, splits_dir)
    output = root / cfg["paths"]["cache"] / "embeddings"
    scope = "webis17/processed"
    if args.sample_size is not None:
        manifest = load_manifest(splits_dir / "temporal_main.json")
        train = posts.set_index("post_id").loc[manifest.train_ids].reset_index()
        posts = train.sample(n=args.sample_size, random_state=int(cfg["random_seed"]))
        output = output / "pilot"
        scope = "temporal_main/train/pilot"
        coverage = {}
    coverage_note = f"; {len(coverage)} split manifests covered" if args.sample_size is None else ""

    if args.check:
        vectors = load_embeddings(output, posts, cfg)
        metadata = json.loads((output / "meta.json").read_text(encoding="utf-8"))
        if metadata["scope"] != scope or metadata["n_rows"] != len(posts):
            raise ValueError("Cache scope or row count differs from the requested dataset")
        if settings["normalize_embeddings"]:
            np.testing.assert_allclose(np.linalg.norm(vectors, axis=1), 1.0, atol=1e-6, rtol=0)
        print(f"Verified {len(posts)} embeddings for {scope}{coverage_note}")
        return

    import torch
    from sentence_transformers import SentenceTransformer

    if args.device == "cuda" and not torch.cuda.is_available():
        parser.error("CUDA is unavailable; use --device cpu")
    if args.device == "cuda":
        torch.cuda.reset_peak_memory_stats()

    start = time.perf_counter()
    model = SentenceTransformer(
        cfg["embedding_model"],
        revision=settings["revision"],
        device=args.device,
        cache_folder=str(root / cfg["paths"]["cache"] / "models"),
        local_files_only=args.local_files_only,
    ).float()
    model.requires_grad_(False)
    model.max_seq_length = int(settings["max_seq_length"])
    load_seconds = time.perf_counter() - start

    texts = posts["post_text"].tolist()
    start = time.perf_counter()
    token_lengths = [
        len(ids) for ids in model.tokenizer(
            texts, truncation=False, return_attention_mask=False, return_token_type_ids=False,
        )["input_ids"]
    ]
    token_audit_seconds = time.perf_counter() - start

    if args.device == "cuda":
        torch.cuda.synchronize()
    start = time.perf_counter()
    vectors = model.encode(
        texts,
        batch_size=int(settings["batch_size"]),
        precision="float32",
        normalize_embeddings=bool(settings["normalize_embeddings"]),
        convert_to_numpy=True,
        show_progress_bar=True,
    )
    if args.device == "cuda":
        torch.cuda.synchronize()
    encode_seconds = time.perf_counter() - start

    start = time.perf_counter()
    norms = np.linalg.norm(vectors, axis=1)
    if settings["normalize_embeddings"]:
        np.testing.assert_allclose(norms, 1.0, atol=1e-6, rtol=0)
    selected = np.random.default_rng(int(cfg["random_seed"])).choice(len(posts), min(5, len(posts)), replace=False)
    direct = model.encode(
        posts.iloc[selected]["post_text"].tolist(), batch_size=1, precision="float32",
        normalize_embeddings=bool(settings["normalize_embeddings"]), show_progress_bar=False,
    )
    np.testing.assert_allclose(vectors[selected], direct, atol=1e-6, rtol=1e-5)
    verification_seconds = time.perf_counter() - start

    cpu_model = platform.processor()
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.exists():
        cpu_model = next(
            (line.split(":", 1)[1].strip() for line in cpuinfo.read_text().splitlines() if line.startswith("model name")),
            cpu_model,
        )
    metadata = {
        **encoding_spec(cfg),
        "scope": scope,
        "sample_seed": int(cfg["random_seed"]) if args.sample_size is not None else None,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": shlex.join(["uv", "run", "--locked", "python", *sys.argv]),
        "git_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
        "code_dirty": bool(subprocess.check_output(
            ["git", "status", "--porcelain", "--", "src", "scripts", "configs", "pyproject.toml", "uv.lock"],
            cwd=root, text=True,
        ).strip()),
        "model_files_local_only": args.local_files_only,
        "batch_size": int(settings["batch_size"]),
        "device": str(model.device),
        "torch_threads": torch.get_num_threads(),
        "hardware": {"platform": platform.platform(), "cpu_model": cpu_model, "logical_cpus": os.cpu_count()},
        "python_version": platform.python_version(),
        "package_versions": {
            name: version(name)
            for name in (
                "numpy", "pandas", "pyarrow", "torch", "sentence-transformers", "transformers",
                "tokenizers", "huggingface-hub", "safetensors",
            )
        },
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "uv_lock_sha256": hashlib.sha256((root / "uv.lock").read_bytes()).hexdigest(),
        "config_sha256": hashlib.sha256((root / "configs" / "experiment.yaml").read_bytes()).hexdigest(),
        "split_coverage": coverage,
        "tokenization": {
            "max_tokens_including_special_tokens": max(token_lengths),
            "truncated_posts": sum(length > model.max_seq_length for length in token_lengths),
        },
        "validation": {
            "seed": int(cfg["random_seed"]),
            "direct_reencoded_ids": posts.iloc[selected]["post_id"].tolist(),
            "max_absolute_reencoding_error": float(np.abs(vectors[selected] - direct).max()),
            "reencoding_atol": 1e-6,
            "reencoding_rtol": 1e-5,
            "max_norm_error": float(np.abs(norms - 1).max()),
        },
        "timing_seconds": {
            "model_load": load_seconds, "token_audit": token_audit_seconds,
            "encode": encode_seconds, "direct_verification": verification_seconds,
        },
    }
    if args.device == "cuda":
        metadata["hardware"]["gpu_model"] = torch.cuda.get_device_name()
        metadata["peak_cuda_allocated_bytes"] = torch.cuda.max_memory_allocated()
        metadata["peak_cuda_reserved_bytes"] = torch.cuda.max_memory_reserved()

    start = time.perf_counter()
    save_embeddings(output, posts, vectors, metadata)
    np.testing.assert_array_equal(load_embeddings(output, posts, cfg), vectors)
    save_reload_seconds = time.perf_counter() - start
    summary = json.loads((output / "meta.json").read_text(encoding="utf-8"))
    summary["timing_seconds"]["save_and_reload"] = save_reload_seconds
    summary["archive_bytes"] = (output / "embeddings.npz").stat().st_size
    summary_path = root / cfg["paths"]["results"] / "embedding_cache.json"
    if args.sample_size is not None:
        summary_path = output / "summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Saved and reloaded {len(posts)} embeddings with shape {vectors.shape} on {model.device}")
    print(f"Scope: {scope}{coverage_note}")
    print(f"Encoding: {encode_seconds:.3f} s; cache: {output.relative_to(root)}")


if __name__ == "__main__":
    main()
