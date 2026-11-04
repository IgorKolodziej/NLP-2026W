#!/usr/bin/env python3
from clickbait.config import load_config, repo_root


def main() -> None:
    cfg = load_config()
    assert cfg["random_seed"] == 42
    assert cfg["embedding_model"] == "sentence-transformers/all-MiniLM-L6-v2"
    assert cfg["logistic_regression"]["class_weight"] == "balanced"
    print(f"config ok (repo root: {repo_root()})")


if __name__ == "__main__":
    main()
