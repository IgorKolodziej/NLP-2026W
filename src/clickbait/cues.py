from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from clickbait.config import repo_root

WORD_RE = re.compile(r"[a-z0-9']+", re.IGNORECASE)
CUE_NAMES = [
    "n_chars",
    "n_words",
    "avg_word_len",
    "unique_word_ratio",
    "n_exclamation",
    "n_question",
    "uppercase_char_ratio",
    "n_digits",
    "second_person_lexicon_hits",
    "first_person_plural_lexicon_hits",
    "forward_reference_hits",
    "all_caps_word_count",
]

CUE_GROUPS = {
    "length_structure": CUE_NAMES[0:4],
    "punctuation_caps": CUE_NAMES[4:8],
    "pronoun_forward_lexicon": CUE_NAMES[8:12],
}


@lru_cache(maxsize=1)
def _lexicon_paths() -> dict[str, Path]:
    root = repo_root() / "resources"
    return {
        "second_person": root / "second_person.txt",
        "first_person_plural": root / "first_person_plural.txt",
        "forward_reference": root / "forward_reference.txt",
    }


@lru_cache(maxsize=3)
def _load_terms(path: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    p = Path(path)
    words: list[str] = []
    phrases: list[str] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        term = line.strip().lower()
        if not term or term.startswith("#"):
            continue
        if " " in term:
            phrases.append(re.escape(term))
        else:
            words.append(re.escape(term))
    return tuple(words), tuple(phrases)


def _word_tokens(text: str) -> list[str]:
    return WORD_RE.findall(text.lower())


def _count_word_terms(text: str, words: tuple[str, ...]) -> int:
    if not words:
        return 0
    pattern = re.compile(r"\b(" + "|".join(words) + r")\b", re.IGNORECASE)
    return len(pattern.findall(text))


def _count_phrase_terms(text: str, phrases: tuple[str, ...]) -> int:
    if not phrases:
        return 0
    lowered = text.lower()
    total = 0
    for pat in phrases:
        total += len(re.findall(pat, lowered))
    return total


def _lexicon_hits(text: str, lexicon_key: str) -> int:
    paths = _lexicon_paths()
    words, phrases = _load_terms(str(paths[lexicon_key]))
    return _count_word_terms(text, words) + _count_phrase_terms(text, phrases)


def extract_cues(text: str) -> dict[str, float]:
    if text is None:
        text = ""
    tokens = _word_tokens(text)
    n_words = len(tokens)
    n_chars = len(text)
    unique_ratio = len(set(tokens)) / n_words if n_words else 0.0
    avg_word_len = (sum(len(t) for t in tokens) / n_words) if n_words else 0.0
    alpha = sum(c.isalpha() for c in text)
    upper = sum(c.isupper() for c in text)
    uppercase_char_ratio = upper / alpha if alpha else 0.0

    all_caps = 0
    for raw in text.split():
        stripped = re.sub(r"[^A-Za-z]", "", raw)
        if len(stripped) > 1 and stripped.isupper():
            all_caps += 1

    return {
        "n_chars": float(n_chars),
        "n_words": float(n_words),
        "avg_word_len": float(avg_word_len),
        "unique_word_ratio": float(unique_ratio),
        "n_exclamation": float(text.count("!")),
        "n_question": float(text.count("?")),
        "uppercase_char_ratio": float(uppercase_char_ratio),
        "n_digits": float(sum(c.isdigit() for c in text)),
        "second_person_lexicon_hits": float(_lexicon_hits(text, "second_person")),
        "first_person_plural_lexicon_hits": float(_lexicon_hits(text, "first_person_plural")),
        "forward_reference_hits": float(_lexicon_hits(text, "forward_reference")),
        "all_caps_word_count": float(all_caps),
    }


def extract_cues_frame(texts: pd.Series) -> pd.DataFrame:
    rows = [extract_cues(t) for t in texts.astype(str).tolist()]
    return pd.DataFrame(rows, columns=CUE_NAMES)


def cues_matrix(texts: pd.Series) -> np.ndarray:
    return extract_cues_frame(texts).to_numpy(dtype=np.float64)
