# Presentation review resolution

Review target: the approved storyboard, current reveal.js source/HTML, exact two-person script and pinned PoC artifacts. The earlier independent review is retained as a historical record in [independent_review.md](independent_review.md), its slide references describe an earlier draft.

## Narrative and scientific claims

| Review question | Current resolution |
|---|---|
| Is the problem understandable before the models? | Slides 1-2 define the teaser/label task, illustrate withheld information and explain ambiguity. |
| Does half the talk cover problem and SOTA? | Slides 1-6 occupy exactly 00:00-05:00. Feature, neural, hybrid/context and evaluation papers each have an explicit purpose. |
| Are papers explained beyond author lists? | Slides 3-5 describe input, mechanism and research question. Michaluk is the closest precedent, additional literature is retained in the preparation notes. |
| Is our intended difference clear? | Fixed embeddings, matched LR family/tuning budget, chronological versus grouped-random cue effects, family removals and a separate matched-input relation experiment. |
| Are novelty claims defensible? | The talk acknowledges existing linguistic cues, hybrid models and title-body comparison. It claims a proposed combination of controls and analysis, not ownership of those ideas. |
| Is the PoC proportionate? | One main slide, 07:10-08:10. Detailed costs, audits, examples and secondary metrics remain in the repository evidence. |
| Are findings interpreted correctly? | C−B is +0.0263 on April, while A remains strongest. One window, no paired interval and prior April exposure are disclosed beside the result. |
| Are planned and completed work distinct? | Slides 7-8 describe the study, slide 9 reports current evidence, slide 10 marks remaining experiments as future work. |
| Does the ending state a scientific aim? | Slide 11 returns to when cues help and whether their value persists, negative or unstable effects remain informative. |

## Content and rendering checks

- Eleven spoken slides, ending on the closing slide, with one manual cover and no generated duplicate.
- All eleven note speeches match the script verbatim: **1,179 words**, 599 for Presenter 1 and 580 for Presenter 2.
- Contiguous timing windows total **600 seconds**, handoff at **05:00**. Per-slide targets are approximately 109-125 words/minute.
- Displayed April macro-F1 values and C−B match `results/poc/main/summary.json`.
- Paper references in presenter notes link to the corresponding primary sources, the RoCliCo reference uses the verified Anthology paper ending in `640`.
- Every slide was visually inspected at **1600×900**. No horizontal clipping, missing images or content/footer collisions were detected. Embedded Inter loaded successfully.
- The HTML contains embedded CSS, font, runtime and the displayed result chart, with no external runtime dependencies.
- The warm-paper/dark-teal reference design, typography, and teal/orange accents are preserved. Small source footers and middle-dot separators are removed, sources remain in presenter notes.

## Remaining team actions and limits

An aloud rehearsal must establish actual duration and check both presenters' pronunciation, pacing, handoff and audio levels. The 600-second schedule is not a measured recording. No video has been recorded or submitted.

The scientific limits remain material: historical collection, subjective labels, topic/time confounding, imperfect article proxies, no publisher IDs, unfinished near-duplicate auditing, no external transfer result and no paired uncertainty yet. A/B/C share LR, the distinct decision-model-family plan for Phase 2 still needs confirmation. Current materials disclose these points and do not claim complete Phase 2 compliance.
