import copy
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from clickbait.embeddings import (
    EMBEDDING_DIM,
    encoding_spec,
    load_embeddings,
    save_embeddings,
    validate_split_coverage,
)


class EmbeddingCacheTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.cfg = {
            "embedding_model": "fixture-model",
            "embeddings": {
                "revision": "fixture",
                "max_seq_length": 256,
                "normalize_embeddings": True,
                "batch_size": 32,
            },
        }
        self.posts = pd.DataFrame(
            {
                "post_id": ["9007199254740993", "002", "three"],
                "post_text": ["An ordinary headline", "WHY?!", "Café — what's next?"],
            }
        )
        self.vectors = np.arange(3 * EMBEDDING_DIM, dtype=np.float32).reshape(3, EMBEDDING_DIM)

    def save(self):
        save_embeddings(self.directory, self.posts, self.vectors, encoding_spec(self.cfg))

    def test_lookup_preserves_requested_order_and_subset(self):
        self.save()
        actual = load_embeddings(self.directory, self.posts.iloc[[2, 0]], self.cfg)
        np.testing.assert_array_equal(actual, self.vectors[[2, 0]])
        self.assertEqual(actual.dtype, np.float32)
        metadata = json.loads((self.directory / "meta.json").read_text())
        self.assertEqual(metadata["model_revision"], "fixture")
        self.assertEqual(metadata["n_rows"], 3)

    def test_changed_text_is_rejected(self):
        self.save()
        changed = self.posts.copy()
        changed.loc[0, "post_text"] = "A different headline"
        with self.assertRaisesRegex(ValueError, "Post text differs"):
            load_embeddings(self.directory, changed, self.cfg)

    def test_missing_id_is_rejected(self):
        self.save()
        changed = self.posts.copy()
        changed.loc[0, "post_id"] = "absent"
        with self.assertRaisesRegex(KeyError, "absent"):
            load_embeddings(self.directory, changed, self.cfg)

    def test_labels_do_not_affect_lookup(self):
        self.save()
        labelled = self.posts.assign(label=[1, 0, 1])
        np.testing.assert_array_equal(load_embeddings(self.directory, labelled, self.cfg), self.vectors)

    def test_changed_encoder_is_rejected(self):
        self.save()
        for field, value in [("revision", "different"), ("max_seq_length", 128), ("normalize_embeddings", False)]:
            with self.subTest(field=field):
                changed = copy.deepcopy(self.cfg)
                changed["embeddings"][field] = value
                with self.assertRaisesRegex(ValueError, "differs from configuration"):
                    load_embeddings(self.directory, self.posts, changed)
        changed = {**self.cfg, "embedding_model": "different-model"}
        with self.assertRaisesRegex(ValueError, "model_id"):
            load_embeddings(self.directory, self.posts, changed)

    def test_batch_size_does_not_invalidate_saved_vectors(self):
        self.save()
        changed = copy.deepcopy(self.cfg)
        changed["embeddings"]["batch_size"] = 1
        np.testing.assert_array_equal(load_embeddings(self.directory, self.posts, changed), self.vectors)

    def test_incompatible_metadata_is_rejected(self):
        self.save()
        path = self.directory / "meta.json"
        original = json.loads(path.read_text())
        for field, value in [("format_version", 99), ("n_rows", 10), ("dimension", 10), ("dtype", "float64")]:
            with self.subTest(field=field):
                path.write_text(json.dumps({**original, field: value}))
                with self.assertRaises(ValueError):
                    load_embeddings(self.directory, self.posts, self.cfg)

    def test_invalid_posts_are_rejected(self):
        for column, value in [("post_id", "002"), ("post_id", 123), ("post_text", " "), ("post_text", None)]:
            with self.subTest(column=column, value=value):
                changed = self.posts.copy()
                changed[column] = changed[column].astype(object)
                changed.loc[0, column] = value
                with self.assertRaises(ValueError):
                    save_embeddings(self.directory, changed, self.vectors, {})

    def test_invalid_vectors_are_rejected(self):
        invalid = [self.vectors[:, :10], self.vectors.astype(np.float64), self.vectors.copy()]
        invalid[-1][0, 0] = np.nan
        for vectors in invalid:
            with self.subTest(shape=vectors.shape, dtype=vectors.dtype):
                with self.assertRaises(ValueError):
                    save_embeddings(self.directory, self.posts, vectors, {})

    def test_incomplete_or_damaged_cache_is_rejected(self):
        self.save()
        archive = self.directory / "embeddings.npz"
        archive.write_bytes(archive.read_bytes()[:100])
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            load_embeddings(self.directory, self.posts, self.cfg)
        (self.directory / "meta.json").unlink()
        with self.assertRaises(FileNotFoundError):
            load_embeddings(self.directory, self.posts, self.cfg)

    def write_split(self, train_ids, val_ids, test_ids):
        payload = {
            "name": "fixture", "type": "temporal", "metadata": {},
            "train_ids": train_ids, "val_ids": val_ids, "test_ids": test_ids,
        }
        (self.directory / "fixture.json").write_text(json.dumps(payload))

    def test_split_coverage_allows_unused_posts(self):
        ids = self.posts["post_id"].tolist()
        self.write_split(ids[:1], ids[1:2], ids[2:])
        posts = pd.concat([self.posts, pd.DataFrame({"post_id": ["unused"], "post_text": ["Later post"]})])
        summary = validate_split_coverage(posts, self.directory)["fixture"]
        self.assertEqual([summary[part] for part in ("train", "val", "test")], [1, 1, 1])
        self.assertEqual(len(summary["manifest_sha256"]), 64)

    def test_split_missing_id_is_rejected(self):
        self.write_split(["absent"], ["002"], ["three"])
        with self.assertRaisesRegex(ValueError, "fixture: missing post IDs"):
            validate_split_coverage(self.posts, self.directory)

    def test_duplicate_or_overlapping_split_ids_are_rejected(self):
        for train, val in [(["002", "002"], ["9007199254740993"]), (["002"], ["002"])]:
            with self.subTest(train=train, val=val):
                self.write_split(train, val, ["three"])
                with self.assertRaisesRegex(ValueError, "duplicate or overlapping"):
                    validate_split_coverage(self.posts, self.directory)

    def test_empty_partition_is_rejected(self):
        self.write_split([], ["002"], ["three"])
        with self.assertRaisesRegex(ValueError, "empty partition"):
            validate_split_coverage(self.posts, self.directory)

    def test_absent_manifests_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "No split manifests"):
            validate_split_coverage(self.posts, self.directory)


if __name__ == "__main__":
    unittest.main()
