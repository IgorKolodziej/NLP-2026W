from pathlib import Path
import hashlib
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "presentation" / "assets"
SOURCE = ROOT / "results" / "poc" / "main"
PAPER, INK, TEAL, ORANGE, MUTED, RULE = "#faf9f5", "#142f38", "#007f78", "#b76831", "#63737a", "#d9dfdb"


def save(fig, name):
    for suffix in ("png", "svg"):
        fig.savefig(OUTPUT / f"{name}.{suffix}", dpi=200, bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)


def axes_style(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(RULE)
    ax.tick_params(colors=MUTED)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=RULE, linewidth=0.7)


def main():
    summary = json.loads((SOURCE / "summary.json").read_text())
    posts = pd.read_parquet(ROOT / "data" / "processed" / "posts.parquet")
    plt.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
        "font.size": 16, "text.color": INK, "axes.labelcolor": MUTED,
        "axes.facecolor": PAPER, "figure.facecolor": PAPER, "svg.fonttype": "none",
    })
    monthly = posts.groupby("year_month")["label"].agg(["count", "mean"])
    fig, ax = plt.subplots(figsize=(7.2, 4.5), layout="constrained")
    bars = ax.bar(["Dec", "Jan", "Feb", "Mar", "Apr"], monthly["mean"] * 100, color=TEAL, width=0.62)
    ax.set(ylim=(0, 35), ylabel="Clickbait (%)", xlabel="December 2016-April 2017")
    ax.set_title("All cleaned posts, n = 18,682", fontsize=17, loc="left", pad=16)
    for bar, count in zip(bars, monthly["count"], strict=True):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.8, f"n={count:,}", ha="center", fontsize=12, color=MUTED)
    axes_style(ax)
    save(fig, "monthly_prevalence")

    fig, ax = plt.subplots(figsize=(7.2, 4.7), layout="constrained")
    values = [summary["systems"][s]["test"]["macro_f1"] for s in "ABC"]
    bars = ax.bar(["A\nTF-IDF", "B\nMiniLM", "C\nMiniLM + cues"], values, color=[INK, TEAL, ORANGE], width=0.6)
    ax.set(ylim=(0, 1), ylabel="Macro-F1")
    ax.set_title("April test, n = 3,580, 23.2% positive", fontsize=16, loc="left", pad=18)
    for bar, value in zip(bars, values, strict=True):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.025, f"{value:.3f}", ha="center", fontsize=20, fontweight="bold")
    axes_style(ax)
    save(fig, "test_macro_f1")

    fig, ax = plt.subplots(figsize=(10.5, 2.8), layout="constrained")
    ax.axis("off")
    cells = [[s, *[f"{summary['systems'][s]['test'][m]:.3f}" for m in ("macro_f1", "average_precision", "brier_score")]] for s in "ABC"]
    table = ax.table(cellText=cells, colLabels=["System", "Macro-F1", "Average precision", "Brier"], cellLoc="center", loc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(16)
    table.scale(1, 1.9)
    for (row, column), cell in table.get_celld().items():
        cell.set_edgecolor(RULE)
        cell.set_linewidth(0.7)
        cell.set_facecolor("#eaf1e8" if row == 3 else PAPER)
        cell.get_text().set_color(MUTED if row == 0 else INK)
    table[(1, 1)].get_text().set_weight("bold")
    ax.set_title("April test, n = 3,580, 23.2% positive", fontsize=17, loc="left", pad=10)
    save(fig, "results_table")

    path = OUTPUT / "artifact_manifest.json"
    provenance = json.loads(path.read_text())
    for name in ("monthly_prevalence", "test_macro_f1", "results_table"):
        provenance["figures"][f"{name}.png"] = {
            "source": "results/poc/main/summary.json" if name != "monthly_prevalence" else "data/processed/posts.parquet",
            "rendered_by": "presentation/render_figures.py",
            "sha256": hashlib.sha256((OUTPUT / f"{name}.png").read_bytes()).hexdigest(),
            "style": "supplied CSS/QMD warm-paper palette",
        }
    provenance["style_reference"] = {"font": "Inter Seminar", "body_background": PAPER, "cover_background": "#102d36", "teal": TEAL, "orange": ORANGE}
    path.write_text(json.dumps(provenance, indent=2) + "\n")


if __name__ == "__main__":
    main()
