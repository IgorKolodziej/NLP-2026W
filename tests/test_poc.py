import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

from clickbait.config import load_config
from clickbait.embeddings import EMBEDDING_DIM, encoding_spec, save_embeddings
from clickbait.poc import _stats, _subset, run_poc, verify_poc
from clickbait.splits import SplitManifest, write_manifest
from clickbait.tuning import candidate_c_values


class PocUnitTests(unittest.TestCase):
    def test_candidate_grid_is_sorted_and_unique(self):
        self.assertEqual(candidate_c_values({"grid_search": {"C": [10.0, 0.1, 1.0]}}), [0.1, 1.0, 10.0])

    def test_subset_preserves_manifest_order_and_stats(self):
        posts = pd.DataFrame({"post_id": ["a", "b", "c"], "label": [0, 1, 1], "post_text": ["a", "b", "c"]})
        selected = _subset(posts, ["c", "a"])
        self.assertEqual(selected["post_id"].tolist(), ["c", "a"])
        self.assertEqual(_stats(selected), {"n": 2, "positive": 1, "positive_rate": 0.5})


class PocIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for directory in ["data/processed", "cache/embeddings", "configs", "resources", "src/clickbait/models"]:
            (self.root / directory).mkdir(parents=True, exist_ok=True)
        source_root = Path(__file__).parents[1]
        source_files = ["resources/linguistic_cues.json", "src/clickbait/cues.py", "src/clickbait/tuning.py", "src/clickbait/models/neural.py", "src/clickbait/models/system_a.py", "src/clickbait/metrics.py", "src/clickbait/dataset.py", "src/clickbait/poc.py", "src/clickbait/poc_data.py", "src/clickbait/embeddings.py"]
        for relative in source_files:
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_root / relative, destination)
        (self.root / "configs/experiment.yaml").write_text("fixture\n")
        (self.root / "uv.lock").write_text("fixture lock\n")
        self.cfg = load_config()
        self.cfg.update({"paths": {"data_processed": "data/processed", "cache": "cache", "splits": "splits", "results": "results"}, "embedding_model": "fixture-model", "embeddings": {"revision": "fixture", "max_seq_length": 256, "normalize_embeddings": True}, "grid_search": {"C": [0.1, 1.0, 10.0], "tie_break": "smallest_C"}, "logistic_regression": {"class_weight": "balanced", "max_iter": 300, "solver": "lbfgs"}, "protocol": {"min_test_size": 1}, "training": {"refit_on": "train"}})
        rows = []
        index = 0
        for month, count in [("2016-12", 14), ("2017-01", 13), ("2017-02", 13), ("2017-03", 12), ("2017-04", 8)]:
            for offset in range(count):
                label = (offset + (0 if month == "2016-12" else 1)) % 2
                rows.append({"post_id": f"post-{index:03}", "post_text": f"{'amazing clickbait' if label else 'ordinary report'} item {index}", "label": label, "target_title": f"Title {index}", "year_month": month, "post_timestamp": month + "-01"})
                index += 1
        self.posts = pd.DataFrame(rows)
        self.posts.to_parquet(self.root / "data/processed/posts.parquet", index=False)
        train_ids = self.posts.loc[self.posts.year_month.isin(["2016-12", "2017-01", "2017-02"]), "post_id"].tolist()
        val_ids = self.posts.loc[self.posts.year_month.eq("2017-03"), "post_id"].tolist()
        test_ids = self.posts.loc[self.posts.year_month.eq("2017-04"), "post_id"].tolist()
        write_manifest(SplitManifest("temporal_main", "temporal", train_ids, val_ids, test_ids, {}), self.root / "splits")
        vectors = np.random.default_rng(42).normal(size=(len(self.posts), EMBEDDING_DIM)).astype(np.float32)
        vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
        save_embeddings(self.root / "cache/embeddings", self.posts[["post_id", "post_text"]], vectors, encoding_spec(self.cfg))
        self.audit = {"manifest": "temporal_main", "partitions": {"train": {"n": 40}, "val": {"n": 12}, "test": {"n": 8}}}

    def tearDown(self):
        self.tmp.cleanup()

    def _patches(self):
        return patch.multiple("clickbait.poc", repo_root=lambda: self.root, load_config=lambda: self.cfg, reconcile_raw=lambda root, posts, output_dir: {"cleaning": {"final_rows": len(posts)}}, audit_main=lambda posts, manifest, min_test_size: self.audit)

    def test_run_snapshots_before_test_prediction_and_verifies_without_fit(self):
        output = self.root / "results/poc/main"
        import clickbait.poc as poc
        original_predict = poc._predict
        def checked_predict(model, rows, system, cache_dir, cfg):
            self.assertTrue((output / "protocol.json").exists())
            self.assertTrue((self.root / "results/runs/poc/main/models" / f"model_{system.lower()}.pkl").exists())
            return original_predict(model, rows, system, cache_dir, cfg)
        with self._patches(), patch("clickbait.poc._predict", side_effect=checked_predict), patch("clickbait.poc_artifacts.export_artifacts", return_value={}):
            run_poc(output)
        with self._patches(), patch("clickbait.poc.fit_lr", side_effect=AssertionError("verify fitted a model")):
            self.assertTrue(verify_poc(output)["verified"])

    def test_verify_rejects_tampered_prediction(self):
        output = self.root / "results/poc/tamper"
        with self._patches(), patch("clickbait.poc_artifacts.export_artifacts", return_value={}):
            run_poc(output)
        predictions = output / "predictions.parquet"
        frame = pd.read_parquet(predictions)
        frame.loc[0, "p_clickbait_B"] += 0.01
        frame.to_parquet(predictions, index=False)
        with self.assertRaises(ValueError):
            verify_poc(output)

    def test_verify_rejects_tampered_model_input_and_summary(self):
        output = self.root / "results/poc/tamper-all"
        with self._patches(), patch("clickbait.poc_artifacts.export_artifacts", return_value={}):
            run_poc(output)
        model_path = self.root / "results/runs/poc/tamper-all/models/model_b.pkl"
        original_model = model_path.read_bytes()
        model_path.write_bytes(original_model + b"tampered")
        with self._patches(), self.assertRaises(ValueError):
            verify_poc(output)
        model_path.write_bytes(original_model)
        source = self.root / "data/processed/posts.parquet"
        original_source = source.read_bytes()
        source.write_bytes(original_source + b"tampered")
        with self._patches(), self.assertRaises(ValueError):
            verify_poc(output)
        source.write_bytes(original_source)
        summary_path = output / "summary.json"
        summary = json.loads(summary_path.read_text())
        summary["delta_macro_f1_C_minus_B"] = 99.0
        summary_path.write_text(json.dumps(summary))
        with self._patches(), self.assertRaises(ValueError):
            verify_poc(output)

    def test_artifact_failure_leaves_failure_without_summary(self):
        output = self.root / "results/poc/failure"
        with self._patches(), patch("clickbait.poc_artifacts.export_artifacts", side_effect=RuntimeError("render failed")):
            with self.assertRaisesRegex(RuntimeError, "render failed"):
                run_poc(output)
        self.assertTrue((output / "failure.json").exists())
        self.assertFalse((output / "summary.json").exists())


if __name__ == "__main__":
    unittest.main()
