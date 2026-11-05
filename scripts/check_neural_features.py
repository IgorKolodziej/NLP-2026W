#!/usr/bin/env python3
import argparse

import numpy as np
import pandas as pd

from clickbait.config import load_config, repo_root
from clickbait.cues import CUE_NAMES
from clickbait.embeddings import EMBEDDING_DIM
from clickbait.models.neural import build_cue_scaler, load_neural_inputs
from clickbait.splits import load_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Check B/C training and validation feature matrices.")
    parser.add_argument("--split", default="temporal_main")
    args = parser.parse_args()
    cfg = load_config()
    root = repo_root()
    manifest = load_manifest(root / cfg["paths"]["splits"] / f"{args.split}.json")
    posts = pd.read_parquet(
        root / cfg["paths"]["data_processed"] / "posts.parquet", columns=["post_id", "post_text"],
    ).set_index("post_id")
    cache_dir = root / cfg["paths"]["cache"] / "embeddings"
    preprocessor = build_cue_scaler()
    for partition, ids in (("train", manifest.train_ids), ("val", manifest.val_ids)):
        ordered = posts.loc[ids].reset_index()
        b = load_neural_inputs(ordered, cache_dir, cfg, "B")
        raw_c = load_neural_inputs(ordered, cache_dir, cfg, "C")
        c = preprocessor.fit_transform(raw_c) if partition == "train" else preprocessor.transform(raw_c)
        np.testing.assert_array_equal(c[:, :EMBEDDING_DIM], b)
        assert c.shape == (len(ids), EMBEDDING_DIM + len(CUE_NAMES))
        assert b.dtype == c.dtype == np.float64
        assert b.flags.c_contiguous and c.flags.c_contiguous
        assert np.isfinite(b).all() and np.isfinite(c).all()
        if partition == "train":
            scaled_cues = c[:, EMBEDDING_DIM:]
            varying = preprocessor.named_transformers_["cues"].var_ > 0
            np.testing.assert_allclose(scaled_cues.mean(axis=0), 0, atol=1e-10)
            np.testing.assert_allclose(scaled_cues[:, varying].std(axis=0), 1, atol=1e-10)
        print(f"{manifest.name}/{partition}: B={b.shape}, C={c.shape}; float64, finite, embeddings identical")
    n_train = int(preprocessor.named_transformers_["cues"].n_samples_seen_)
    print(f"Cue scaler fitted on {n_train} training posts")


if __name__ == "__main__":
    main()
