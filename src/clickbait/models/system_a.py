from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline


def build_tfidf_union() -> FeatureUnion:
    word = TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 2),
        min_df=2,
        sublinear_tf=True,
    )
    char = TfidfVectorizer(
        analyzer="char",
        ngram_range=(3, 5),
        min_df=2,
        sublinear_tf=True,
    )
    return FeatureUnion([("word", word), ("char", char)])


def build_system_a_pipeline(vectorizer: FeatureUnion | None = None) -> Pipeline:
    vec = vectorizer if vectorizer is not None else build_tfidf_union()
    return Pipeline([("tfidf", vec)])
