from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache

import numpy as np
import pandas as pd

from clickbait.config import repo_root

CUE_SPECIFICATION = "mechanism_cues"
WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)*|[0-9]+")
CUE_NAMES = [
    "initial_unresolved_pointer", "indefinite_referent_density", "delayed_revelation_frame",
    "direct_address_density", "action_invitation", "question_hook",
    "surprise_word_density", "epistemic_distance_density", "narrative_reversal",
    "numbered_payoff_promise", "attention_punctuation", "referent_anchor_imbalance",
]
CUE_GROUPS = {
    "referential_withholding": CUE_NAMES[:3],
    "audience_involvement": CUE_NAMES[3:6],
    "affective_narrative_framing": CUE_NAMES[6:9],
    "specificity_presentation": CUE_NAMES[9:12],
}


@lru_cache(maxsize=1)
def lexicons() -> dict[str, list[str]]:
    return json.loads((repo_root() / "resources" / "linguistic_cues.json").read_text(encoding="utf-8"))


def normalize_cue_text(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).translate(
        str.maketrans({"’": "'", "‘": "'", "ʼ": "'", "`": "'"}),
    ).split())


def phrase_present(text: str, phrases: list[str]) -> bool:
    return any(re.search(r"\b" + r"\s+".join(map(re.escape, phrase.split())) + r"\b", text)
               for phrase in phrases)


def extract_cues(text: str | None) -> dict[str, float]:
    text = normalize_cue_text(text or "")
    if not text:
        return dict.fromkeys(CUE_NAMES, 0.0)
    original_tokens = WORD_RE.findall(text)
    tokens = [token.lower() for token in original_tokens]
    n = max(1, len(tokens))
    terms = lexicons()
    first = tokens[0] if tokens else ""

    def rate(key: str) -> float:
        return sum(token in terms[key] for token in tokens) / n

    numbered = any(
        token.isdigit() and 1 <= int(token) <= 99
        and any(word in terms["payoff"] for word in tokens[i + 1:i + 5])
        for i, token in enumerate(tokens[:2])
    )
    referents = sum(token in terms["referent"] for token in tokens)
    anchors = sum(token[0].isupper() and not token.isupper() for token in original_tokens[1:])
    values = [
        first in terms["initial_pointer"], rate("indefinite_referent"),
        phrase_present(text.lower(), terms["delayed_revelation"]),
        rate("direct_address"),
        first in terms["action_invitation"] or tokens[:2] == ["find", "out"],
        first in terms["question_start"] and "?" in text,
        rate("surprise"), rate("epistemic_distance"),
        phrase_present(text.lower(), terms["narrative_reversal"]),
        numbered, min(1.0, (text.count("!") + text.count("?") + text.count("...")) / max(1, len(text))),
        referents / (referents + anchors + 1),
    ]
    return dict(zip(CUE_NAMES, map(float, values), strict=True))


def extract_cues_frame(texts: pd.Series) -> pd.DataFrame:
    return pd.DataFrame([extract_cues(text) for text in texts.astype(object).fillna("")], columns=CUE_NAMES)


def cues_matrix(texts: pd.Series) -> np.ndarray:
    return extract_cues_frame(texts).to_numpy(dtype=np.float64)
