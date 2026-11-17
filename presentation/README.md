# Ten-minute mid-term presentation

Open [poc.html](poc.html) for the rendered reveal.js slides. Edit [poc.qmd](poc.qmd). Use [speaking_script.md](speaking_script.md) for exact speech and slide-change cues. The approved structure is documented in [PLAN.md](PLAN.md).

The video has **12 spoken slides**. Presenter 1 covers **00:00-05:00**, Presenter 2 covers **05:00-10:00**.

| Time | Content | Slides |
|---|---|---|
| 00:00-01:20 | Research problem and curiosity gap | 1-2 |
| 01:20-02:55 | Explicit features and neural models | 3-4 |
| 02:55-03:45 | Michaluk hybrid and our differences | 5 |
| 03:45-05:00 | Article context and evaluation evidence | 6-7 |
| 05:00-07:10 | Proposed study, data and evaluation | 8-9 |
| 07:10-08:10 | Current working PoC and preliminary findings | 10 |
| 08:10-10:00 | Remaining experiments, intended contribution and limits | 11-12 |

## Render and present

From the repository root:

```bash
quarto render presentation/poc.qmd
quarto preview presentation/poc.qmd
```

The HTML embeds reveal.js, CSS, the Inter font and figures, so it can be shared as one file and shown offline. External source links require internet only when opened. Arrow keys advance, `F` enters full screen. Use `S` for speaker view through Quarto preview when the browser permits it.

The visual style follows the supplied CSS/QMD reference: warm off-white slides, dark teal cover and closing, Inter and teal/orange accents. Citations and detailed evidence are in presenter notes. Slides have no small source footers. Recreate the existing chart assets with `uv run --locked python presentation/render_figures.py`, then render again.

## What the talk establishes

The first half explains clickbait ambiguity and the ideas behind Potthast, Biyani, Zhou, Indurthi, Michaluk and Wu. Slide 5 is dedicated to Michaluk and the differences in our study. Split-design and temporal-adaptation studies motivate our evaluation. Sources are linked in the corresponding presenter notes.

Our intended contribution is a controlled account of when twelve interpretable cues add information beyond fixed embeddings, whether the benefit persists over time, and which families contribute. A separate matched-input experiment will examine teaser-article relations. Individual linguistic patterns, hybrid prediction and title-body comparison already have precedents.

| Mid-term requirement | Evidence in the deck |
|---|---|
| Research problem | Slides 1-2: teaser input, human labels, curiosity gap and ambiguity |
| Revised SOTA | Slides 3-7: methods, motivation, differences and evaluation conditions |
| Proposed methodology / experimental plan | Slides 8-9 and 11: A/B/C, cues, splits and planned context study |
| Working PoC and preliminary findings | Slide 10: real-data outputs, scores and verified reproduction |
| Next steps and feedback | Slides 11-12: hypothesis-specific evidence, unfinished checks and Q&A focus |

The video is a preparation milestone, not a claim of complete Phase 2 compliance. All current A/B/C classifiers are LR. A feasible distinct decision-model family still needs confirmation for Criterion 2.3, optional Jeff is one candidate. Webis-16 has no transfer result because compatibility and overlap checks remain unfinished.

## Evidence provenance

All PoC numbers come from `results/poc/main/`. April macro-F₁ is **A 0.747911 / B 0.711133 / C 0.737411**, **C−B +0.026278**, on **3,580 posts, 830 positive**. The full cleaned corpus has **18,682 posts**. Exact main-split ID/normalized-teaser/title overlap checks are zero. The near-duplicate audit remains unfinished. `reproduction.json` records a fresh-environment refit with matching predictions and metrics.

April was excluded from fitting and selection, but its earlier pilot exposure means it is not a fresh blind test. One window and point estimates do not establish temporal robustness or significance.

The saved PoC artifacts record the measured **8.024 s** runner time and **718.6 MiB** process-wide peak RSS on Apple M3 Max with OMP/MKL thread limits 4. Timing includes reconciliation, fitting, scoring and figure export after imports, using cached embeddings. It excludes downloads and embedding generation. Timing varies by machine.

Additional model-disagreement examples are saved in `assets/selected_examples.csv`: one correction and one introduced false positive. Across April, C corrects **162** B errors and introduces **80**. These descriptive changes do not isolate individual-cue causality. `assets/artifact_manifest.json` records figure provenance and hashes.

To reproduce the PoC in a new output directory, follow the root README and run:

```bash
uv run --locked python scripts/run_poc.py --output results/poc/local
uv run --locked python scripts/run_poc.py --verify results/poc/local
```

## Rehearsal and submission

The exact script contains **1,217 spoken words** with contiguous **600-second** windows and a **05:00 handoff**. Rehearse aloud with both presenters, allowing for paper names, decimal scores, slide changes and pauses. The timings are targets. No recording duration has been measured. Stop after slide 12.

Record the screen and microphone audio, check legibility and both audio levels, then submit the video to the course Teams channel. No video has been recorded or uploaded. The 18 November video prepares the 25 November Q&A and 2 December Phase 2 submission. Contribution hours, the formal LLM declaration, data statement, MR and point-by-point rebuttal remain report/submission responsibilities.
