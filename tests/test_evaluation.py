import hashlib
import io
import json
import pickle
import tempfile
import unittest
from contextlib import redirect_stdout
from importlib.metadata import version
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
from scipy.special import expit
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, f1_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from clickbait.config import load_config
from clickbait.embeddings import EMBEDDING_DIM, encoding_spec, save_embeddings
from clickbait.evaluation import load_frozen_neural
from clickbait.models.neural import build_cue_scaler, load_neural_inputs
from clickbait.splits import SplitManifest, write_manifest
from clickbait.tuning import make_lr
from scripts import evaluate_neural


class FrozenEvaluationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.cfg = load_config()
        self.cfg["embedding_model"] = "fixture-model"
        self.cfg["embeddings"]["revision"] = "fixture"
        rng = np.random.default_rng(42)
        labels = np.tile([0, 1], 10)
        self.posts = pd.DataFrame({
            "post_id": [f"post-{i:03}" for i in range(20)],
            "post_text": [f"{'YOU! 12 things you must see!' if label else 'Council announces routine meeting'} {i}"
                          for i, label in enumerate(labels)],
            "label": labels,
        })
        vectors = rng.normal(scale=0.02, size=(20, EMBEDDING_DIM)).astype(np.float32)
        vectors[:, 0] += 2 * labels - 1
        vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
        self.cache_dir = self.root / "cache/embeddings"
        save_embeddings(self.cache_dir, self.posts.iloc[::-1], vectors[::-1], encoding_spec(self.cfg))
        self.source = self.root / "data/processed/posts.parquet"
        self.source.parent.mkdir(parents=True)
        self.posts.iloc[rng.permutation(20)].to_parquet(self.source, index=False)
        self.manifest = SplitManifest(
            "fixture", "temporal", self.posts.post_id.iloc[:12].tolist(),
            self.posts.post_id.iloc[12:16].tolist(), self.posts.post_id.iloc[[18, 16, 19, 17]].tolist(), {},
        )
        write_manifest(self.manifest, self.root / "splits")
        resources = self.root / "resources"
        resources.mkdir()
        (resources / "forward_reference.txt").write_text("must see\n")
        self.freeze_path = self.root / "results/frozen/fixture/protocol.json"
        self.freeze_path.parent.mkdir(parents=True)
        self.models = {}
        entries = {}
        for system in ("B", "C"):
            classifier = make_lr(0.5, self.cfg, 42)
            model = classifier if system == "B" else Pipeline([
                ("preprocessor", build_cue_scaler()), ("classifier", classifier),
            ])
            model.fit(load_neural_inputs(self.posts.iloc[:12], self.cache_dir, self.cfg, system), labels[:12])
            if system == "B":
                model.intercept_[:] = -20
            self.models[system] = model
            path = self.freeze_path.parent / f"model_{system.lower()}.pkl"
            with path.open("wb") as f:
                pickle.dump(model, f)
            entries[system] = {"file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "selected_C": 0.5}
        input_paths = ["data/processed/posts.parquet", "splits/fixture.json", "cache/embeddings/embeddings.npz",
                       "cache/embeddings/meta.json", "resources/forward_reference.txt"]
        self.frozen = {
            "split": "fixture", "config": self.cfg, "models": entries,
            "input_sha256": {p: hashlib.sha256((self.root / p).read_bytes()).hexdigest() for p in input_paths},
            "package_versions": {name: version(name) for name in ("numpy", "scipy", "scikit-learn")},
        }
        self.freeze_path.write_text(json.dumps(self.frozen))

    def run_cli(self):
        with (
            patch.object(evaluate_neural, "repo_root", return_value=self.root),
            patch("sys.argv", ["scripts/evaluate_neural.py", "--freeze", "results/frozen/fixture/protocol.json"]),
            patch.object(evaluate_neural.subprocess, "check_output", side_effect=["fixture-revision\n", ""]),
            redirect_stdout(io.StringIO()),
        ):
            evaluate_neural.main()

    def test_paired_predictions_match_reference_without_fitting(self):
        with (
            patch.object(LogisticRegression, "fit", side_effect=AssertionError("Test evaluation must not fit LR")),
            patch.object(StandardScaler, "fit", side_effect=AssertionError("Test evaluation must not fit a scaler")),
        ):
            self.run_cli()
        summary = json.loads((self.root / "results/bc_fixture_test.json").read_text())
        predictions_path = self.root / summary["paired_predictions"]
        predictions = pd.read_parquet(predictions_path)
        self.assertEqual(predictions.post_id.tolist(), self.manifest.test_ids)
        self.assertEqual(predictions.split.unique().tolist(), ["fixture"])
        self.assertEqual(predictions.partition.unique().tolist(), ["test"])
        self.assertEqual(summary["evaluation_partition"], "test")
        self.assertEqual(summary["n_test"], 4)
        self.assertEqual(summary["paired_predictions_sha256"], hashlib.sha256(predictions_path.read_bytes()).hexdigest())
        test_posts = self.posts.set_index("post_id").loc[self.manifest.test_ids].reset_index()
        np.testing.assert_array_equal(predictions.y_true, test_posts.label)
        for system in ("B", "C"):
            features = load_neural_inputs(test_posts, self.cache_dir, self.cfg, system)
            classifier = self.models[system]
            if system == "C":
                features = classifier.named_steps["preprocessor"].transform(features)
                classifier = classifier.named_steps["classifier"]
            scores = features @ classifier.coef_[0] + classifier.intercept_[0]
            expected_labels = (scores > 0).astype(int)
            expected_probabilities = expit(scores)
            np.testing.assert_array_equal(predictions[f"y_pred_{system}"], expected_labels)
            np.testing.assert_allclose(predictions[f"p_clickbait_{system}"], expected_probabilities, atol=1e-12)
            metrics = summary["systems"][system]["test"]
            self.assertEqual(metrics["macro_f1"], f1_score(test_posts.label, expected_labels, average="macro"))
            self.assertAlmostEqual(metrics["average_precision"], average_precision_score(test_posts.label, expected_probabilities))
            self.assertAlmostEqual(metrics["brier_score"], brier_score_loss(test_posts.label, expected_probabilities))
            entry = self.frozen["models"][system]
            self.assertEqual(entry["sha256"], hashlib.sha256((self.freeze_path.parent / entry["file"]).read_bytes()).hexdigest())
        expected_delta = summary["systems"]["C"]["test"]["macro_f1"] - summary["systems"]["B"]["test"]["macro_f1"]
        self.assertGreater(expected_delta, 0)
        self.assertEqual(summary["delta_macro_f1_C_minus_B"], expected_delta)
        self.assertEqual(summary["freeze_sha256"], hashlib.sha256(self.freeze_path.read_bytes()).hexdigest())

    def test_changed_inputs_are_rejected_before_test_labels_are_loaded(self):
        for relative in self.frozen["input_sha256"]:
            with self.subTest(path=relative):
                path = self.root / relative
                original = path.read_bytes()
                path.write_bytes(original + b"changed")
                try:
                    with patch.object(evaluate_neural.pd, "read_parquet") as read:
                        with self.assertRaisesRegex(ValueError, "Frozen input changed"):
                            self.run_cli()
                        read.assert_not_called()
                finally:
                    path.write_bytes(original)

    def test_changed_models_are_rejected(self):
        for system in ("B", "C"):
            with self.subTest(system=system):
                path = self.freeze_path.parent / self.frozen["models"][system]["file"]
                original = path.read_bytes()
                path.write_bytes(original + b"changed")
                try:
                    with self.assertRaisesRegex(ValueError, f"Frozen model changed: {system}"):
                        load_frozen_neural(self.root, self.freeze_path)
                finally:
                    path.write_bytes(original)

    def test_changed_environment_is_rejected(self):
        self.frozen["package_versions"]["scikit-learn"] = "0.0"
        self.freeze_path.write_text(json.dumps(self.frozen))
        with self.assertRaisesRegex(ValueError, "Frozen environment requires scikit-learn==0.0"):
            load_frozen_neural(self.root, self.freeze_path)


if __name__ == "__main__":
    unittest.main()
