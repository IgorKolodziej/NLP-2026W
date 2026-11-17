# Ten-minute presentation plan

**Status: approved and implemented.** The deck, exact two-person speaking script and rendered HTML follow this storyboard. Problem/SOTA occupies the first five minutes, the PoC occupies one minute. Rehearsal and video recording remain team actions.

## Purpose and balance

Explain the research problem, what existing approaches achieve, and the scientific question that remains. Then introduce our proposed study and use the current PoC as a short progress checkpoint.

| Part | Time | Share |
|------|------|-------|
| Problem and state of the art | 00:00-05:00 | 50% |
| Our research design, remaining experiments and intended contribution | 05:00-07:10 and 08:10-10:00 | 40% |
| Current PoC and preliminary result | 07:10-08:10 | 10% |

**Presenter 1:** problem and SOTA, 00:00-05:00. **Presenter 2:** proposed study, brief PoC and future work, 05:00-10:00. One handoff at 05:00.

Source of scientific scope: [NLP_Proposal_v4-1.tex](../NLP_Proposal_v4-1.tex), especially the research questions, related work/SOTA table, models, evaluation protocol and cue/context appendices. The video also follows the course rules and assessment criteria. It prepares the mid-term Q&A and Phase 2 submission, rather than claiming that the full project is complete.

## Storyboard

### 1. Project title and central question

**00:00-00:25 - Presenter 1: 25 seconds**

Introduce *Clickbait Without the Click: Linguistic Cues under Temporal Shift*. State the broad question: when do inexpensive, interpretable language cues add information beyond learned text representations, and does that value persist across time?

Keep the cover brief. No implementation status or performance numbers yet.

### 2. What makes clickbait detection difficult?

**00:25-01:20 - Presenter 1: 55 seconds**

- Define the input as an English social-media teaser and the target as the published human clickbait label.
- Use one short corpus example to explain curiosity gaps, withheld referents or promised revelation.
- Explain the ambiguity: ordinary reporting can use similar wording, and the label reflects perceived clickbait.
- Explain the generalization problem: language/topic composition may change between collection periods.
- Distinguish the task from factual verification, click prediction and spoiler generation.

**Visual:** one readable teaser with an annotated linguistic cue. Its classifier predictions are unnecessary here.

### 3. Classical approaches: explicit linguistic signals

**01:20-02:05 - Presenter 1: 45 seconds**

Discuss the idea behind feature-based detection, not just a list of authors:

- **Potthast et al. (2016):** detect clickbait in publisher tweets using explicit lexical/stylistic cues and a random forest. Explain the central idea: measurable wording patterns can carry predictive information.
- **Biyani et al. (2016):** use article informality alongside title/body/URL information with boosted trees in a news stream. Explain how this broadens detection beyond the teaser itself.
- **Connection to our study:** retain inspectable signals, then ask whether they add information beyond fixed embeddings and remain useful in later months. Our primary comparison needs only the teaser, article context is a separate experiment.

**Visual:** compact method/input/evidence table. Any published number must name dataset, partition and metric type. Explain that weighted and positive-class F1 are different quantities.

### 4. Neural approaches: learned text representations

**02:05-02:55 - Presenter 1: 50 seconds**

Explain the progression from explicit counts to learned representations:

- **Zhou (2017):** a bidirectional GRU encodes the tweet, attention weights its tokens to learn a task-specific representation without manually designed cues. The system won the Clickbait Challenge 2017.
- **Indurthi et al. (2020):** transformer representations and boosted regression predict how strongly clickbait-like a post is, rather than treating every positive as equally clickbait-like.
- **Connection to our study:** learned representations motivate our embedding baseline. We keep the encoder frozen and compare the same embeddings with and without explicit cues, our target is the released binary label.
- **Yi et al. (2022):** retain a short supporting reference to learning from limited/biased labels, explain its joint classification/generation and contrastive objective in the preparation notes rather than adding a third architecture explanation to this fifty-second slide.

Explain what these approaches add and why regression strength, binary classification, unlike inputs and different evaluation partitions prevent a single score ranking.

**Visual:** a small comparison of representation, prediction task and evaluation conditions. Use only selected evidence from the proposal, without overloading the slide with architectures or scores.

### 5. Michaluk et al.: our starting point

**02:55-03:45 - Presenter 1: 50 seconds**

Dedicate this slide to the seed paper and our differences:

- Explain its OpenAI embeddings, fifteen linguistic features and XGBoost hybrid.
- Describe the mixed-source, balanced dataset and random 80/10/10 evaluation.
- Its published embedding-only/hybrid comparison also changes embedding width. Our B/C comparison preserves exactly the same embedding coordinates and LR family/tuning budget.
- Contrast its whole-feature-block comparison with our planned chronological tests, paired uncertainty and four family removals.
- Do not rank its published F1 against our April macro-F1 or imply that hybrid features are new.

**Visual:** three comparison rows: representation control, evaluation and cue evidence. No other paper appears on this slide. The source is in presenter notes.

### 6. Title style and article context

**03:45-04:10 - Presenter 1: 25 seconds**

- Explain Wu et al.'s content/style modelling and title-body attention.
- Motivate the planned relation cues: word overlap, missing teaser entities and embedding similarity.
- All context models receive identical teaser/title/lead input and records. The incremental relation test starts from a baseline that already includes the twelve teaser cues.

**Visual:** concise description and three relation cues. Keep this secondary experiment explicitly planned.

### 7. What the existing evidence does not settle

**04:10-05:00 - Presenter 1: 50 seconds**

Synthesize the literature rather than introduce another model:

- **Søgaard et al. (2021):** random splits can give optimistic estimates of performance on new samples, motivate evaluating beyond a shuffled sample of one collection.
- **Röttger and Pierrehumbert (2021):** temporal adaptation can capture changes in language without improving the downstream task beyond domain adaptation, motivate measuring task effects rather than assuming them from dates.
- Source-separated work such as RoCliCo tests unseen publishers. Our chronological study tests later collection periods, without publisher IDs it cannot establish unseen-publisher generalization.
- Input availability, label definitions, metric averaging and grouping/leakage controls matter when interpreting reported results.

End with the research gap: a controlled test of **when and why** the cue contribution survives, with matched embeddings/classifiers and mechanism-level analysis.

**Handoff at 05:00.** The first half has covered only the problem, existing approaches and the gap.

### 8. Our proposed study

**05:00-06:15 - Presenter 2: 75 seconds**

Introduce our design as a response to that gap:

- **A:** word/character TF-IDF plus logistic regression.
- **B:** frozen MiniLM embeddings plus logistic regression.
- **C:** exactly B's embeddings plus twelve prespecified cues and the same classifier family/tuning budget.
- Describe the four three-cue families in plain language, with one or two concrete trigger examples.
- Map the proposal's goals: **H1** incremental cue value, **H2** temporal stability, **H3** family mechanisms, and secondary **H4** context relation value.
- Explain that the context experiment gives every model the same available teaser/title/lead, rather than giving additional input only to the proposed system.

**Visual:** simple A/B/C comparison and a concise research-question map. Exact cue formulas and context variants remain in the proposal and repository documentation.

### 9. Data and evaluation design

**06:15-07:10 - Presenter 2: 55 seconds**

- Primary corpus: public Webis-17 labelled training release, official labels and December 2016-April 2017 dates.
- Briefly distinguish the 19,538 raw rows from the verified 18,682-row cleaned pilot, with 23.8% positives.
- Main window: train December-February, validate March, test April. The full study adds the other chronological windows and three article-grouped random diagnostics.
- Explain macro-F1, paired C−B and train-only fitting/validation selection without reciting implementation details.
- Position Webis-16 as an external, evaluation-only diagnostic. It is publicly available, but our compatibility/overlap checks and transfer result remain unfinished.

**Visual:** chronological split table or timeline. Keep detailed exclusion counts and source/licence notes in the repository evidence.

### 10. Current PoC: a brief feasibility checkpoint

**07:10-08:10 - Presenter 2: 60 seconds**

Use one slide to demonstrate current progress:

- The real-data pipeline runs A/B/C on identical main-window IDs and exports reproducible predictions.
- April macro-F1: **A 0.7479, B 0.7111, C 0.7374**, **C−B +0.0263**.
- Interpret both findings: cues improve B in this comparison, while TF-IDF remains strongest.
- State that these are preliminary point estimates from one window. April was excluded from fitting but had earlier pilot exposure.

**Visual:** one small result chart/table, with split, test N and prevalence. Keep commands, tests, hashes, memory, runtime details and individual prediction examples in the repository evidence. Do not give the PoC multiple main slides.

### 11. Remaining experiments and the evidence they provide

**08:10-09:10 - Presenter 2: 60 seconds**

Return to the research questions:

- **H1:** paired uncertainty for the cue gain.
- **H2:** effects across February/March/April and grouped-random diagnostics.
- **H3:** remove one cue family at a time, inspect feature changes and at least twenty categorized errors.
- **H4:** matched complete-case context models, then test the incremental relation cues.
- Complete near-duplicate/cross-corpus auditing and interpret calibration with class prevalence.

The optional Jeff and YouTube extensions are supplementary, not the project's main contribution. All current PoC classifiers use LR, so an acceptable distinct-method-class plan for Phase 2 still needs confirmation, the proposal's Jeff comparison is one feasibility candidate.

**Visual:** question → experiment → evidence mapping. Avoid presenting future experiments as completed work.

### 12. Intended contribution and next checkpoint

**09:10-10:00 - Presenter 2: 50 seconds**

Close on the scientific aim: an auditable account of **when and why interpretable clickbait cues help under chronological evaluation**, plus the separate test of article relations.

- A negative or unstable gain is informative if the controls hold.
- State the principal interpretation limits: historical collection, topic/time confounding, imperfect article proxies and absent publisher IDs.
- Before Phase 2, strengthen the audit, revised literature review and reproduction package, and answer supervisor/Q&A feedback.
- Invite focused feedback on the scientific controls and prioritization of the remaining experiments.

**Visual:** dark closing slide in the approved reference style. Avoid ending on code or test counts.

## Paper-level narrative and our intended differences

These notes define the substance behind slides 3-7. They are preparation material, not additional spoken paragraphs. In the video, explain each main paper's question and mechanism before connecting it to our design. Reserve the most time for the seed paper. Keep full scores, partitions and supporting papers in the proposal and preparation notes.

### Explicit features: what can wording tell us?

**Potthast et al. (2016)** establish feature-based detection in publisher tweets: encode observable lexical/stylistic signals and train a random forest. This is a foundation for our cue-based reasoning, not evidence that we invented these linguistic patterns. **Our intended difference:** test the extra predictive value of a fixed, documented combination over identical sentence embeddings, then inspect its stability by month and cue family. [Paper](https://doi.org/10.1007/978-3-319-30671-1_72).

**Biyani et al. (2016)** investigate article informality and use title, body and URL information with boosted trees. This illustrates that detection can exploit information beyond a headline. **Our intended difference:** keep the primary teaser-only setting separate from the context setting, so any context result is interpreted against comparators with the same available input. Its Yahoo-news scores do not directly predict performance on Webis teasers. [Paper](https://ojs.aaai.org/index.php/AAAI/article/view/10388).

### Learned representations: can the model discover the signals?

**Zhou (2017)** learns tweet representations with a bidirectional GRU and token attention, reformulating clickbait-strength prediction using the annotation categories. Manual feature engineering is unnecessary for this approach. **Our intended difference:** use a fixed encoder to make the added contribution of explicit cues measurable. This is a controlled feature study rather than a reproduction of the challenge winner. [Paper](https://arxiv.org/abs/1710.05364).

**Indurthi et al. (2020)** treat clickbait as a matter of degree and investigate transformer-based strength regression. **Our intended difference:** evaluate released binary labels and paired macro-F1 differences. Their strength-prediction task and official challenge test remain distinct from our chronological partitions of the public training release. Their result motivates learned representations, but does not answer our cue-stability question. [Paper](https://aclanthology.org/2020.coling-main.425/).

**Yi et al. (2022), preparation notes only:** address limited and biased labels by jointly learning to classify text and generate text conditioned on labels, using a variational model and contrastive separation. **Our intended difference:** investigate explicit cue value and temporal stability with a frozen representation, rather than propose a new training objective to use labels more effectively. Do not imply that our study tests or solves label scarcity. [Paper](https://www.ijcai.org/proceedings/2022/0621).

### Hybrid and context approaches: our closest connections

**Michaluk et al. (2026)** provide the closest hybrid precedent: embeddings plus fifteen explicit informativeness/style features with XGBoost, evaluated on a balanced mixed-source corpus using a random split. **Our intended difference:** isolate twelve prespecified cues using the same cached embeddings and LR family/tuning budget, compare later-month and grouped-random effects, investigate families and errors. These are proposed experimental extensions, not an assertion that the paper's reported gains are invalid. Its published F1 cannot be ranked against our April macro-F1. [Paper](https://arxiv.org/abs/2602.18171).

**Wu et al. (2020)** combine learned title/body content, character-level title style and co-attention for title-body relatedness. **Our intended difference:** test inexpensive, transparent relationscontent-word overlap, missing teaser entities and embedding similarityon a fixed article lead. Compare context models on identical complete-case rows and inputs, with and without relation cues. The idea of comparing title and body is established, our contribution is the controlled temporal test. [Paper](https://aclanthology.org/2020.ccl-1.106/).

### Evaluation studies: what should count as evidence?

**Søgaard et al. (2021)** challenge reliance on random splits as estimates of performance on new samples. We apply that methodological concern to clickbait cue effects through three chronological tests and grouped-random diagnostics. **Röttger and Pierrehumbert (2021)** distinguish temporal language adaptation from downstream benefits, we therefore measure distribution changes and cue effectiveness separately. Neither paper establishes that our particular corpus must show degradation. [Split-design paper](https://aclanthology.org/2021.eacl-main.156/), [temporal-adaptation paper](https://aclanthology.org/2021.findings-emnlp.206/).

### The difference the audience should remember

**We want to establish when and why a fixed set of interpretable cues adds predictive value beyond learned representations, whether that benefit persists over time, and whether transparent teaser-article relations add further information under matched conditions.**

| Intended contribution | Comparison that supplies the evidence | Current status |
|-----------------------|---------------------------------------|----------------|
| Incremental teaser-cue value | C minus B: identical embeddings, inputs, splits and LR family/tuning budget, add only the cue block | One chronological window has point estimates, paired uncertainty remains |
| Stability over time | Three chronological C−B effects, alongside three grouped-random diagnostics | Main April window only, full comparison remains |
| Which cue families matter | Remove each of four families, inspect distributions and categorized errors | Planned |
| Incremental relation value | D_ctx minus C_ctx, identical teaser/title/lead and complete-case rows | Planned secondary experiment |

Use predictive-contribution language. Ablations do not establish a causal account of reader behaviour. Individual cue patterns, hybrid classification and title-body comparison already have precedents. A negative or unstable effect is a valid outcome of the proposed study.

## Supporting repository evidence, outside the deck

- Detailed SOTA comparison conditions, metric definitions and source links.
- Exact twelve-cue definitions and four context-system variants.
- Dataset provenance, exclusion ledger summary and overlap evidence.
- PoC runtime/memory, test/verification/reproduction details and secondary metrics.
- Selected model-disagreement examples, if useful for Q&A.

## Style and implementation

Preserve the approved CSS/QMD reference style: warm paper slides, dark teal cover/closing, embedded Inter font, teal/orange accents, a 1600×900 canvas, with citations in presenter notes rather than small slide footers. Do not change the visual direction while rebalancing the content.

Implementation follows the approved sequence:

1. Eleven slides follow the storyboard. The deck ends at the closing slide, detailed supporting evidence remains in the proposal, documentation and PoC artifacts.
2. The audited script has 1,215 spoken words with a 05:00 handoff and contiguous 600-second timing windows. Speech is synchronized with slide notes.
3. The reveal.js HTML embeds its runtime, style, font and figures. Rendered slides are reviewed for fit, readability, citations and evidence.

The video duration still requires an aloud rehearsal, the schedule is a target rather than a measured recording.
