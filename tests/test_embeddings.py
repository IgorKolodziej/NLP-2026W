import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from clickbait.embeddings import EMBEDDING_DIM, load_embeddings, save_embeddings


class EmbeddingCacheTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.posts = pd.DataFrame(
            {
                "post_id": ["9007199254740993", "002", "three"],
                "post_text": ["An ordinary headline", "WHY?!", "Café — what's next?"],
            }
        )
        self.vectors = np.arange(3 * EMBEDDING_DIM, dtype=np.float32).reshape(3, EMBEDDING_DIM)

    def save(self):
        save_embeddings(self.directory, self.posts, self.vectors, {"model_revision": "fixture"})

    def test_lookup_preserves_requested_order_and_subset(self):
        self.save()
        actual = load_embeddings(self.directory, self.posts.iloc[[2, 0]])
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
            load_embeddings(self.directory, changed)

    def test_missing_id_is_rejected(self):
        self.save()
        changed = self.posts.copy()
        changed.loc[0, "post_id"] = "absent"
        with self.assertRaisesRegex(KeyError, "absent"):
            load_embeddings(self.directory, changed)

    def test_labels_do_not_affect_lookup(self):
        self.save()
        labelled = self.posts.assign(label=[1, 0, 1])
        np.testing.assert_array_equal(load_embeddings(self.directory, labelled), self.vectors)

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
            load_embeddings(self.directory, self.posts)
        (self.directory / "meta.json").unlink()
        with self.assertRaises(FileNotFoundError):
            load_embeddings(self.directory, self.posts)


if __name__ == "__main__":
    unittest.main()
