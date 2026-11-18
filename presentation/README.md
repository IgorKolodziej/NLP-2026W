# Ten-minute mid-term presentation

Open [poc.html](poc.html) to present. Use [speaking_script.md](speaking_script.md) for the exact speech and cues. Edit [poc.qmd](poc.qmd) and [styles.css](styles.css) before rendering again. The full storyboard is in [PLAN.md](PLAN.md).

| Time | Presenter | Content | Slides |
|---|---|---|---|
| 00:00–01:05 | 1 | Task, teaser and research questions | 1–2 |
| 01:05–03:05 | 1 | Prior work and the contribution | 3–4 |
| 03:05–05:00 | 1 | Completed A/B/C pipeline and cue example | 5–6 |
| 05:00–06:50 | 2 | Data, overlap checks, split and measures | 7–8 |
| 06:50–08:40 | 2 | April result and paired prediction examples | 9–10 |
| 08:40–10:00 | 2 | Planned experiments, Phase 2 checkpoint and Q&A | 11–12 |

The three appendix slides are for Q&A. They give the twelve cue rules, secondary April metrics and measured compute, and selected literature comparisons. The video prepares the 25 November Q&A and the 2 December Phase 2 submission.

## Render and present

From the repository root:

```bash
quarto render presentation/poc.qmd
quarto preview presentation/poc.qmd
```

The HTML embeds reveal.js, CSS, the Inter font and the prevalence figure for offline playback. External source links need internet access. Arrow keys advance. Press `F` for full screen or `S` for speaker view through Quarto preview. Stop after slide 12 when recording.

## Evidence

The [PoC summary](../results/poc/main/summary.json) reports April 2017 test macro-F₁ of **0.747911** for A, **0.711133** for B and **0.737411** for C. Paired C−B is **+0.026278** on 3,580 posts, of which 830 are clickbait. The result chart shows the four-decimal scores and reports the difference from the unrounded values. The [refit record](../results/poc/main/reproduction.json) documents matching predictions and metrics in a separate locked environment.

The [exclusion ledger](../results/poc/main/exclusion_ledger.csv) records 54 empty teasers, 411 repeated teasers and 391 repeated normalized titles. The resulting 18,682-row pilot has 4,448 positive labels. Median lengths of 10 words for clickbait and 12 for the other class use whitespace word counts over all cleaned posts. Exact main-split ID, normalized-teaser and title overlap checks are zero. Near-duplicate and cross-corpus checks remain pending.

The [April examples](assets/selected_examples.csv) illustrate a correction and an introduced false positive. Across the April test, C corrects 162 errors made by B and introduces 80. Both examples activate the initial-pointer cue. The March cue demonstration uses Webis-17 post `837668396816728064` and illustrates two implemented rules. [Cue definitions](../docs/cues.md)

April was held out from fitting and regularization selection in this run. The team had previously seen April pilot scores. The current estimate covers one temporal window and the paired interval is pending.

The compute appendix uses the measured 8.024 s runner, 0.582 s April inference and 718.6 MiB process-wide peak RSS on an Apple M3 Max with thread limits 4. These figures use cached embeddings and exclude download and embedding-generation time. The runner measurement covers reconciliation, fitting, scoring and export after imports.

For a new result, follow the [root README](../README.md) for raw data and cache setup, then run:

```bash
uv run --locked python scripts/run_poc.py --output results/poc/local
uv run --locked python scripts/run_poc.py --verify results/poc/local
```

## Rehearsal and recording

The script has **1,111 spoken words** and the windows sum to **600 seconds**, with a **05:00 handoff**. Rehearse aloud with both presenters and time the pauses. Check full-screen legibility and both audio levels. The recorded video is submitted to the course Teams channel.

For the Phase 2 experiment plan, a compact fine-tuned encoder is a candidate for the second method class. Webis-16 awaits schema, label and overlap checks. Jeff and YTClickbait21K remain optional.
