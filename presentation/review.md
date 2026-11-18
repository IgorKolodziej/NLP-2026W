# Presentation review

## Revised recording deck

- The [storyboard](PLAN.md) places the controlled comparison before the presenter handoff and gives the April result and paired examples 1 minute 50 seconds. Twelve spoken slides total 600 seconds. The three appendix slides are for Q&A.
- The [speaking script](speaking_script.md) and rendered presenter notes contain the same 1,111 spoken words. The handoff is at 05:00. The team still needs a joint rehearsal.
- The [rendered deck](poc.html) was checked offline at 1600×900 and 1280×720 for clipping, embedded resources and slide order.
- Cleaning counts, median lengths, exact split overlap, macro-F₁ and paired error changes were checked against the saved data and predictions. Both April examples fire the opening-pointer cue. The March example fires the question hook and has one direct-address match among seven tokens.
- The recording deck keeps the earlier-April-exposure disclosure and treats the second Phase 2 method class as open. The completed PoC, planned study and optional extensions have distinct status labels.

## Factual audit of the previous deck · 17 November 2026

The revised speech agrees with the proposal's scientific design and the saved main-window experiment. Numerical claims passed model-reload verification. Planned robustness, uncertainty, family and context experiments are explicitly described as unfinished.

| Claim | Evidence checked | Finding |
|---|---|---|
| English teaser classification using released human labels | Proposal research questions and dataset section, [dataset loader](../src/clickbait/dataset.py) | Matches. No click-count or factual-verification claim. |
| Cleaned corpus: 18,682 posts, about 24% clickbait | [Summary](../results/poc/main/summary.json), [exclusion ledger](../results/poc/main/exclusion_ledger.csv), processed IDs/labels | Matches: 4,448 positives, 23.809%. Cleaning excludes 54 empty teasers, 411 repeated teasers and 391 repeated article titles. Retained IDs match processed data. |
| Train December-February, validate March, test April | [Protocol](../results/poc/main/protocol.json) and split manifest | Matches: 11,184 / 3,918 / 3,580 posts. April has 830 positives. |
| A uses word/character TF-IDF, B uses fixed MiniLM, C appends twelve cues to B | Proposal model section, [A](../src/clickbait/models/system_a.py), [B/C](../src/clickbait/models/neural.py), [cue definitions](../docs/cues.md) | Matches. C retains the same embedding coordinates. Four groups contain three cues each. |
| Shared classifier family and tuning budget, train-only transforms | Protocol, [tuning](../src/clickbait/tuning.py), model code | Matches. Balanced LR, five C values, March selection and train-only final fit. Only cue columns are scaled for C. |
| April macro-F1 A 0.7479, B 0.7111, C 0.7374, C-B +0.0263 | Saved models, predictions and summary, recomputed by the verifier | Matches. The unrounded difference is 0.0262776967, or 2.6278 percentage points. A is strongest in this run. |
| Reload and fresh-environment reproduction | Current reload verification and [recorded independent refit](../results/poc/main/reproduction.json) | Reload passed during this audit. The earlier fresh-environment refit record matches the summary hash. A new full training run was not required or performed for this audit. |
| Three chronological tests, three grouped-random diagnostics, paired bootstrap and cue-family removals | Proposal H1-H3 and evaluation section | Correct as planned work. The presented twelve-cue PoC covers one main window, not the full robustness study. |
| Additional relation cues beyond a context-aware baseline already containing the twelve teaser cues | Proposal H4 and matched-context section | Correct as planned work. All context comparators share rows, teaser, title and a 96-word article lead. |
| No external transfer or current-deployment/source-transfer claim | Proposal limitations and current results | Correct. Webis-16 checks and near-duplicate/cross-corpus auditing remain unfinished. No publisher IDs are available. |

The verification command was:

```bash
uv run --locked python scripts/run_poc.py --verify results/poc/main
```

It checks saved input/model hashes, software versions, test IDs and labels, reloaded predictions/probabilities, every saved test metric and C-B. It passed with C-B = 0.02627769674856828.

## Proposal wording that no longer describes the current status

- The proposal calls April untouched. Earlier pilot exposure means it is not a fresh blind test. The speech explicitly says April was excluded from fitting/selection but had already been seen in pilot results.
- The proposal leaves the 391-row discrepancy unresolved. The current ledger now reconciles those exclusions as repeated normalized article titles. The speech uses the verified cleaned count.
- The protocol snapshot contains a legacy 70/15/15 random-split configuration. The revised proposal calls for random diagnostics matching the main chronological proportions. The current PoC does not execute or report these diagnostics. Their implementation must follow the revised plan before they can support a claim.

## SOTA and the dedicated Michaluk slide

The paper summaries follow the proposal. The dedicated Michaluk slide also checks the [primary paper, Table 4](https://arxiv.org/html/2602.18171v1): the reported embedding-only/hybrid comparison changes embedding width. Our B/C design keeps the vectors unchanged. The slide acknowledges the existing hybrid and feature-block comparison, and states our planned temporal, uncertainty and cue-group tests. It does not rank unlike published scores against our April macro-F1.

The Röttger-Pierrehumbert summary specifically concerns extra pretraining, avoiding a broader claim that all forms of time-specific model adaptation are ineffective.

## Wording changes

- Explained an embedding as a vector of numbers representing text.
- Replaced withheld referent, incremental value, paired uncertainty and calibration alongside prevalence with direct descriptions where the technical term was unnecessary.
- Explained grouped random splits as keeping posts linked to the same article together.
- Used future tense for comparisons and cue-group removals that have not been completed.
- Defined the purpose of the relation experiment and kept the matching-input condition explicit.
- Preserved the one-window, missing-interval and earlier-April-exposure qualifications.

## Timing and rendering of the previous deck

The deck has **12 slides**, with Michaluk on slide 5 at **02:55-03:45** and Wu on slide 6 at **03:45-04:10**. Problem/SOTA occupies **00:00-05:00**, the handoff is **05:00**, and the PoC remains **07:10-08:10**.

All twelve speeches match the notes: **1,217 words**, 595 for Presenter 1 and 622 for Presenter 2. The schedule totals **600 seconds**. Actual duration requires an aloud rehearsal.

The rendered slides were checked at 1600x900. No horizontal clipping or missing figures were detected. The warm-paper/dark-teal style is retained. There are no backup slides, small source footers, middle-dot separators, long dashes or semicolons in visible slide content. Sources remain in presenter notes. The HTML embeds its runtime, styling, font and result chart.

No video has been recorded or submitted. All current classifiers use LR, so a distinct classifier-family plan for Phase 2 still needs confirmation. Optional Jeff and YouTube experiments do not determine completion of the core scientific study.
