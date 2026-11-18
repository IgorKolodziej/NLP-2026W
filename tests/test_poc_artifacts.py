import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

from clickbait.poc_artifacts import export_artifacts


class PocArtifactTests(unittest.TestCase):
    def test_export_creates_readable_presentation_files(self):
        with tempfile.TemporaryDirectory() as directory:
            posts = pd.DataFrame({
                "post_id": [f"p{i}" for i in range(8)],
                "post_text": ["A short teaser", "YOU will love this!", "News report"] * 2 + ["What happens next?", "Ordinary item"],
                "label": [0, 1, 0, 0, 1, 0, 1, 0],
                "year_month": ["2017-04"] * 8,
            })
            predictions = pd.DataFrame({
                "post_id": posts.post_id,
                "y_true": posts.label,
                "y_pred_A": [0, 0, 0, 0, 1, 0, 1, 0],
                "p_clickbait_A": np.linspace(.1, .8, 8),
                "y_pred_B": [0, 1, 0, 1, 1, 0, 0, 0],
                "p_clickbait_B": np.linspace(.2, .9, 8),
                "y_pred_C": [0, 1, 0, 1, 1, 0, 1, 0],
                "p_clickbait_C": np.linspace(.25, .95, 8),
            })
            summary = {"systems": {s: {"test": {"macro_f1": score}} for s, score in zip("ABC", [.5, .6, .7])}, "delta_macro_f1_C_minus_B": .1}
            manifest = SimpleNamespace(test_ids=posts.post_id.tolist())
            output = export_artifacts(posts, manifest, summary, predictions, Path(directory))
            for key in ("results_table", "examples", "notes"):
                self.assertTrue((Path(directory) / output[key]).is_file())
            for figure in output["figures"].values():
                self.assertTrue((Path(directory) / figure["png"]).is_file())
                self.assertTrue((Path(directory) / figure["svg"]).is_file())
            table = pd.read_csv(Path(directory) / output["results_table"])
            self.assertEqual(table["system"].tolist(), ["A", "B", "C"])
            examples = pd.read_csv(Path(directory) / output["examples"])
            self.assertLessEqual(len(examples), 5)
            self.assertIn("one temporal window", (Path(directory) / output["notes"]).read_text())

    def test_reorders_predictions_by_id_and_rejects_wrong_id_sets(self):
        posts = pd.DataFrame({"post_id": ["p0", "p1"], "post_text": ["plain", "wow!"], "label": [0, 1], "year_month": ["2017-04", "2017-04"]})
        predictions = pd.DataFrame({"post_id": ["p1", "p0"], "y_true": [1, 0], **{f"y_pred_{s}": [1, 0] for s in "ABC"}, **{f"p_clickbait_{s}": [.9, .1] for s in "ABC"}})
        summary = {"systems": {s: {"test": {"macro_f1": .5, "average_precision": .5, "brier_score": .2}} for s in "ABC"}}
        with tempfile.TemporaryDirectory() as directory:
            output = export_artifacts(posts, SimpleNamespace(test_ids=["p0", "p1"]), summary, predictions, Path(directory))
            self.assertTrue((Path(directory) / output["figures"]["confusion_matrices"]["png"]).is_file())
        bad = predictions.copy()
        bad.loc[0, "post_id"] = "other"
        with self.assertRaises(ValueError):
            export_artifacts(posts, SimpleNamespace(test_ids=["p0", "p1"]), summary, bad, Path(tempfile.mkdtemp()))

    def test_rejects_label_mismatch(self):
        posts = pd.DataFrame({"post_id": ["p"], "post_text": ["x"], "label": [1], "year_month": ["2017-04"]})
        predictions = pd.DataFrame({"post_id": ["p"], "y_true": [0], **{f"y_pred_{s}": [0] for s in "ABC"}, **{f"p_clickbait_{s}": [.1] for s in "ABC"}})
        summary = {"systems": {s: {"test": {"macro_f1": .5}} for s in "ABC"}}
        with self.assertRaises(ValueError):
            export_artifacts(posts, SimpleNamespace(test_ids=["p"]), summary, predictions, Path(tempfile.mkdtemp()))


if __name__ == "__main__":
    unittest.main()
