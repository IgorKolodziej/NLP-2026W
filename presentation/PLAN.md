# Ten-minute mid-term presentation plan

The video follows one real teaser from the prediction task to the April result. The first presenter explains why the literature motivates a controlled test and how A, B and C work. The second presenter shows the data checks, the result and its limits, and the experiments needed next. The PoC has 1 minute 50 seconds over slides 9 and 10.

## Storyboard

| Slide | Time | Presenter | Visual and spoken emphasis |
|---|---|---|---|
| 1. Clickbait Without the Click | 00:00–00:15 | 1 | Introduce the English teaser and human clickbait label. |
| 2. Which cities? | 00:15–01:05 | 1 | Pause on the real Webis-17 teaser. State the controlled question and preview later-month stability and cue families. |
| 3. What prior work tells us | 01:05–01:55 | 1 | Use Potthast to motivate explicit cues and Zhou and Indurthi to motivate learned representations. Explain the official challenge's strength target and our binary target. |
| 4. What our experiment adds | 01:55–03:05 | 1 | Explain Michaluk's 3,072 vs 1,000 embedding dimensions and our matched B/C design. Use Søgaard to motivate the chronological comparison and explain the article-grouped diagnostic and overlap checks. |
| 5. The A/B/C pipeline | 03:05–04:15 | 1 | Follow the completed main-window pipeline from ID join to three separate logistic regressions. Trace one shared MiniLM representation into both B and C. |
| 6. What a cue measures | 04:15–05:00 | 1 | Highlight a question hook and direct address in a March teaser. Name the four cue families, then hand off. |
| 7. What entered the PoC | 05:00–06:00 | 2 | Explain the four cleaning counts, monthly prevalence, median teaser length, and exact overlaps checked. Point out the pending near-duplicate audit. |
| 8. Train, validate, test | 06:00–06:50 | 2 | Use the Dec–Feb, March and April timeline. Explain train-only transforms, March selection and the paired macro-F₁ comparison. |
| 9. April results | 06:50–07:55 | 2 | Show three April scores in one chart. Speak the paired gain, TF-IDF's ranking and earlier April exposure. Point to the saved and reproduced outputs. |
| 10. What changed on individual posts? | 07:55–08:40 | 2 | Return to slide 2's teaser. Pair one corrected error with one new false positive. Report the two counts over all paired April predictions. |
| 11. What will test H1–H4? | 08:40–09:30 | 2 | Map paired uncertainty, temporal runs and family ablations to H1–H3. Use a separate matched-input diagram for H4 and name calibration as planned analysis. |
| 12. Before the Phase 2 checkpoint | 09:30–10:00 | 2 | Show the audit and second-method priorities. State why Webis-16 transfer is pending and keep Jeff and YTClickbait21K optional. Close on the near-duplicate Q&A question. |

The three appendix slides cover the exact cue rules, April metrics and measured compute, and selected literature. End the video on slide 12.

## Evidence and scope

- **Completed PoC.** A/B/C use the same main-window rows from the public labelled Webis-17 release. A uses word and character TF-IDF, B uses frozen MiniLM, and C uses B's identical vectors plus twelve cues. Each fits balanced L2 logistic regression. Training data determine the fitted transforms and models. March validation chooses regularization from the same five candidates.
- **EDA and audit.** The exclusion ledger reconciles the 391 repeated normalized titles. The January–April positive rates are about 23%, with December at 26.4%. The length summary uses whitespace word counts over the cleaned corpus. Exact ID, teaser and title overlap checks cover the three main partitions. Article titles approximate article identity. Approximate matching and cross-corpus checks are pending.
- **April finding.** A scores 0.7479, B 0.7111 and C 0.7374 macro-F₁ on the 3,580 April test posts. C−B is +2.63 percentage points. Earlier April pilot results were known to the team. The current result is a one-window estimate with a paired interval pending. Example rows illustrate the full models' decisions.
- **Full study.** H1 adds the paired interval, H2 compares the three chronological windows and three article-grouped random diagnostics, and H3 removes one family at a time. H4 compares context models on the same complete-case rows and inputs. Both C_ctx and D_ctx have the twelve teaser cues. D_ctx adds the three proposal-defined relations. Calibration is interpreted alongside test prevalence.
- **Phase 2 planning.** Criterion 2.3 calls for baselines from at least two method classes. A compact fine-tuned encoder is a candidate for an additional comparator if adopted. It would use the same teaser-only split manifest, train on Dec–Feb, select settings on March, and use locked settings for April. The revised literature table and point-by-point responses to supervisor and Q&A feedback belong in the Phase 2 submission.
- **External and optional work.** Webis-16 is a compatibility-dependent evaluation-only diagnostic. Jeff is an optional decision-model comparison. YTClickbait21K is an optional title-only cross-platform evaluation.

The [revised proposal](../NLP_Proposal_v4-1.tex) specifies the scientific design. [PoC evidence](../results/poc/main/) and [cue definitions](../docs/cues.md) support the presentation. The [project rules](../Project%20rules%202026-27.docx) and [assessment criteria](../Assessment%20criteria%202026-27.docx) govern the course milestones.

## Rehearsal

Both presenters read [speaking_script.md](speaking_script.md) together using the rendered [deck](poc.html). Leave time after “Which cities?”, the April chart, and the paired examples. The 05:00 handoff and 10:00 finish are rehearsal targets. Check both microphones and the result chart at recording resolution, then stop at slide 12.
