import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from clickbait.dataset import clean_dataset
from clickbait.poc_data import _ledger, audit_main, reconcile_raw
from clickbait.splits import SplitManifest


class PocDataTests(unittest.TestCase):
    def setUp(self):
        self.posts = pd.DataFrame(
            {
                "post_id": ["d", "j", "f", "m", "a"],
                "post_text": ["December report", "January report", "February report", "March report", "April report"],
                "label": [0, 1, 0, 1, 0],
                "target_title": ["D", "J", "F", "M", "A"],
                "year_month": ["2016-12", "2017-01", "2017-02", "2017-03", "2017-04"],
            }
        )
        self.manifest = SplitManifest("temporal_main", "temporal", ["d", "j", "f"], ["m"], ["a"], {})

    def test_audit_reports_counts_and_months(self):
        result = audit_main(self.posts, self.manifest, min_test_size=1)
        self.assertEqual(result["partitions"]["train"]["n"], 3)
        self.assertEqual(result["partitions"]["val"]["positive"], 1)
        self.assertEqual(result["months"]["test"], ["2017-04"])
        self.assertEqual(result["cross_partition_overlap"]["train_val"]["ids"], 0)

    def test_audit_rejects_duplicate_teaser_across_partitions(self):
        posts = self.posts.copy()
        posts.loc[posts.post_id == "a", "post_text"] = "December report"
        with self.assertRaisesRegex(ValueError, "overlap"):
            audit_main(posts, self.manifest, min_test_size=1)

    def test_audit_rejects_missing_or_nonbinary_labels(self):
        for value in (None, 2):
            posts = self.posts.copy()
            posts.loc[0, "label"] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "labels"):
                audit_main(posts, self.manifest, min_test_size=1)

    def test_ledger_matches_cleaning_stage_order_and_representatives(self):
        raw = pd.DataFrame(
            {
                "post_id": ["empty", "first", "same", "title_dup", "equal_time", "after_empty"],
                "post_text": ["", "One", " one ", "Two", "Three", "Four"],
                "post_timestamp": pd.to_datetime([
                    "2017-01-01", "2017-01-02", "2017-01-03", "2017-01-04", "2017-01-04", "2017-01-05",
                ], utc=True),
                "target_title": ["shared", "title-a", "title-b", "title-a", "title-c", "shared"],
                "label": [0, 0, 1, 1, 0, 1],
                "truth_class": ["no_clickbait", "no_clickbait", "clickbait", "clickbait", "no_clickbait", "clickbait"],
                "truth_judgments": [None] * 6,
            }
        )
        ledger = _ledger(raw)
        by_id = ledger.set_index("post_id")
        self.assertEqual(by_id.loc["same", "retained_post_id"], "first")
        self.assertEqual(by_id.loc["title_dup", "retained_post_id"], "first")
        self.assertEqual(by_id.loc["empty", "reason"], "empty_teaser")
        self.assertEqual(by_id.loc["equal_time", "reason"], "retained")
        self.assertEqual(by_id.loc["after_empty", "reason"], "retained")

        cleaned, stats = clean_dataset(raw)
        self.assertEqual(int((ledger.reason == "repeated_teaser").sum()), stats.teaser_duplicates_removed)
        self.assertEqual(int((ledger.reason == "repeated_article_title").sum()), stats.article_duplicates_removed)
        self.assertEqual(set(ledger.loc[ledger.reason == "retained", "post_id"]), set(cleaned.post_id))

    def test_reconcile_writes_id_only_ledger(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw_dir = root / "raw"
            raw_dir.mkdir()
            instances = [
                {"id": "1", "postText": [""], "postTimestamp": "2016-12-01T00:00:00Z", "targetTitle": "empty"},
                {"id": "2", "postText": ["Same"], "postTimestamp": "2016-12-02T00:00:00Z", "targetTitle": "one"},
                {"id": "3", "postText": [" same "], "postTimestamp": "2016-12-03T00:00:00Z", "targetTitle": "two"},
                {"id": "4", "postText": ["Other"], "postTimestamp": "2016-12-04T00:00:00Z", "targetTitle": "one"},
            ]
            truths = [
                {"id": "1", "truthClass": "no_clickbait"}, {"id": "2", "truthClass": "clickbait"},
                {"id": "3", "truthClass": "clickbait"}, {"id": "4", "truthClass": "no_clickbait"},
            ]
            (raw_dir / "instances.jsonl").write_text("\n".join(json.dumps(row) for row in instances) + "\n")
            (raw_dir / "truth.jsonl").write_text("\n".join(json.dumps(row) for row in truths) + "\n")
            from unittest.mock import patch
            with patch("clickbait.poc_data.load_config", return_value={"webis17": {"instances": "raw/instances.jsonl", "truth": "raw/truth.jsonl"}}):
                raw = __import__("clickbait.dataset", fromlist=["build_raw_frame"]).build_raw_frame(raw_dir / "instances.jsonl", raw_dir / "truth.jsonl")
                cleaned, _ = clean_dataset(raw)
                result = reconcile_raw(root, cleaned, root / "audit")
            self.assertEqual(result["cleaning"]["empty_teasers"], 1)
            self.assertEqual(result["cleaning"]["repeated_teasers"], 1)
            self.assertEqual(result["cleaning"]["repeated_article_titles"], 1)
            ledger = pd.read_csv(root / "audit" / "exclusion_ledger.csv")
            self.assertNotIn("post_text", ledger.columns)
            self.assertEqual(set(ledger.loc[ledger.reason != "retained", "post_id"].astype(str)), {"1", "3", "4"})


if __name__ == "__main__":
    unittest.main()
