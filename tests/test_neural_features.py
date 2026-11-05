import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from clickbait.cues import cues_matrix
from clickbait.embeddings import EMBEDDING_DIM, encoding_spec, save_embeddings
from clickbait.models.neural import build_cue_scaler, load_neural_inputs


class NeuralFeatureTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.cfg = {
            "embedding_model": "fixture-model",
            "embeddings": {"revision": "fixture", "max_seq_length": 256, "normalize_embeddings": True},
        }
        self.posts = pd.DataFrame(
            {
                "post_id": ["train-long", "train-short", "val-extreme", "val-phrase"],
                "post_text": ["YOU! 2 cats?", "a", "you " * 100 + "!", "must seem"],
            },
            index=[41, 7, 99, 13],
        )
        self.vectors = np.random.default_rng(42).normal(size=(4, EMBEDDING_DIM)).astype(np.float32)
        order = [2, 0, 3, 1]
        save_embeddings(
            self.directory, self.posts.iloc[order], self.vectors[order], encoding_spec(self.cfg),
        )

    def inputs(self, positions, system):
        return load_neural_inputs(self.posts.iloc[positions], self.directory, self.cfg, system)

    def test_id_alignment_and_embedding_equality(self):
        order = [3, 0, 2, 1]
        b = self.inputs(order, "B")
        c = self.inputs(order, "C")
        np.testing.assert_array_equal(b, self.vectors[order])
        np.testing.assert_array_equal(c[:, :EMBEDDING_DIM], b)
        self.assertEqual(b.shape, (4, 384))
        self.assertEqual(c.shape, (4, 396))
        for matrix in (b, c):
            self.assertEqual(matrix.dtype, np.float64)
            self.assertTrue(matrix.flags.c_contiguous)

    def test_cue_values_follow_documented_order(self):
        c = self.inputs([0], "C")
        expected = [12, 3, 8 / 3, 1, 1, 1, 3 / 7, 1, 1, 0, 0, 1]
        np.testing.assert_allclose(c[0, EMBEDDING_DIM:], expected)

    def test_literal_and_overlapping_phrase_matches(self):
        cues = cues_matrix(pd.Series(["must see", "must seem", "you won't believe"]))
        np.testing.assert_array_equal(cues[:, 10], [1, 1, 2])

    def test_train_only_scaling_and_embedding_passthrough(self):
        train = self.inputs([1, 0], "C")
        validation = self.inputs([2, 3], "C")
        original = train.copy()
        preprocessor = build_cue_scaler()
        transformed_train = preprocessor.fit_transform(train)
        transformed_val = preprocessor.transform(validation)
        scaler = preprocessor.named_transformers_["cues"]

        self.assertEqual(scaler.n_samples_seen_, 2)
        self.assertEqual(scaler.mean_[0], 6.5)
        self.assertEqual(scaler.scale_[0], 5.5)
        np.testing.assert_allclose(transformed_train[:, EMBEDDING_DIM], [-1, 1])
        np.testing.assert_allclose(transformed_val[:, EMBEDDING_DIM], [(401 - 6.5) / 5.5, (9 - 6.5) / 5.5])
        for raw, transformed in ((train, transformed_train), (validation, transformed_val)):
            np.testing.assert_array_equal(transformed[:, :EMBEDDING_DIM], raw[:, :EMBEDDING_DIM])
            self.assertEqual(transformed.shape, (2, 396))
            self.assertEqual(transformed.dtype, np.float64)
            self.assertTrue(transformed.flags.c_contiguous)
        np.testing.assert_array_equal(train, original)

        means, scales = scaler.mean_.copy(), scaler.scale_.copy()
        validation[:, EMBEDDING_DIM:] += 1e6
        preprocessor.transform(validation)
        np.testing.assert_array_equal(scaler.mean_, means)
        np.testing.assert_array_equal(scaler.scale_, scales)
        np.testing.assert_array_equal(preprocessor.transform(train), transformed_train)

    def test_constant_training_cue_is_retained(self):
        preprocessor = build_cue_scaler()
        preprocessor.fit(self.inputs([0, 1], "C"))
        validation = preprocessor.transform(self.inputs([3], "C"))
        scaler = preprocessor.named_transformers_["cues"]
        self.assertEqual(scaler.var_[10], 0)
        self.assertEqual(scaler.scale_[10], 1)
        self.assertEqual(validation[0, EMBEDDING_DIM + 10], 1)
        self.assertTrue(np.isfinite(validation).all())


if __name__ == "__main__":
    unittest.main()
