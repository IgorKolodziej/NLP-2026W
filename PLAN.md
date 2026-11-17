# Implementation plan — Clickbait Without the Click

**Proposal baseline:** [v4.1](NLP_Proposal_v4-1.tex), revised 14 November 2026. **Status:** presentation PoC implemented on `feat/poc`; the remaining full-project work is scoped separately below.

The ten tasks below are implementation work packages, distinct from course Phases 1–3. Retain Python 3.11+, `uv`, `pyproject.toml`, `uv.lock`, the existing `src/clickbait/` package and straightforward scripts. CPU suffices for core linear models; GPU is optional for encoding and decision-model experiments.

## Authority and changes from v2

[NLP_Proposal_v4-1.tex](NLP_Proposal_v4-1.tex) is the scientific specification; [nlp_proposal_v2.tex](nlp_proposal_v2.tex) describes the historical implementation. The [change log](../NLP_Proposal_Change_Log_v4-1.tex) explains the revision. [AGENTS.md](AGENTS.md) still points to v2 and contains superseded scientific instructions; align it in Task 1 after plan approval. Course requirements and repository conventions continue to apply.

| Area | Existing v2 implementation | Required v4.1 change |
|------|----------------------------|----------------------|
| Research | Main temporal C−B comparison | H1 controlled April gain; H2 three-window robustness; H3 family mechanisms; secondary H4 context relation gain |
| Teaser cues | Twelve cues in three groups of four | Replace with Appendix A's twelve cues in four groups of three; retrain C and redo ablations |
| LR selection | 25 sampled log-uniform candidates | Same prespecified fixed regularization grid and validation budget for A/B/C |
| Data audit | Aggregate counts; exact teaser/title deduplication | Row-level exclusion ledger, 391-row reconciliation, exact/near-duplicate and cross-corpus audit |
| Random splits | Article-grouped 70/15/15; group label uses maximum | Main-temporal proportions where possible; majority group label and deterministic ties |
| Chronology | Three windows already exist | Test-month eligibility N ≥ 1,000; explicit boundary exclusions and versioned final manifests |
| Context | Excluded from all prediction | Required secondary matched-row A_ctx/B_ctx/C_ctx/D_ctx experiment; primary A/B/C stay teaser-only |
| External data | Webis-16 collection/stub planned | Public access/licence established in proposal; verify local readiness and evaluate if compatible |
| Extensions | None | Optional title-only YTClickbait21K and Jeff zero-shot/few-shot/window-specific LoRA |
| Analysis | Scores, calibration, bootstrap and errors planned | Per-month cue/prevalence shifts, four family ablations and matched-context effects |

## Change-log coverage

All sixteen entries in the change log map to planned work below. This is requirement coverage, not a claim that implementation or report updates are complete. Entries 12–14 and 16 concern literature/reporting as well as code and are explicit delivery requirements in Task 10.

| Change-log item | Plan coverage |
|-----------------|---------------|
| 1. Four hypotheses | Scientific contract; Tasks 8–9 |
| 2. Operational twelve-cue specification | Task 4; four-family ablations in Task 9 |
| 3. Controlled teaser–article experiment | Required context suite in Task 8; H4 analysis in Task 9 |
| 4. Optional Jeff family | Optional comparison in Task 10 |
| 5. Expanded temporal-shift analysis | Tasks 3, 8 and 9 |
| 6. Optional YTClickbait21K | Title-only external evaluation in Task 10 |
| 7. Webis-16 provenance / restricted Webis-17 test | Shared data protocol; Tasks 2 and 10 |
| 8. Monthly pilot / eligibility | Chronological split table; Tasks 2–3 |
| 9. Explicit random grouping key | Shared split protocol; Task 2 |
| 10. Reusable leakage audit | Shared leakage policy; Task 2, with external checks in Task 10 |
| 11. Official labels / annotator disagreement | Scientific contract; label provenance in Task 2 and stratified errors in Task 9 |
| 12. Corrected SOTA table and discussion | Task 10 report/presentation alignment, including Zhou and Wu corrections |
| 13. Chronological-evaluation literature | Task 10 report/presentation alignment: Søgaard and Röttger–Pierrehumbert |
| 14. Substantive distinction from Michaluk et al. | Scientific contract and Tasks 8–9 evidence; explicit contribution discussion in Task 10 |
| 15. Analysis / reproducibility / accountability | Shared fitting/provenance protocol, ownership and Tasks 8–10 |
| 16. Formal presentation / attribution / appendices | Task 4 feature documentation and Task 10 report/presentation checks |

## Scientific contract

Predict the released binary `truthClass` from English social-media teasers. Do not derive replacement labels from `truthMean`; preserve `truthJudgments` and `truthMean` for disagreement analysis. Article groups are proxies for articles, not publishers. No publisher-disjoint claim is possible without publisher IDs.

Document the released Webis-17 label construction as specified in v4.1: the modal five-person rating maps 0/.33 to non-clickbait and .66/1 to clickbait, with the fifth judgment breaking multiple-mode ties. This explains label provenance; training still reads the published `truthClass` directly. Webis-16 uses its published three-annotator majority labels, with compatibility checked separately.

| Hypothesis | Controlled comparison | Required evidence |
|------------|-----------------------|-------------------|
| H1 | Δ_Apr = macro-F₁(C) − macro-F₁(B), identical April IDs | Point estimate and paired bootstrap 95% CI |
| H2 | Δ_Feb, Δ_Mar, Δ_Apr versus three grouped-random diagnostics | All window effects, uncertainty and random–temporal differences; random-only gains do not establish robustness |
| H3 | Full C versus C without each three-cue family | Four family ablations across months, feature distributions/correlations and categorized errors |
| H4, secondary | macro-F₁(D_ctx) − macro-F₁(C_ctx), identical complete-case IDs | Matched context effects, coverage and teaser-only controls on the same rows |

**Core completion:** D1 audited data/ledger/manifests; D2 A/B/C on three eligible temporal windows and three grouped-random diagnostics, four family ablations, and the matched-context experiment; D3 uncertainty, drift, calibration, errors, compute analysis, report and presentation. A negative cue effect is valid. The first A/B/C PoC is an intermediate milestone. Webis-16 is a compatibility-dependent external diagnostic. YTClickbait21K and Jeff are optional and cannot block core completion.

**Existing test exposure:** April has already been scored under v2, including A and frozen B/C. Preserve that history. Freeze v4.1 cues, grid, audit thresholds and analysis choices before new scoring, using development data only. April remains the designated final test partition, but the revised study must disclose prior v2 exposure and must not describe it as newly untouched. Do not select features, prompts, thresholds or optional runs from April outcomes, or silently invent a replacement test.

## Immediate PoC scope — presentation checkpoint

**Delivery target:** a working teaser-only A/B/C comparison on **one main temporal window**, plus artifacts for a ten-minute video. This is **less than half of the full project**. Use branch `feat/poc` and plain filenames without proposal-version suffixes.

| Package | Deliver now | Evidence |
|---------|-------------|----------|
| P1. Data | Reproduce ID joins, cleaning and the 391 title exclusions; verify months and exact teaser/title overlap | ID-only ledger, audit JSON, partition/month counts |
| P2. Features | Twelve mechanism cues, four family mappings, shared fixed grid, train-only transformations | Cue specification and focused tests |
| P3. Models | A TF–IDF, B frozen MiniLM, C identical embeddings plus cues | Converged main-window fits, candidate histories, saved models |
| P4. Evaluation | April A/B/C macro-F₁, C−B, positive P/R/F₁, AP, Brier and confusion matrices | ID-aligned predictions, metrics, measured runtime/memory and reload verification |
| P5. Presentation artifacts | Monthly prevalence/length charts, result chart/table, confusion matrices, five illustrative prediction examples | Portable PNG/SVG/CSV and notes |
| P6. Video materials | Twelve timed slides, revised SOTA, exact two-person script, render/recording instructions | `presentation/poc.qmd`, reveal.js HTML, Markdown script and presentation plan |

**Experiment:** Webis-17 `postText` only; train December 2016–February 2017, validate March, test April. Verified pilot sizes: 11,184 / 3,918 / 3,580. Use balanced L2 LR, fixed `C = [0.01, 0.1, 1, 10, 100]`, smallest-C ties, training-only refit/scalers and the default decision rule. Preserve historical snapshots and do not reuse old fitted scores under the changed cue specification.

**Completion evidence:** one command trains and exports results, another reloads frozen models and recomputes predictions/metrics without fitting. Readable figures and result tables must match these outputs. The script and main-slide timings total ten minutes, with one handoff between two presenters. The team records and submits the video; creating slides does not itself record or submit it.

**Deferred:** other temporal windows, three revised grouped-random runs, family ablations, paired bootstrap/CI, full drift/calibration/error analysis, matched article-context models, external corpora and repeated final evaluation. Jeff/LoRA/YouTube remain optional. Five illustrative examples are not the final commitment to twenty categorized errors. One window provides a preliminary point estimate, not proof of temporal robustness or statistical significance.

**Limits to disclose:** prior April scoring, title-based article proxies, absent publisher IDs, unfinished near-duplicate audit and the historical collection period. Correct any known exact leak before scoring. Explain any missing external comparison as a concrete deferred check.

**Delivery progress:** check only after the corresponding evidence is verified; full-project tasks below may remain open after this checkpoint.

- [x] P1 — Raw/processed reconciliation and exact main-split audit
- [x] P2 — Cue/shared-grid implementation and tests
- [x] P3 — Main-window A/B/C fits and frozen models
- [x] P4 — Recomputed metrics/predictions and measured compute
- [x] P5 — Readable, accurate presentation figures/tables/examples
- [x] P6 — Rendered Quarto deck and timed two-presenter script

Verified checkpoint evidence is in `results/poc/main/`: A/B/C April macro-F₁ 0.747911 / 0.711133 / 0.737411, C−B +0.026278, on 3,580 posts. `reproduction.json` records matching predictions/probabilities/metrics from a second full fit in a fresh locked environment. The relevant suite passes 58 tests. The reviewed presentation has twelve timed slides and a synchronized 1,215-word two-presenter script, with the selected reference style applied. Problem/SOTA occupies the first five minutes, the PoC one minute, and the presenter handoff is at 05:00. The team still needs a timed rehearsal, recording and Teams submission; broader tasks below remain subject to their full acceptance/merge criteria.

## Progress and migration baseline

The previous plan marked Tasks 1, 2, 4, 5 and 6 complete for v2. Preserve that credit; unchecked items below mean **v4.1 acceptance is pending**, not that existing work is absent. Mark tasks complete after revised acceptance criteria are met and merged.

| Task | Existing evidence to retain | v4.1 status |
|------|-----------------------------|-------------|
| 1 | Working uv scaffold/config | Reopen for protocol/configuration and documentation changes |
| 2 | Cleaned table and six manifests | Reopen for reconciliation, context fields and expanded audits |
| 3 | EDA notebook previously pending | Pending |
| 4 | Extractor, System A and tuning modules | Reopen for new cues and fixed grid |
| 5 | Verified/shared 18,682-row cache with measured CPU run | Reuse implementation; validate revised-data compatibility |
| 6 | Feature checks, validation runs and frozen April result | Reopen for new cues/grid/data provenance |
| 7–10 | Integration, suites, analysis and external reproduction previously pending | Pending with expanded scope |

- [ ] **Task 1** — v4.1 configuration/protocol (Hubert; Adam review)
- [ ] **Task 2** — Reconciliation, leakage audit and splits (Adam; Igor review)
- [ ] **Task 3** — Monthly EDA and context/external readiness (Mateusz; Adam support)
- [ ] **Task 4** — Exact twelve cues, shared grid and System A (Hubert; Adam review)
- [ ] **Task 5** — Compatible frozen MiniLM cache (Igor; Mateusz review)
- [ ] **Task 6** — Revised controlled B/C training (Igor; Mateusz review)
- [ ] **Task 7** — Reproducible v4.1 A/B/C PoC (Mateusz; Igor review)
- [ ] **Task 8** — Full suite and matched context models (Igor; Mateusz support)
- [ ] **Task 9** — Ablations, uncertainty, drift, calibration and errors (Mateusz; Hubert review/ablations)
- [ ] **Task 10** — External diagnostic, reproduction and delivery (Adam; Igor review)

Historical artifacts: [cache summary](results/embedding_cache.json), [cache measurement](results/embedding_cache_time.txt), [v2 frozen protocol](results/frozen/temporal_main/protocol.json), [April result](results/bc_temporal_main_test.json) and [paired predictions](results/bc_temporal_main_test_predictions.parquet). On 3,580 `temporal_main/test` rows, v2 macro-F₁ was B = 0.710541, C = 0.737422, C−B = +0.026881. These use old cues/randomized selection and are not v4.1 evidence. Do not overwrite snapshots or relabel their numbers.

## Ownership, dependencies and review gates

Follow v4.1 accountability: Adam owns data/provenance/Webis-16, Igor reviews; Hubert owns TF–IDF/cues/ablations, Adam reviews; Igor owns MiniLM/B/C protocol, Mateusz reviews; Mateusz owns split checks/uncertainty/calibration/errors, Hubert reviews. Historical scaffold/data commits by Hubert remain credited. Assign context implementation to Igor, with Hubert supporting relation features and Adam checking article availability.

| Gate | Owner / reviewer | Required evidence |
|------|------------------|-------------------|
| Before implementation | Team | Approve revised plan |
| Before data are final | Adam / Igor | Paths verified; row-level reconciliation; documented article/near-duplicate policy; immutable manifest version |
| Before revised training/scoring | Hubert + Igor / Adam + Mateusz | Appendix A conformance; shared grid; train-only fitting; cache checks and protocol snapshot |
| Before context scoring | Igor / Mateusz | Identical complete-case IDs; fixed serialization/96-word lead; stop list/NER version; truncation audit |
| Before Phase 2 submission | Igor / team | Confirm course method-class interpretation for frozen embeddings + LR; B is not a fine-tuned encoder. Optional Jeff supplies another family if feasible |
| Before final delivery | Adam / Igor | README-only reproduction and consistent report/artifact provenance |

Critical path after approval: Task 1 → Task 2 pilot reconciliation → Tasks 3/4/5 → Task 6 → Task 7 PoC. Final leakage thresholds/manifests can follow the pilot, but precede definitive Tasks 8–9 runs. EDA starts on provisional data and is refreshed after final auditing. No download or GPU allocation is needed merely to approve this plan.

## Shared data and evaluation protocol

### Data stages and leakage

1. Use the public labelled Webis-17 archive `clickbait17-train-170630.zip`. Validate unique IDs and join instances/truth by ID, never row order. The restricted official 18,979-post challenge test is excluded.
2. Retain teaser, timestamp, official label, title, paragraphs and annotator fields. Drop empty teasers; keep the earliest normalized teaser occurrence, using a deterministic ID tie-break. Preserve original case for cues and separate normalization for overlap checks.
3. Reproduce 19,538 raw → 54 empties removed → 411 repeated teasers removed → 19,073 rows. [Existing aggregate stats](data/processed/dataset_stats.json) attribute 391 further removals to title-based article deduplication, yielding the 18,682-row pilot. This is an explanation in current code/stats, not yet v4.1's row-level reconciliation. Export excluded IDs, retained representative IDs and reasons; verify stage-level positive counts. Do not force final counts to equal the pilot.
4. Set `article_group_key` to normalized `targetTitle`, falling back to a namespaced record ID. Hash normalized teasers/titles and stable IDs actually present. Add character n-gram similarity or MinHash candidates; review a fixed sample near the threshold on development data and freeze thresholds/sample IDs before test application. Do not invent publisher IDs or target URLs.
5. At chronological boundaries, keep the earliest eligible occurrence of a repeated article/high-confidence duplicate and exclude later occurrences; never move a future post into training. Record exclusions by window/boundary/reason. Keep random article groups intact and resolve high-confidence duplicate leakage consistently before freezing. Report unconfirmed near matches separately.
6. Apply the reusable audit across each train/validation/test boundary and Webis-17/Webis-16. Keep Webis-17 training data fixed and exclude overlapping external examples, reporting before/after counts. Apply the same principle to optional YouTube evaluation.
7. Version datasets/manifests/checksums. Released manifests contain IDs, assignments, opaque/hashed group keys and provenance, not full teaser/title/body text. Keep raw data/large caches gitignored; retain attribution and access dates.

### Chronological and random splits

These are **provisional v4.1 pilot counts**, before revised audit exclusions.

| Manifest | Train | Validation | Test | Pilot sizes (train / val / test) |
|----------|-------|------------|------|--------------------------------|
| `temporal_w1_dec_jan_feb` | Dec 2016 | Jan 2017 | Feb 2017 | 3,832 / 3,848 / 3,504 |
| `temporal_w2_decjan_feb_mar` | Dec–Jan | Feb 2017 | Mar 2017 | 7,680 / 3,504 / 3,918 |
| `temporal_main` | Dec–Feb | Mar 2017 | Apr 2017 | 11,184 / 3,918 / 3,580 |

Require test-month N ≥ 1,000 after cleaning; exclude ineligible windows with a reason rather than merging future months. Record final N/prevalence for every partition. Report context complete-case sizes separately and document any additional eligibility decision before context scoring.

Keep random seeds 42, 43 and 44. Derive random proportions from the finalized main chronological manifest (pilot 11,184:3,918:3,580, approximately 59.9/21.0/19.2), replacing 70/15/15. Stratify article groups by majority official label; **proposed tie rule: class 0**. Log achieved post-level ratios/prevalence deviations and group counts. Random results diagnose optimism, not future-time robustness.

### Fitting, metrics and provenance

- A = word 1–2 + character 3–5 TF–IDF with L2 LR. B = frozen pinned 384-dimensional `all-MiniLM-L6-v2` embeddings + LR. C = exactly B's embeddings + twelve train-standardized cues + LR. All use `class_weight='balanced'` and identical IDs.
- Replace randomized selection with a fixed grid. **Proposed implementation choice**, since v4.1 omits numeric values: `C = [0.01, 0.1, 1.0, 10.0, 100.0]`, ascending; ties select smallest `C`. Use the same grid/budget for A/B/C, context models and ablations. Each model can select a different best value. Freeze the grid before scoring.
- Fit vocabulary/IDF/scalers/LR on train only. Retain train-only final refit and the default 0.5 decision rule. Select by each window's validation macro-F₁: January for W1, February for W2, March for W3. The proposal's March-tuning statement applies to the main window. No k-fold CV or test-driven threshold adjustment.
- Fail on missing/stale features or unconverged fits. Record all candidates and shared solver/iteration changes. Save fitted transforms/classifiers and ID-aligned labels, predictions and probabilities.
- Primary: macro-F₁ and paired C−B. Secondary: positive precision/recall/F₁, AP with prevalence, Brier, reliability, confusion matrices, wall time and peak memory. Freeze bootstrap resample count/seed before scoring; resample paired instances or article/duplicate clusters where dependence remains. Use identical draws for compared systems; April's 95% CI is primary.
- Log hardware, actual Python/package versions, lockfile, seeds, code revision, retrieval dates, input/feature/model hashes and measurement procedures. Measure encoding, feature extraction, tuning/training and inference separately; distinguish host RSS and GPU memory. Interpret calibration changes with prevalence; any fitted recalibration uses validation only and is separately labelled.

## Task 1 — Configuration and protocol record

**Executor: Hubert · Reviewer: Adam.** Update `configs/experiment.yaml` and config validation for fixed-grid selection, cue/protocol versions, split eligibility, random proportions, audit/context settings and optional extensions disabled by default. Keep seeds and train-only refit explicit. Record adopted grid/tie rules after approval.

Align `AGENTS.md`, README and data/cue docs as the corresponding implementation lands. Introduce versioned outputs such as manifest snapshots and separate `results/poc/<run-id>/` outputs; prevent silent v2 reuse/overwrite. Store a machine-readable protocol snapshot before scoring. Preserve historical reproduction via old code revision/hashes.

**Done when:** locked setup/config smoke check work, scientific settings have one source of truth and v2/v4.1 outputs are distinguishable. No experiment run is required.

## Task 2 — Reconciliation, overlap audit and manifests

**Executor: Adam · Reviewer: Igor; Hubert supports existing loader/split code.** Extend `src/clickbait/dataset.py`, `src/clickbait/splits.py`, `scripts/build_dataset.py` and `scripts/build_splits.py`.

- Implement the data contract above, including `targetParagraphs`/`truthMean`, validated joins and the exclusion ledger.
- Add a reusable audit module/CLI for exact/approximate matches, development-sample threshold review and boundary/cross-corpus summaries. Keep global earliest-title filtering traceable; explain differences from the final boundary policy.
- Generate versioned temporal/random manifests with eligibility, majority strata and main-window proportions. Save checksums, month ranges, excluded IDs/reasons, achieved balance and overlap counts; preserve old manifests.
- Label pilot/final audit status. A provisional PoC can use a recorded pilot manifest; definitive experiments require the final audited version.

**Done when:** the 391-row difference is reconciled by ID/reason; regeneration is deterministic; prohibited ID/article/high-confidence duplicate overlap is absent; reviewers can trace every count. Final N may differ from 18,682.

## Task 3 — Monthly EDA and readiness

**Executor: Mateusz · Data support: Adam.** Create executable `notebooks/eda.ipynb` and a machine-readable summary; add locked notebook dependencies if needed.

Include exclusion stages, labels and token/character lengths by class/month, exact/near-duplicate/article audit tables, per-partition N/prevalence, the row reconciliation, and per-cue frequency/distributions/correlations/monthly variability with bootstrap intervals. Describe length/topic proxies and prevalence effects without redesigning cues from test labels.

Reproduce or explain differences from monthly pilot totals: Dec 3,832 (1,012 positive), Jan 3,848 (884), Feb 3,504 (814), Mar 3,918 (908), Apr 3,580 (830). Report usable title/lead coverage and missingness by partition/class. Compare Webis-16 schema, label rates, lengths and overlap if locally ready; otherwise state the concrete obstacle. Generic “collection pending per proposal” is obsolete because v4.1 establishes public access.

**Done when:** notebook executes, figures have self-contained scope/split captions and summaries identify data/audit versions. Basic EDA can precede Task 4; refresh cue plots and final split summaries afterward.

## Task 4 — Exact twelve cues, shared grid and System A

**Executor: Hubert · Reviewer: Adam.** Replace `src/clickbait/cues.py`, lexicons and `docs/cues.md`. Appendix A is authoritative for every token set, phrase, denominator and edge case; keep this order.

| Family | # | Cue | Rule/output |
|--------|---|-----|-------------|
| I. Referential withholding | 1 | Initial unresolved pointer | Binary first-token rule |
| I | 2 | Indefinite-referent density | Listed token hits / n |
| I | 3 | Delayed-revelation frame | Binary full-phrase match |
| II. Audience involvement | 4 | Direct-address density | Listed token hits / n |
| II | 5 | Action invitation | Initial verb / “find out” rule |
| II | 6 | Question hook | Listed initial token and question mark |
| III. Affective/narrative framing | 7 | Surprise-word density | Listed token hits / n |
| III | 8 | Epistemic-distance density | Listed token hits / n |
| III | 9 | Narrative reversal | Binary listed phrase match |
| IV. Specificity/presentation | 10 | Numbered payoff promise | Integer 1–99 in first two tokens; payoff noun within following four |
| IV | 11 | Attention punctuation | min(1, (! + ? + ellipsis events) / m) |
| IV | 12 | Referent-to-anchor imbalance | P / (P + A + 1); capitalized non-initial anchors excluding ALL-CAPS |

Use NFKC and normalized apostrophes/whitespace; ASCII letter tokens with optional internal apostrophes or digit runs; case-insensitive whole-token matching without stemming; n = max(1, token count), m = max(1, character count); twelve zeros for empty input. Preserve original case for anchors. Version exact Appendix A lexicons; remove old substring semantics. Define four groups of three cues.

Update `src/clickbait/tuning.py`, `src/clickbait/models/system_a.py` and `scripts/train_system_a.py` for fixed-grid selection and separate training/validation/scoring. Focused tests cover Unicode/apostrophes, phrase boundaries, empty input, numbered-payoff positions, ellipses, capitalization, column/family order, train-only fitting and equal candidate budgets.

**Done when:** twelve outputs conform to Appendix A and A exports fixed-grid validation history/model. Test scoring happens through frozen PoC/suite evaluation, not implicitly during tuning.

## Task 5 — Compatible frozen MiniLM cache

**Executor: Igor · Reviewer: Mateusz.** Retain the pinned encoder revision, normalization, sequence limit, ID/text fingerprints and `scripts/cache_embeddings.py` checks. The v2 cache covers 18,682 teasers, was shared/verified and has measured CPU cost; preserve its provenance.

Check revised IDs/text/encoder settings. Reuse unchanged teaser vectors; regenerate missing/changed entries or create a compatible subset artifact as needed. Record revised manifest coverage without overwriting old provenance. Cue changes alone do not invalidate embeddings. Context serialization/lead caches belong separately to Task 8.

**Done when:** every revised teaser ID has a finite 384-dimensional vector; B/C load identical aligned vectors; round-trip/sampled direct-encoding checks pass. Measure new encoding costs separately from cache reuse.

## Task 6 — Revised controlled B/C training

**Executor: Igor · Reviewer: Mateusz.** Adapt `src/clickbait/models/neural.py`, `scripts/check_neural_features.py`, `scripts/train_neural.py` and `scripts/evaluate_neural.py` for new cues/grid and versioned artifacts.

B has 384 embedding columns; C has the identical columns plus twelve cues. Fit only C's cue columns with a train-only scaler. Train/validate without test-label access; export models/scaler, cue order, all candidate scores/convergence, input hashes and aligned validation predictions. New frozen evaluations must validate the revised protocol rather than bypass v2 hash checks.

**Done when:** revised main-window B/C validation succeeds; saved models reproduce probabilities; scaler statistics match train; IDs/grid/embedding values agree; protocol snapshot is ready for Task 7. Retrain both B/C because grid/data may change even when vectors are reused.

## Task 7 — First reproducible v4.1 PoC

**Executor: Mateusz · Reviewer: Igor.** After Tasks 1/2/4/5/6, add `scripts/run_poc.py` to coordinate a recorded `temporal_main` A/B/C run, check compatibility and export versioned `poc_summary.json`, predictions and a slide table.

Freeze protocol before scoring. Table fields: proposal/protocol/data versions, split/partition, test N/prevalence, A/B/C macro-F₁, C−B and measured runtime/memory. Label pilot status until final leakage auditing; never mix v2 A/B/C with revised scores. Add a README reproduction command. This first PoC does not depend on context or optional models.

**Done when:** one command produces a real-data three-system result with auditable artifacts and measured cost. Immediate delivery additionally includes packages P1–P6 above: basic EDA/audit, slide-ready artifacts, a timed presentation and model reload verification. Confidence intervals and full error analysis are deferred. The immediate delivery priority advances the revised proposal's original three-way PoC target of 26 November–2 December; existing v2 results remain historical evidence until replaced by a completed, clearly labelled v4.1 pilot.

## Task 8 — Full suite and matched context experiment

**Executor: Igor · Support/review: Mateusz; Hubert supports relation cues; Adam checks completeness.** Add `scripts/run_experiments.py` using shared training/evaluation functions. Definitive runs require final audited manifests.

**Primary suite:** A/B/C × three eligible temporal windows and three random seeds. Export selected regularization, all candidate histories, predictions, metrics, hashes and per-stage measured cost. Include ≥3 runs with spread or justify why deterministic LR repeats have no meaningful stochastic spread. Different windows are not repetitions of one experiment; report window variation and random-seed variation separately.

**Required secondary context suite:** select usable teaser/title/paragraph rows; concatenate non-empty paragraphs in order and take the first **96 word tokens** as lead. Pin tokenization and field-labelled teaser/title/lead serialization before scoring; audit MiniLM truncation. Intersect base manifests with complete-case IDs without repartitioning. All four models share serialized input, rows, grid and train-only fitting:

| System | Features |
|--------|----------|
| A_ctx | TF–IDF of serialized teaser/title/lead + LR |
| B_ctx | Frozen MiniLM of that same serialization + LR |
| C_ctx | B_ctx + twelve teaser-only cues |
| D_ctx | C_ctx + three relation cues |

Implement Appendix B: R1 = lexical intersection size / max(1, teaser content-word type count), with lowercasing/fixed English stop list; R2 = teaser entities absent from lead / max(1, teaser entity count), using normalized case-insensitive spaCy person/organization/location/product entity sets; R3 = (1 + cosine(teaser, lead)) / 2 using the same pinned, unit-normalized MiniLM. Empty teaser content/entity sets yield zero; missing leads are excluded, not imputed. Pin spaCy package/language-model artifact and stop list. Key separate context/lead caches by exact text/encoder; scale added scalar features on train only.

Run context comparisons across eligible chronological windows. Report D_ctx−C_ctx for H4 and C_ctx−B_ctx for teaser-cue value with context. Train/tune teaser-only A/B/C controls on the **same complete-case training/validation rows** and evaluate on the same test rows, so context effects do not confound training availability. Label full-core-model subset scores separately if included. Report coverage/prevalence/selection effects. Relation cues never enter primary C or text-only external tests.

**Done when:** a complete core folder contains primary/context metrics and paired predictions, matching IDs/protocol snapshots and measured costs. Optional experiments remain separate suites.

## Task 9 — Ablations, uncertainty, drift, calibration and errors

**Executor: Mateusz · Reviewer: Hubert; Hubert implements family ablations, Adam reviews them.** Analyze frozen Task 8 outputs using small scripts such as `bootstrap_paired.py`, `ablate_cues.py`, `calibration_plots.py` and `export_errors.py`.

- April paired C−B 95% CI; all Δ_t effects with uncertainty; explicitly defined random–temporal contrasts with different test populations visible.
- Four leave-one-family-out C variants, each removing three cues, retrained/tuned on identical train/validation IDs and grid. Compare family effects by month; no test-driven lexicon changes.
- Per-cue frequencies/distributions/correlations/monthly stability with bootstrap variability; relate effects to prevalence and length/topic proxies without claiming time is the only cause.
- Brier/reliability, AP with prevalence, confusion matrices and measured cost; explain class-weighted probabilities and prevalence shifts in calibration interpretation.
- Secondary context D_ctx−C_ctx and C_ctx−B_ctx paired effects/uncertainty and matched teaser-only controls, separately from H1–H3.
- ≥20 manually checked misclassified/model-disagreement examples in named categories, including low/high annotator agreement. Inspect cautious-reporting terms, pointers, numbered promises, anchor proxies and context/NER failures where actually observed; do not assert unobserved error types.

**Done when:** H1–H4 can be assessed, including negative/inconclusive outcomes; error categories, uncertainty procedures and self-contained captions are report-ready. Name data version/split/partition on every figure/table.

## Task 10 — External evaluation, reproduction and delivery

**Executor: Adam · Reviewer: Igor; all contribute to reports/video.** Complete `scripts/eval_webis16.py` for v4.1's Webis-16 source: Zenodo record 3251557, `corpus-webis-clickbait-16.zip`, CC BY 4.0. Public availability is established in the proposal; local acquisition/schema checks remain. Verify English tweet-text mapping, majority-vote labels and overlap; log retrieval/exclusions/final N/prevalence.

Evaluate with unchanged Webis-17 main-training A/B/C selected on March. Do not fit transforms, retune thresholds, alter labels or train on Webis-16. If incompatible/unavailable locally, document the precise reason and unperformed comparison. Exclude context models from this text-only test.

**Optional YTClickbait21K:** inspect `main_dataset.csv` and video dates from the proposal's Figshare source. Evaluate English titles only with unchanged Webis-trained A/B/C after overlap checks. Descriptions/thumbnails/channels/metadata are not inputs. Report platform/annotation confounds; later publication does not prove all videos postdate Webis or isolate temporal shift.

**Optional Jeff-Qwen3.5:** Igor leads, Mateusz reviews, once the core path is secure. Use Jeff's native score/choice interface: zero-shot, fixed balanced training-only few-shot demonstrations per window, LoRA if feasible. Pin model/code revision, label descriptions, prompt, option order, demonstration IDs and probability extraction before evaluation. Each adapted window needs a separate adapter; explicitly label main-only LoRA. No Jeff–cue fusion. Record measured compute/skipped variants; optional work must not delay core/context delivery.

README must cover locked setup, data/audit/manifests, cache construction/reuse, one-command pinned PoC reproduction and full-suite/analysis commands. Distinguish v2 snapshots, v4.1 pilot/final core and optional results. Adam performs clean-environment README-only reproduction; Igor checks IDs/hashes/numbers with stated numeric tolerances where hardware matters.

**Report and presentation alignment — Igor leads, all review.** Apply these requirements to the next report/video updates, including Phase 2, rather than waiting for final delivery:

- Carry forward v4.1's corrected SOTA evidence: name dataset and train/dev/test/CV conditions, input modalities and metric averaging for every quoted score; keep unspecified averaging explicit. Credit Zhou for the winning challenge system, replace the insufficiently documented Yu entry with Wu et al. (2020), and connect title–body interaction work to the secondary context experiment. Do not rank unlike published results as a common benchmark.
- Incorporate Søgaard et al. (2021) and Röttger and Pierrehumbert (2021) into the motivation and interpretation of chronological evaluation; retain the distinction between temporal and publisher/source separation.
- Explain the distinction from Michaluk et al. through matched embeddings/classifiers/tuning, chronological effects, mechanism-level ablations, leakage audits and matched context relations. Support claims with the corresponding evidence; do not frame model substitution or isolated pronoun/punctuation patterns as the scientific novelty.
- Define abbreviations on first use, check citation/source links and published versions, preserve the course-template attribution to Anna Wróblewska and the ACL 2015 template, and include readable exact cue/relation appendices consistent with implemented lexicons, formulas and edge cases.

**Done when:** one result independently reproduces, Webis-16 is evaluated or its obstacle documented, and core artifacts/course submissions are complete. Optional suites are not completion requirements.

## Calendar and course deliverables

These follow v4.1 planning targets, not claimed completion. Context is scheduled explicitly because it belongs to D2 although the proposal's weekly table gives it no separate row.

| Period | Accountable lead | Target |
|--------|------------------|--------|
| 4–18 Nov 2026 | Igor | Source/feedback audit; PoC evidence/first cue specification; 18 Nov mid-term presentation and 10-minute video |
| 19–25 Nov | Adam | Monthly EDA, 391-row ledger reconciliation/article audit; 25 Nov individual Q&A |
| 26 Nov–2 Dec | Hubert | Exact cues/v4.1 three-way PoC; Phase 2 EDA/report/MR/reproduction |
| 3–9 Dec | Adam | Development-reviewed duplicate thresholds/final splits; freeze context selection/serialization |
| 10–16 Dec | Igor | Matched temporal/random A/B/C runs and required context suite |
| 17–23 Dec | Mateusz | Four family ablations, uncertainty/drift/calibration, ≥20 errors and context interpretation |
| 24–30 Dec | Adam | Contingency/external compatibility and evaluation; optional work only if schedule allows |
| 31 Dec–6 Jan 2027 | Hubert | Independent reproduction/report checks; Adam runs README check, Igor verifies |
| 7–13 Jan | Igor | Final paper, source/MR, video/question session; all review |

**Phase 2, 2 December:** real-data PoC plus number; EDA with leakage and another dataset or precise absence reason; method classes/hyperparameters/splits/metrics; README reproduction; measured runtime/memory; revised report/MR; rebuttal to every supervisor and meeting #8 Q&A point with checkable locations. Final audit freezing is scheduled after Phase 2, so identify pilot status and remaining audit work.

**Phase 3, 13 January 2027:** full core evidence/interpretation; ≥3 runs with spread or justified deterministic exception; ≥20 categorized errors; reproducibility/measurement procedures; limitations with consequences; rebuttal through meeting #13 Q&A. Every phase report needs actual contribution tasks/hours consistent with git, formal LLM-use declaration and data statement. Preserve folder `kolodziej_kowalski_kaniasty_iwaniuk` and course templates.

## Completion checks and limits

- Verify changed cue semantics, joins/exclusions, split eligibility/group rules, cache compatibility, train-only fitting, shared tuning and matched context rows with focused tests. Run relevant existing tests; old tests passing does not prove new cue conformance.
- Preserve historical artifacts and regenerate dependent features/models when inputs change. Embedding reuse does not authorize reusing fitted classifiers/scores under a new protocol label.
- Label results temporal or grouped-random. Historical five-month coverage, topic/prevalence confounds, subjective labels, pretrained exposure and prior April scoring limit interpretation.
- Measure/discuss complete-case selection, title proxies, NER errors, semantic false matches and truncation. Context findings do not establish performance without articles or on text-only external data.
- Spoiler generation, multilingual modelling, browser extensions, live scraping and factual verification remain outside scope. Article leads are used only in the separately labelled consistency experiment.
