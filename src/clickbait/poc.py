"""One temporal-window A/B/C proof-of-concept run and verifier."""

from __future__ import annotations

import hashlib
import json
import os
import pickle
import platform
import resource
import subprocess
import time
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from clickbait.config import load_config, repo_root
from clickbait.metrics import evaluate_split
from clickbait.models.neural import load_neural_inputs, train_neural_validation
from clickbait.models.system_a import build_system_a_pipeline
from clickbait.poc_data import audit_main, reconcile_raw
from clickbait.splits import load_manifest
from clickbait.tuning import fit_lr, make_lr, tune_lr_c

SYSTEMS = ("A", "B", "C")
PACKAGES = ("numpy", "pandas", "scikit-learn", "scipy", "pyarrow")


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _subset(posts: pd.DataFrame, ids: list[str]) -> pd.DataFrame:
    return posts.set_index("post_id").loc[ids].reset_index()


def _stats(rows: pd.DataFrame) -> dict[str, Any]:
    return {"n": int(len(rows)), "positive": int(rows["label"].sum()), "positive_rate": float(rows["label"].mean())}


def _rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if platform.system() == "Darwin" else value * 1024)


def _versions() -> dict[str, str]:
    result = {}
    for package in PACKAGES:
        try:
            result[package] = version(package)
        except PackageNotFoundError:
            result[package] = "missing"
    return result


def _train_a(train: pd.DataFrame, val: pd.DataFrame, cfg: dict[str, Any]) -> tuple[Pipeline, dict[str, Any]]:
    started = time.perf_counter()
    vectorizer = build_system_a_pipeline()
    vectorizer.fit(train["post_text"], train["label"])
    x_train = vectorizer.transform(train["post_text"])
    x_val = vectorizer.transform(val["post_text"])
    best_c, best_score, candidates = tune_lr_c(x_train, train["label"].to_numpy(), x_val, val["label"].to_numpy(), cfg, int(cfg["random_seed"]))
    classifier = fit_lr(make_lr(best_c, cfg, int(cfg["random_seed"])), x_train, train["label"].to_numpy())
    model = Pipeline([("tfidf", vectorizer.named_steps["tfidf"]), ("classifier", classifier)])
    probability = model.predict_proba(val["post_text"])[:, 1]
    prediction = model.predict(val["post_text"])
    return model, {
        "selected_C": best_c,
        "validation": evaluate_split(val["label"].to_numpy(), probability, prediction),
        "tuning": {"protocol": "fixed grid on validation macro-F1; refit on train only", "candidates": candidates, "validation_macro_f1_at_best_C": best_score, "tie_break": "smallest_C"},
        "timing_seconds": {"fit_and_tune": time.perf_counter() - started},
    }


def _predict(model: Any, rows: pd.DataFrame, system: str, cache_dir: Path, cfg: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    features = rows["post_text"] if system == "A" else load_neural_inputs(rows, cache_dir, cfg, system)
    return model.predict(features), model.predict_proba(features)[:, 1]


def _input_paths(root: Path, cfg: dict[str, Any], manifest_path: Path, cache_dir: Path) -> list[Path]:
    return [
        root / cfg["paths"]["data_processed"] / "posts.parquet", manifest_path,
        cache_dir / "meta.json", cache_dir / "embeddings.npz",
        root / "configs" / "experiment.yaml", root / "uv.lock",
        root / "resources" / "linguistic_cues.json",
        root / "src" / "clickbait" / "cues.py", root / "src" / "clickbait" / "tuning.py",
        root / "src" / "clickbait" / "models" / "neural.py",
        root / "src" / "clickbait" / "models" / "system_a.py",
        root / "src" / "clickbait" / "metrics.py", root / "src" / "clickbait" / "dataset.py",
        root / "src" / "clickbait" / "poc.py", root / "src" / "clickbait" / "poc_data.py",
        root / "src" / "clickbait" / "embeddings.py",
    ]


def _git_revision(root: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _hardware() -> dict[str, Any]:
    cpu = platform.processor() or platform.machine()
    if platform.system() == "Darwin":
        try:
            cpu = subprocess.check_output(
                ["sysctl", "-n", "machdep.cpu.brand_string"], text=True, stderr=subprocess.DEVNULL,
            ).strip()
        except (OSError, subprocess.CalledProcessError):
            pass
    return {
        "platform": platform.platform(), "cpu": cpu, "logical_cpus": os.cpu_count(),
        "thread_limits": {key: os.environ.get(key) for key in ("OMP_NUM_THREADS", "MKL_NUM_THREADS")},
    }


def run_poc(output_dir: Path | None = None, split_name: str = "temporal_main") -> dict[str, Any]:
    root = repo_root()
    cfg = load_config()
    started = time.perf_counter()
    output = (Path(output_dir) if output_dir else root / "results" / "poc" / time.strftime("%Y%m%d-%H%M%S")).resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"PoC output exists and is non-empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    try:
        source = root / cfg["paths"]["data_processed"] / "posts.parquet"
        manifest_path = root / cfg["paths"]["splits"] / f"{split_name}.json"
        cache_dir = root / cfg["paths"]["cache"] / "embeddings"
        posts = pd.read_parquet(source)
        manifest = load_manifest(manifest_path)
        audit = audit_main(posts, manifest, int(cfg.get("protocol", {}).get("min_test_size", 1000)))
        raw_audit = reconcile_raw(root, posts, output)
        train, val, test = (_subset(posts, ids) for ids in (manifest.train_ids, manifest.val_ids, manifest.test_ids))
        partitions = {"train": _stats(train), "val": _stats(val), "test": _stats(test)}
        paths = _input_paths(root, cfg, manifest_path, cache_dir)
        missing = [str(path) for path in paths if not path.exists()]
        if missing:
            raise FileNotFoundError("Missing PoC inputs: " + ", ".join(missing))
        models: dict[str, Any] = {}
        details: dict[str, Any] = {}
        model_paths = root / "results" / "runs" / "poc" / output.name / "models"
        if model_paths.exists() and any(model_paths.iterdir()):
            raise FileExistsError(f"Saved models already exist: {model_paths}")
        model_paths.mkdir(parents=True, exist_ok=True)
        models["A"], details["A"] = _train_a(train, val, cfg)
        for system in ("B", "C"):
            model, detail, _ = train_neural_validation(train[["post_id", "post_text", "label"]], val[["post_id", "post_text", "label"]], cache_dir, cfg, system)
            models[system] = model
            details[system] = {"selected_C": detail["best_C"], "validation": detail["validation"], "tuning": detail["tuning"], "timing_seconds": detail["timing_seconds"]}
        model_hashes = {}
        for system, model in models.items():
            path = model_paths / f"model_{system.lower()}.pkl"
            with path.open("wb") as stream:
                pickle.dump(model, stream)
            model_hashes[system] = _hash(path)
        protocol = {
            "status": "pilot", "split": split_name, "split_type": manifest.split_type, "config": cfg,
            "partitions": partitions, "audit": audit, "raw_audit": raw_audit,
            "grid": cfg["grid_search"]["C"], "tie_break": "smallest_C", "cue_specification": "mechanism_cues",
            "selected_C": {system: details[system]["selected_C"] for system in SYSTEMS}, "model_hashes": model_hashes,
            "input_hashes": {str(path.relative_to(root)): _hash(path) for path in paths},
            "python_version": platform.python_version(), "package_versions": _versions(), "git_revision": _git_revision(root),
            "hardware": _hardware(),
            "model_paths": {system: str((model_paths / f"model_{system.lower()}.pkl").relative_to(root)) for system in SYSTEMS},
        }
        (output / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n", encoding="utf-8")
        predictions = {"post_id": test["post_id"].tolist(), "partition": ["test"] * len(test), "y_true": test["label"].to_numpy()}
        inference_started = time.perf_counter()
        for system, model in models.items():
            system_started = time.perf_counter()
            prediction, probability = _predict(model, test, system, cache_dir, cfg)
            predictions[f"y_pred_{system}"] = prediction
            predictions[f"p_clickbait_{system}"] = probability
            details[system].setdefault("timing_seconds", {})["test_inference"] = time.perf_counter() - system_started
            details[system]["test"] = evaluate_split(test["label"].to_numpy(), probability, prediction)
        predictions_frame = pd.DataFrame(predictions)
        predictions_frame.to_parquet(output / "predictions.parquet", index=False)
        summary = {"split": split_name, "partitions": partitions, "audit": audit, "raw_audit": raw_audit, "systems": details,
                   "delta_macro_f1_C_minus_B": details["C"]["test"]["macro_f1"] - details["B"]["test"]["macro_f1"],
                   "timing_seconds": {"total": time.perf_counter() - started, "test_inference": time.perf_counter() - inference_started},
                   "hardware": {**_hardware(), "peak_rss_bytes": _rss_bytes()},
                   "measurement": {
                       "test_inference": "feature loading/construction plus predict and predict_proba; cached encoder, no embedding generation",
                       "peak_rss": "process-wide high-water host RSS including reconciliation, all models and figure export; not per-model",
                       "total": "runner after imports, including reconciliation, fitting, test scoring and artifact export; excludes dependency/model downloads and cache construction",
                   },
                   "artifacts": {"protocol": "protocol.json", "predictions": "predictions.parquet", "models": str(model_paths.relative_to(root))}}
        from clickbait.poc_artifacts import export_artifacts
        summary["presentation"] = export_artifacts(posts, manifest, summary, predictions_frame, output / "artifacts")
        summary["timing_seconds"]["total"] = time.perf_counter() - started
        summary["hardware"]["peak_rss_bytes"] = _rss_bytes()
        (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        return summary
    except Exception as error:
        (output / "failure.json").write_text(json.dumps({"error": type(error).__name__, "message": str(error)}, indent=2) + "\n", encoding="utf-8")
        raise


def verify_poc(output_dir: Path) -> dict[str, Any]:
    root = repo_root()
    cfg = load_config()
    output = Path(output_dir)
    protocol = json.loads((output / "protocol.json").read_text(encoding="utf-8"))
    if protocol["package_versions"] != _versions():
        raise ValueError("Frozen package versions differ from the current environment")
    manifest_path = root / cfg["paths"]["splits"] / f"{protocol['split']}.json"
    cache_dir = root / cfg["paths"]["cache"] / "embeddings"
    source = root / cfg["paths"]["data_processed"] / "posts.parquet"
    paths = _input_paths(root, cfg, manifest_path, cache_dir)
    for path in paths:
        key = str(path.relative_to(root))
        if protocol["input_hashes"].get(key) != _hash(path):
            raise ValueError(f"Frozen input changed: {key}")
    for system in SYSTEMS:
        path = root / protocol["model_paths"][system]
        if protocol["model_hashes"][system] != _hash(path):
            raise ValueError(f"Frozen model changed: {system}")
    manifest = load_manifest(manifest_path)
    posts = pd.read_parquet(source)
    test = _subset(posts, manifest.test_ids)
    predictions = pd.read_parquet(output / "predictions.parquet")
    if predictions["post_id"].tolist() != manifest.test_ids or predictions["y_true"].tolist() != test["label"].tolist():
        raise ValueError("Saved test IDs or labels differ from current manifest/data")
    if predictions["partition"].tolist() != ["test"] * len(test):
        raise ValueError("Saved prediction partition must be test")
    summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
    recalculated = {}
    for system in SYSTEMS:
        with (root / protocol["model_paths"][system]).open("rb") as stream:
            model = pickle.load(stream)
        prediction, probability = _predict(model, test, system, cache_dir, cfg)
        if not np.array_equal(predictions[f"y_pred_{system}"].to_numpy(), prediction) or not np.allclose(predictions[f"p_clickbait_{system}"], probability, atol=1e-12, rtol=1e-10):
            raise ValueError(f"Reloaded {system} predictions differ")
        recalculated[system] = evaluate_split(test["label"].to_numpy(), probability, prediction)
        if recalculated[system] != summary["systems"][system]["test"]:
            raise ValueError(f"Saved {system} metrics differ from recomputation")
    delta = recalculated["C"]["macro_f1"] - recalculated["B"]["macro_f1"]
    if not np.isclose(delta, summary["delta_macro_f1_C_minus_B"], atol=1e-12, rtol=1e-10):
        raise ValueError("Saved C-minus-B delta differs from recomputation")
    result = dict(summary)
    result["verified"] = True
    return result
