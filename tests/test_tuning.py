import copy
import unittest
from unittest.mock import patch

import numpy as np
from scipy.sparse import csr_matrix
from scipy.stats import loguniform
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score

from clickbait.config import load_config
from clickbait.tuning import TuningConvergenceError, fit_lr, make_lr, sample_c_values, tune_lr_c


class TuningTests(unittest.TestCase):
    def setUp(self):
        self.cfg = load_config()
        self.cfg["randomized_search"]["n_iter"] = 4
        rng = np.random.default_rng(17)
        x = rng.normal(size=(120, 6))
        y = (x[:, 0] - x[:, 1] + rng.normal(size=120) > 0.8).astype(int)
        self.x_train, self.x_val = x[:96], x[96:]
        self.y_train, self.y_val = y[:96], y[96:]

    def search(self, cfg=None):
        return tune_lr_c(self.x_train, self.y_train, self.x_val, self.y_val, cfg or self.cfg, 42)

    def test_dense_and_sparse_search_match_reference(self):
        values = loguniform.rvs(0.01, 100, size=4, random_state=np.random.default_rng(42))
        for convert in (np.asarray, csr_matrix):
            with self.subTest(matrix=convert.__name__):
                x_train, x_val = convert(self.x_train), convert(self.x_val)
                best_c, best_score, candidates = tune_lr_c(
                    x_train, self.y_train, x_val, self.y_val, self.cfg, 42,
                )
                np.testing.assert_array_equal([row["C"] for row in candidates], values)
                scores = []
                for value, row in zip(values, candidates):
                    model = LogisticRegression(
                        C=value, class_weight="balanced", max_iter=1000, solver="lbfgs", random_state=42,
                    ).fit(x_train, self.y_train)
                    score = f1_score(self.y_val, model.predict(x_val), average="macro", zero_division=0)
                    scores.append(score)
                    self.assertEqual(row["validation_macro_f1"], score)
                    self.assertTrue(row["converged"])
                    self.assertEqual(row["n_iter"], model.n_iter_[0])
                    self.assertGreaterEqual(row["fit_seconds"], 0)
                self.assertEqual(best_c, values[np.argmax(scores)])
                self.assertEqual(best_score, max(scores))

    def test_ties_keep_first_sampled_candidate(self):
        with patch("clickbait.tuning.sample_c_values", return_value=[3.0, 0.1, 1.0]):
            best_c, best_score, candidates = tune_lr_c(
                np.zeros_like(self.x_train), self.y_train,
                np.zeros_like(self.x_val), self.y_val, self.cfg, 42,
            )
        self.assertEqual(best_c, 3.0)
        self.assertEqual([row["validation_macro_f1"] for row in candidates], [best_score] * 3)

    def test_real_nonconvergence_aborts_search(self):
        self.cfg["logistic_regression"]["max_iter"] = 1
        with self.assertRaises(TuningConvergenceError) as caught:
            self.search()
        candidates = caught.exception.candidates
        self.assertEqual(len(candidates), 1)
        self.assertFalse(candidates[0]["converged"])
        self.assertIsNone(candidates[0]["validation_macro_f1"])
        self.assertIsNone(candidates[0]["n_iter"])
        self.assertIn("failed to converge", candidates[0]["warning"])

    def test_partial_history_is_retained_without_selecting_a_winner(self):
        def fail_second(model, x, y):
            if model.C == 2.0:
                raise ConvergenceWarning("fixture convergence failure")
            return fit_lr(model, x, y)

        with (
            patch("clickbait.tuning.sample_c_values", return_value=[1.0, 2.0, 3.0]),
            patch("clickbait.tuning.fit_lr", side_effect=fail_second) as fit,
            self.assertRaises(TuningConvergenceError) as caught,
        ):
            self.search()
        self.assertEqual(fit.call_count, 2)
        candidates = caught.exception.candidates
        self.assertEqual([row["C"] for row in candidates], [1.0, 2.0])
        self.assertIsNotNone(candidates[0]["validation_macro_f1"])
        self.assertTrue(candidates[0]["converged"])
        self.assertFalse(candidates[1]["converged"])
        self.assertIsNone(candidates[1]["validation_macro_f1"])

    def test_final_fit_also_rejects_nonconvergence(self):
        self.cfg["logistic_regression"]["max_iter"] = 1
        with self.assertRaises(ConvergenceWarning):
            fit_lr(make_lr(1.0, self.cfg, 42), self.x_train, self.y_train)

    def test_empty_search_is_rejected(self):
        cfg = copy.deepcopy(self.cfg)
        cfg["randomized_search"]["n_iter"] = 0
        with self.assertRaisesRegex(ValueError, "n_iter must be positive"):
            sample_c_values(cfg, np.random.default_rng(42))


if __name__ == "__main__":
    unittest.main()
