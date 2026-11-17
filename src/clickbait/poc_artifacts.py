"""Presentation-ready artefacts for the one-window PoC."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix


SYSTEMS = ("A", "B", "C")
plt.rcParams.update({"font.size": 11, "axes.titlesize": 14, "axes.labelsize": 11})


def _partition(posts: pd.DataFrame, manifest: Any) -> pd.DataFrame:
    ids = list(manifest.test_ids)
    if "post_id" not in posts or not posts["post_id"].is_unique:
        raise ValueError("posts must have unique post_id values")
    missing = sorted(set(ids) - set(posts["post_id"]))
    if missing:
        raise ValueError(f"manifest test IDs missing from posts: {missing[:3]}")
    return posts.set_index("post_id").loc[ids].reset_index()


def _save(fig: plt.Figure, output_dir: Path, name: str) -> dict[str, str]:
    png = output_dir / f"{name}.png"
    svg = output_dir / f"{name}.svg"
    fig.savefig(png, dpi=180, bbox_inches="tight")
    fig.savefig(svg, bbox_inches="tight")
    plt.close(fig)
    return {"png": str(png), "svg": str(svg)}


def _monthly_chart(posts: pd.DataFrame, output_dir: Path) -> dict[str, str]:
    frame = posts.copy()
    if "year_month" not in frame:
        if "post_timestamp" not in frame:
            raise ValueError("posts need year_month or post_timestamp for monthly chart")
        frame["year_month"] = pd.to_datetime(frame["post_timestamp"]).dt.strftime("%Y-%m")
    stats = frame.groupby("year_month", sort=True)["label"].agg(["count", "mean"])
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    bars = ax.bar(stats.index.astype(str), stats["mean"] * 100, color="#386cb0")
    ax.set_ylabel("Clickbait prevalence (%)")
    ax.set_xlabel("Calendar month")
    ax.set_title(f"Webis-17: monthly labels (all cleaned posts, n={len(frame):,})")
    ax.set_ylim(0, max(35, float((stats["mean"] * 100).max() * 1.25)))
    for bar, n in zip(bars, stats["count"], strict=True):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.4, f"n={n:,}", ha="center", fontsize=8)
    fig.tight_layout()
    return _save(fig, output_dir, "monthly_prevalence")


def _length_chart(posts: pd.DataFrame, output_dir: Path) -> dict[str, str]:
    frame = posts.copy()
    frame["word_count"] = frame["post_text"].fillna("").astype(str).str.split().str.len()
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for label, color, name in [(0, "#999999", "Non-clickbait"), (1, "#e66101", "Clickbait")]:
        values = frame.loc[frame["label"] == label, "word_count"]
        ax.hist(values, bins=25, alpha=0.65, color=color, label=f"{name} (n={len(values):,})")
    ax.set_xlabel("Words in teaser")
    ax.set_ylabel("Posts")
    ax.set_title(f"Teaser length by label (all cleaned posts, whitespace word count; n={len(frame):,})")
    ax.legend()
    fig.tight_layout()
    return _save(fig, output_dir, "teaser_length")


def _metric_chart(summary: dict[str, Any], output_dir: Path, n_test: int, prevalence: float) -> dict[str, str]:
    scores = [float(summary["systems"][s]["test"]["macro_f1"]) for s in SYSTEMS]
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    bars = ax.bar(SYSTEMS, scores, color=["#7570b3", "#1b9e77", "#d95f02"])
    ax.set_ylim(0, 1)
    ax.set_ylabel("Macro-F₁")
    ax.set_xlabel("System")
    ax.set_title(f"temporal_main/test macro-F₁ (n={n_test:,}, positive={prevalence:.1%})")
    for bar, score in zip(bars, scores, strict=True):
        ax.text(bar.get_x() + bar.get_width() / 2, score + 0.02, f"{score:.3f}", ha="center", fontweight="bold")
    fig.tight_layout()
    return _save(fig, output_dir, "test_macro_f1")


def _confusion_charts(test: pd.DataFrame, predictions: pd.DataFrame, output_dir: Path) -> dict[str, str]:
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.5))
    for ax, system in zip(axes, SYSTEMS, strict=True):
        cm = confusion_matrix(test["label"], predictions[f"y_pred_{system}"], labels=[0, 1])
        image = ax.imshow(cm, cmap="Blues", vmin=0)
        ax.set_title(f"System {system}")
        ax.set_xticks([0, 1], ["Pred 0", "Pred 1"])
        ax.set_yticks([0, 1], ["Gold 0", "Gold 1"])
        for i in range(2):
            for j in range(2):
                threshold = image.norm(cm[i, j])
                ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                        color="white" if threshold > 0.55 else "black", fontsize=12, fontweight="bold")
    fig.suptitle("Confusion matrices — temporal_main/test", y=1.02)
    fig.tight_layout()
    return _save(fig, output_dir, "confusion_matrices")


def _results_table_chart(rows: list[dict[str, Any]], output_dir: Path) -> dict[str, str]:
    fig, ax = plt.subplots(figsize=(9.6, 2.2))
    ax.axis("off")
    table_rows = [[row["system"], f"{row['macro_f1']:.3f}", f"{row.get('average_precision', float('nan')):.3f}", f"{row.get('brier_score', float('nan')):.3f}"] for row in rows]
    table = ax.table(cellText=table_rows, colLabels=["System", "Macro-F₁", "Average precision", "Brier"], loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 1.65)
    ax.set_title(
        f"temporal_main/test (n={rows[0]['n_test']:,}, positive={rows[0]['positive_rate']:.1%})", pad=10,
    )
    fig.tight_layout()
    return _save(fig, output_dir, "results_table")


def _examples(test: pd.DataFrame, predictions: pd.DataFrame, output_dir: Path) -> Path:
    merged = test[["post_id", "post_text", "label"]].merge(predictions, on="post_id", how="inner", validate="one_to_one")
    wrong = merged[[f"y_pred_{s}" for s in SYSTEMS]].ne(merged["label"].to_numpy()[:, None]).any(axis=1)
    disagreement = merged[[f"y_pred_{s}" for s in SYSTEMS]].nunique(axis=1).gt(1)
    chosen = merged.loc[disagreement | wrong].copy()
    chosen["priority"] = disagreement.loc[chosen.index].astype(int) * 2 + wrong.loc[chosen.index].astype(int)
    chosen = chosen.sort_values(["priority", "post_id"], ascending=[False, True]).head(5)
    cols = ["post_id", "post_text", "label"] + [f"y_pred_{s}" for s in SYSTEMS] + [f"p_clickbait_{s}" for s in SYSTEMS]
    path = output_dir / "example_predictions.csv"
    chosen[cols].to_csv(path, index=False)
    return path


def export_artifacts(
    posts: pd.DataFrame,
    manifest: Any,
    summary: dict[str, Any],
    predictions: pd.DataFrame,
    output_dir: Path,
) -> dict[str, Any]:
    """Export charts, tables, examples, and notes for the presentation PoC."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    test = _partition(posts, manifest)
    required = {"post_id", "y_true", *(f"y_pred_{s}" for s in SYSTEMS), *(f"p_clickbait_{s}" for s in SYSTEMS)}
    missing = required - set(predictions.columns)
    if missing:
        raise ValueError(f"predictions missing columns: {sorted(missing)}")
    predictions = predictions.copy()
    if predictions["post_id"].duplicated().any() or set(predictions["post_id"]) != set(test["post_id"]):
        raise ValueError("predictions must contain each manifest test ID exactly once")
    predictions = predictions.set_index("post_id").loc[test["post_id"]].reset_index()
    if not np.array_equal(test["label"].to_numpy(), predictions["y_true"].to_numpy()):
        raise ValueError("prediction labels do not match posts")
    n_test = len(test)
    prevalence = float(test["label"].mean()) if n_test else 0.0
    rows = []
    for system in SYSTEMS:
        metrics = summary["systems"][system]["test"]
        rows.append({"system": system, "split": "temporal_main/test", "n_test": n_test, "positive_rate": prevalence, **metrics})
    figures = {
        "monthly_prevalence": _monthly_chart(posts, output_dir),
        "teaser_length": _length_chart(posts, output_dir),
        "test_macro_f1": _metric_chart(summary, output_dir, n_test, prevalence),
        "confusion_matrices": _confusion_charts(test, predictions, output_dir),
    }
    table_path = output_dir / "results_table.csv"
    pd.DataFrame(rows).to_csv(table_path, index=False)
    figures["results_table"] = _results_table_chart(rows, output_dir)
    examples_path = _examples(test, predictions, output_dir)
    notes_path = output_dir / "presentation_notes.txt"
    delta = float(summary.get("delta_macro_f1_C_minus_B", rows[2]["macro_f1"] - rows[1]["macro_f1"]))
    notes_path.write_text(
        "PoC presentation notes\n\n"
        "Question: do twelve interpretable teaser cues improve a frozen MiniLM + logistic-regression baseline under a future-month split?\n"
        "Data/protocol: Webis-17 postText; train Dec 2016–Feb 2017, validate Mar 2017, test Apr 2017; class-weighted LR; test labels are not used for tuning.\n"
        "Systems: A word/character TF–IDF + LR; B frozen all-MiniLM-L6-v2 embeddings + LR; C B plus twelve cues + LR.\n"
        f"Observed PoC: A={rows[0]['macro_f1']:.4f}, B={rows[1]['macro_f1']:.4f}, C={rows[2]['macro_f1']:.4f}; C−B={delta:+.4f} macro-F1 on temporal_main/test (n={n_test:,}, positive={prevalence:.1%}).\n"
        "Interpretation: this is one temporal window and a pilot result; it does not establish robustness across months, causality, or publisher generalization. Article titles are only an article-identity proxy, and the broader near-duplicate audit is unfinished. The main test partition had an earlier pilot score, so the result must be presented with that prior exposure disclosed.\n"
        "Next: repeat the other temporal windows and grouped-random diagnostics, run four cue-family ablations, quantify uncertainty and complete the matched teaser–article context experiment.\n",
        encoding="utf-8",
    )
    relative_figures = {
        name: {kind: str(Path(path).relative_to(output_dir)) for kind, path in files.items()}
        for name, files in figures.items()
    }
    metadata = {
        "split": "temporal_main", "partition": "test", "n_test": n_test,
        "positive_rate": prevalence, "figures": relative_figures,
        "results_table": str(table_path.relative_to(output_dir)), "examples": str(examples_path.relative_to(output_dir)), "notes": str(notes_path.relative_to(output_dir)),
    }
    (output_dir / "artifact_manifest.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata
