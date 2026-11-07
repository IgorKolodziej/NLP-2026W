import io
import json
import pickle
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

from clickbait.config import load_config
from clickbait.embeddings import EMBEDDING_DIM, encoding_spec, save_embeddings
from clickbait.metrics import evaluate_split
from clickbait.models.neural import train_b_validation
from clickbait.splits import SplitManifest, write_manifest
from clickbait.tuning import fit_lr, make_lr
from scripts import train_neural, train_system_a


class TrainingTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.cfg = load_config()
        self.cfg["randomized_search"]["n_iter"] = 3
        self.cfg["embedding_model"] = "fixture-model"
        self.cfg["embeddings"]["revision"] = "fixture"
        rng = np.random.default_rng(42)
        labels = np.tile([0, 0, 0, 1], 13)
        self.posts = pd.DataFrame({
            "post_id": [f"post-{i:03}" for i in range(52)],
            "post_text": [
                f"{'YOU will love these 12 facts!' if label else 'Ordinary council report'} story {i}"
                for i, label in enumerate(labels)
            ],
            "label": labels,
        })
        self.vectors = rng.normal(scale=0.02, size=(52, EMBEDDING_DIM)).astype(np.float32)
        self.vectors[:, 0] += 2 * labels - 1
        self.vectors /= np.linalg.norm(self.vectors, axis=1, keepdims=True)
        self.train_positions = rng.permutation(40)
        self.val_positions = rng.permutation(np.arange(40, 52))
        self.manifest = SplitManifest(
            "fixture", "temporal",
            self.posts.iloc[self.train_positions]["post_id"].tolist(),
            self.posts.iloc[self.val_positions]["post_id"].tolist(),
            ["unavailable-test-0", "unavailable-test-1"], {},
        )
        write_manifest(self.manifest, self.root / "splits")
        self.source = self.root / "data" / "processed" / "posts.parquet"
        self.source.parent.mkdir(parents=True)
        self.posts.iloc[rng.permutation(52)].to_parquet(self.source, index=False)
        self.cache_dir = self.root / "cache" / "embeddings"
        order = rng.permutation(52)
        save_embeddings(self.cache_dir, self.posts.iloc[order], self.vectors[order], encoding_spec(self.cfg))
        (self.root / "uv.lock").write_text("fixture lock\n")

    def run_b(self):
        with (
            patch.object(train_neural, "repo_root", return_value=self.root),
            patch.object(train_neural, "load_config", return_value=self.cfg),
            patch("sys.argv", ["scripts/train_neural.py", "--system", "B", "--split", "fixture"]),
            patch.object(train_neural.subprocess, "check_output", side_effect=["fixture-revision\n", ""]),
            redirect_stdout(io.StringIO()),
        ):
            train_neural.main()

    def test_b_exports_reproduce_validation_without_test_data(self):
        with (
            patch("clickbait.tuning.fit_lr", wraps=fit_lr) as search_fit,
            patch("clickbait.models.neural.fit_lr", wraps=fit_lr) as final_fit,
        ):
            self.run_b()
        self.assertEqual(search_fit.call_count, 3)
        final_fit.assert_called_once()
        x_train = self.vectors[self.train_positions].astype(np.float64)
        y_train = self.posts.iloc[self.train_positions]["label"].to_numpy()
        for call in search_fit.call_args_list + final_fit.call_args_list:
            np.testing.assert_array_equal(call.args[1], x_train)
            np.testing.assert_array_equal(call.args[2], y_train)

        summary = json.loads((self.root / "results" / "system_b_fixture_validation.json").read_text())
        self.assertEqual((summary["n_train"], summary["n_val"], summary["n_features"]), (40, 12, 384))
        self.assertEqual(summary["evaluation_partition"], "val")
        self.assertNotIn("test", summary)
        candidates = summary["tuning"]["candidates"]
        best = max(candidates, key=lambda row: row["validation_macro_f1"])
        self.assertEqual(summary["best_C"], best["C"])
        self.assertEqual(summary["validation"]["macro_f1"], best["validation_macro_f1"])
        with (self.root / summary["artifacts"]["model"]).open("rb") as f:
            model = pickle.load(f)
        reference = make_lr(summary["best_C"], self.cfg, 42).fit(x_train, y_train)
        np.testing.assert_array_equal(model.coef_, reference.coef_)
        np.testing.assert_array_equal(model.intercept_, reference.intercept_)
        predictions = pd.read_parquet(self.root / summary["artifacts"]["validation_predictions"])
        self.assertEqual(predictions["post_id"].tolist(), self.manifest.val_ids)
        self.assertEqual(predictions["partition"].unique().tolist(), ["val"])
        np.testing.assert_array_equal(predictions["y_true"], self.posts.iloc[self.val_positions]["label"])
        x_val = self.vectors[self.val_positions].astype(np.float64)
        np.testing.assert_array_equal(model.predict(x_val), predictions["y_pred"])
        np.testing.assert_array_equal(model.predict_proba(x_val)[:, 1], predictions["p_clickbait"])
        self.assertEqual(summary["validation"], evaluate_split(
            predictions["y_true"].to_numpy(), predictions["p_clickbait"].to_numpy(),
            predictions["y_pred"].to_numpy(),
        ))

    def test_b_failure_saves_diagnostics_without_success_artifacts(self):
        self.cfg["logistic_regression"]["max_iter"] = 1
        with self.assertRaisesRegex(SystemExit, "search aborted; details:"):
            self.run_b()
        results = self.root / "results"
        run_dir = results / "runs" / "b_fixture_validation"
        failure = json.loads((run_dir / "tuning_failure.json").read_text())
        self.assertEqual(failure["status"], "failed")
        self.assertEqual(len(failure["candidates"]), 1)
        self.assertFalse(failure["candidates"][0]["converged"])
        self.assertFalse((results / "system_b_fixture_validation.json").exists())
        self.assertFalse((run_dir / "model.pkl").exists())
        self.assertFalse((run_dir / "validation_predictions.parquet").exists())

    def test_b_rejects_refitting_on_validation(self):
        self.cfg["training"]["refit_on"] = "train_val"
        with self.assertRaisesRegex(ValueError, "training.refit_on: train"):
            train_b_validation(
                self.posts.iloc[self.train_positions], self.posts.iloc[self.val_positions],
                self.cache_dir, self.cfg,
            )

    def test_a_caller_accepts_tuning_history(self):
        test_posts = pd.DataFrame({
            "post_id": self.manifest.test_ids,
            "post_text": ["Ordinary council report", "YOU will love these 12 facts!"],
            "label": [0, 1],
        })
        pd.concat([self.posts, test_posts]).to_parquet(self.source, index=False)
        with (
            patch.object(train_system_a, "repo_root", return_value=self.root),
            patch.object(train_system_a, "load_config", return_value=self.cfg),
            patch("sys.argv", ["scripts/train_system_a.py", "--split", "fixture"]),
            redirect_stdout(io.StringIO()),
        ):
            train_system_a.main()
        summary = json.loads((self.root / "results" / "system_a_fixture.json").read_text())
        self.assertEqual(summary["system"], "A")
        self.assertEqual(summary["n_train"], 40)
        self.assertEqual(len(summary["tuning"]["candidates"]), 3)
        self.assertTrue(all(row["converged"] for row in summary["tuning"]["candidates"]))
        self.assertEqual(summary["validation"]["macro_f1"], summary["tuning"]["validation_macro_f1_at_best_C"])


if __name__ == "__main__":
    unittest.main()
