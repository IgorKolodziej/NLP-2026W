Dear Team,

Your proposed Phase 1 assessment is shown below. The scientific score follows the published rubric; any verified administrative penalty is applied separately.

**Phase 1 grade calculation**

| Item                                         | Points     |
| -------------------------------------------- | ---------- |
| Scientific assessment (criteria 1.1–1.5)     | **5.5/10** |
| Confirmed formal penalty                     | **0**      |
| **Phase 1 score after confirmed penalty**    | **5.5/10** |
| Exceptional research (provisional, separate) | **0/1**    |

No confirmed formal penalty has been applied. Any administrative issues described below are recorded for correction or an instructor decision, not treated as additional deductions.

The proposed exceptional research point has **not** been added to the Phase 1 mark; it requires separate verification and approval.

**Criterion-by-criterion assessment**

| Criterion                       | Proposed score | Maximum |
| ------------------------------- | -------------- | ------- |
| 1.1 State of the art            | 1.5            | 3       |
| 1.2 Datasets and their status   | 1.5            | 3       |
| 1.3 Solution concept and plan   | 1              | 2       |
| 1.4 Text quality and references | 0.5            | 1       |
| 1.5 Data statement              | 1              | 1       |
| **Core total**                  | **5.5**        | **10**  |

**Detailed justifications**

**1.1 State of the art — 1.5/3.** Full-credit standard: At least 15 works, each with method, dataset, and result; quantitative comparison of published values with dataset and split for each value. Finding: 15 works are tabulated with approach, data and result, but not every number names its split/partition (Yu et al. 2024: “exact split and averaging unspecified”).

Details: • Table 1, row “Yu et al. 2024”: the split is stated as “exact split and averaging unspecified”. Under the rubric, every number must name both dataset and split. Either find the split in the paper (Yu et al., EMNLP 2024, Section 4) or drop the number. • Table 1 gives split ratios but not the partition the number comes from in several rows: Potthast et al. 2016 (“random 2:1”), Wei and Wan 2017 (“random 3:1”), Andjelić et al. 2025 (“80/10/10”) and Michaluk et al. 2026 (“random 80/10/10”). State “test” explicitly. For Michaluk et al., the 0.864 → 0.909 values are from the ablation (Table 4 of the paper) on the title-only, balanced 20,000/20,000 sample, test partition. • Table 1, row “Clickbait Challenge 2017”: “Self-attentive BiGRU… MSE .033; F1 .683” is the winning system zingel by Zhou (2017), not a result of the overview paper. Cite Zhou (2017) for the system, and the overview only for the benchmark. • “Reported F1” mixes conventions (positive-class F1 against truthClass in the Webis challenge, weighted F1 in Biyani, macro-F1 in RoCliCo/Yi). Add a column for the averaging type. Your primary metric is macro-F1, and only three rows report it. • The SOTA prose (Section 1, p. 1) is one paragraph and cites only 6 of the 15 works (Guo et al. is cited later, in Section 4). Anand, Wei and Wan, the Challenge overview, Indurthi, Yi, Yu, Andjelić and Wang are never cited in the text and appear only as names in the table. For Phase 2, add one or two sentences per work in the text on what each contributes to your question. • No cited work studies temporal or source shift in classification, which is now the core of your design (Section 4). Only RoCliCo (publisher-disjoint test) touches it. See “Works to add”. • Good: the 15 rows, each state approach, data and outcome. The caption honestly warns that the scores cannot be ranked, and the numbers I checked match the sources.

**1.2 Datasets and their status — 1.5/3.** Full-credit standard: For each dataset: size, labels, numeric class balance, licence, acquisition, readiness; collection quantity, date and annotator(s) where applicable. Finding: Webis-17 is fully described. Webis-16 (TO COLLECT) has no licence and no source/access route, and the RESTRICTED official test set is not labelled.

Details: • Webis-Clickbait-16 (Section 2, “External corpus — TO COLLECT”): no licence is stated (“verify its permitted reuse terms”), and you do not say where or how it will be obtained (URL/record). Size, label definition (three-annotator majority), class balance (767/2,992), deadline (20 November) and owner (Adam, supported by Igor) are given. Put the licence and access route in the next version. • The official Webis-17 test set (18,979 posts, labels only via TIRA) is not given a status label. Label it RESTRICTED and state that you will not use it, since your Table 1 quotes results on it. • Label definition: you say you “preserve official binary labels”, but you never state the rule that maps the five annotator ratings to truthClass. The topic card asks you to freeze this rule. Write it down (which field, which threshold), and say whether you will also use truthMean. • Class balance per split: only the global figure is given (4,761/19,538 = 24.37%; 4,529/19,073 after deduplication). Your temporal protocol depends on monthly sizes. Give posts and positive rate per month (Dec–Apr), and the size of the April test set, before freezing the protocol. • Good: the audit (Section 2, p. 2) is concrete and verifiable. It covers the ID join across differently ordered files, 54 empty teasers, 411 duplicate occurrences, timestamps, absent publisher IDs and the Zenodo CC BY 4.0 licence, which I confirmed on the Zenodo record.

**1.3 Solution concept and plan — 1/2.** Full-credit standard: One pipeline figure; evaluation metrics chosen in advance; two or three concrete deliverables; weekly task/owner plan. Finding: One pipeline figure (Fig. 1), macro-F1 fixed as the primary metric, three deliverables, and a week-by-week plan with named owners (Tables 2–3).

Details: • No added value is explained in the methodology above, other than the research and source code, which are the same; still, I do not know of any feature list different from other source codes. Then the methodology seems to rely on previous experiments with possibly slightly different models, which is definitely not what we expect in MSc-level data science projects.

 Remaining weaknesses to fix in Phase 2: • The hypothesis rests on “twelve fixed cues”, but the cues are never listed (Section 3 names only feature families). List all twelve with their exact definitions and lexicons before any result exists. Otherwise “prespecified” cannot be checked. The card’s cues include numerals and superlatives, and neither appears in your families. • Section 4: “three fixed random grouped splits” — grouped by what? Publishers are absent. State the grouping key (e.g., duplicate cluster). • The three expanding-origin runs (test months Feb, Mar, Apr) need a minimum test-month size. The card asks you to specify the minimum eligible group size. • Table 3 (weekly plan) is never referenced in the text, and several rows have “All” as owner. Name one accountable person for joint rows, as you did in Table 2.

**Major concern: Insufficient independent research contribution**

Although the report demonstrates familiarity with relevant literature and provides a reasonably structured experimental plan, the proposed work relies heavily on reproducing existing implementations with relatively minor changes to the models. Reproducing published results is a useful starting point, but it does not, by itself, constitute a sufficiently substantial research contribution for an MSc-level course. The project needs to demonstrate what new scientific question is being investigated, how the experimental design goes beyond existing studies, and what new evidence or insight the results are expected to provide. For Phase 2, the team should clearly distinguish reproduced baselines from its own contribution, formulate testable hypotheses about temporal distribution shift, introduce meaningful experimental controls, and conduct systematic error analysis. Simply replacing models in an existing pipeline will not be sufficient.

**1.4 Text quality and references — 0.5/1.** Full-credit standard: Scientific language and defined abbreviations; accurate published-version citations; fewer than one-third preprint-only references. Finding: References are real and only 2/15 are preprint-only, but many abbreviations are never defined (TF–IDF, MSE, ECE, BiGRU, PoC, MR, EDA, CI…).

Details: • Undefined abbreviations (examples): TF–IDF (abstract, Section 3), MiniLM, ROC-AUC, MSE, BiLSTM, BiGRU, SVM, XGBoost, ECE (Table 1), SQuAD2, SST-2, SentEval, EDA, PoC, MR, CI (Table 3), Q&A, PMLR. LR and CV are defined, but only in the captions. Define each at first use in the text, or add a short abbreviation list. • References: 15 in total. 2 are preprint-only (Potthast et al. 2018b, arXiv:1812.10847; Michaluk et al. 2026, arXiv:2602.18171), which is under one-third. I found no arXiv citation of a work that has a published version. All works exist. Add DOIs.

**1.5 Data statement — 1/1.** Full-credit standard: Data source, licence, personal-data status and concrete handling safeguards. Finding: Source, CC BY 4.0 licence, personal-data content (names, handles, links) and mitigations are all stated (Section 6).

Details: • Full credit is awarded. To keep it in Phase 2, add the Webis-16 licence and source once verified, and state whether the released split manifests contain tweet IDs only or text.

**Strengths, weaknesses, and methodological observations**

WHAT DESERVES PRAISE (not scored): Unusually good preliminary data audit for Phase 1, with concrete counts rather than assuming benchmark cleanliness.

EXPERT NOTE / RISK (not scored): Praise: independently checked 2017 dataset joins, duplicates and class prevalence. | Scope caveat: 2016–2017 collections test historical domain differences, not transfer to the contemporary web without a newer evaluation corpus.

Assessment summary: All five conditions of acceptance are met, so the report is accepted for grading; restore the template attribution line that was deleted. The most important problem is that the SOTA table (Table 1) does not name the evaluation partition for several numbers (Yu et al. 2024 explicitly has no split) and attributes the Clickbait Challenge winner to the overview paper instead of to Zhou (2017). The most important fix is to rebuild Table 1 so that every number carries dataset, split and partition (test/dev), with the original system paper cited, and to list the twelve cues by name.

**Required revisions and priority actions for Phase 2**

1\)               Rebuild Table 1 so that every number names dataset, split and partition (test/dev) and the averaging type (positive-class / macro / weighted). Resolve or remove the Yu et al. 2024 number, and cite Zhou (2017) for the Clickbait Challenge row. This table is the basis of the extended SOTA table required for criterion 2.5; add the works listed above, especially work on temporal/source shift.

2\)               List the twelve cues with exact definitions and lexicons, and freeze them before running system C. **Also, prove what is different; just copying features from previous works will not be accepted as a well-graded deliverable.**

3\)               Complete the Webis-16 entry (licence, access route), label the TIRA test set RESTRICTED, and state the ratings-to-truthClass rule.

4\)               Report posts and positive rate per month and per split. Fix a minimum test-month size, and say what happens if a month falls below it.

5\)               Define the grouping key of the “random grouped” splits.

6\)               Define all abbreviations at first use. Add DOIs to the references and restore the template credit line.

7\)               Make Table 4 specific: concrete tasks per person instead of duplicated generic entries.

8\)               Add an audit of cross-source duplicates between Webis-16 and Webis-17 before any comparison, and document why publisher identity cannot be preserved (Section 2, p.1-2).

9\)               Phase 2 requires a rebuttal that answers every point of this feedback and says where in the revised report it was addressed (criterion 2.4), together with the extended SOTA table (criterion 2.5).

Further actions raised in the parallel review:

1\)               Document the second corpus licence and exact date/version of retrieval before including it.

2\)               Preserve source/publisher identity and dates in splits where available; audit cross-source duplicates before comparisons.

3\)               Report calibration and prevalence-dependent metrics as well as macro-F1.

**Alignment with the assigned project topic (formative, not an additional Phase 1 deduction)**

• Research question: the card asks about publisher-held-out macro-F1. The team verified that the labelled release has no publisher IDs and switched to the card’s own Plan B (time-held-out). This narrowing is justified and stated explicitly (abstract, Section 2). The falsification criterion (gains vanish after deduplication or are confined to random tests) mirrors the card. • The seed publication (Michaluk et al. 2026), which is also the comparison point, is cited and its numbers are in Table 1. Explain how your controlled B-vs-C comparison differs from their XGBoost ablation, where the embedding width also changes (as your own Table 1 row notes). • Data-readiness labels: READY and TO COLLECT are used. RESTRICTED (the TIRA test set) is missing. • Baselines 1 and 2 and the proposed system match the card. The card’s metrics are covered (macro-F1, PR ranking via average precision, calibration, random-vs-held-out gap), except per-publisher F1, which is impossible without publisher IDs; say so. • Deliverables: card D1 (deduplicated loader, metadata audit, split manifest) and D2 (three-system ablation, held-out evaluation, ≥12 errors; you plan 20) are planned. Optional D3 (headline inspector) is not planned, which is acceptable. • Out of scope is respected (Section 5 excludes spoiler generation, browser extension, multilingual modelling and live scraping). • Sibling teams: none.

**Questions to answer in the Phase 2 rebuttal**

1.               Which publisher/date and near-duplicate checks prevent a spurious temporal-shift effect?

2.               What later evaluation corpus is available to test transfer beyond the historical 2016–2017 collection?

**Additional methodological validity checks (formative, not scored in Phase 1)**

Additional evidence to seek Phase 2 (not part of the Phase 1 grade): Create a temporal leakage and duplicate-audit protocol transferable to other news corpora.

**Formal completeness and submission issues**

The required formal elements were reviewed. Final confirmation remains with the responsible supervisor.

Evidence recorded during the independent review:

• Contribution table: present-complete — Table 4 (p. 4) lists all four members, tasks and 4 hours each. The entries are generic and pairwise identical (Igor = Hubert, Adam = Mateusz): name concrete outputs per person (which papers, which audit script). • LLM-use declaration: present-complete — Section 6, p. 3: ChatGPT (OpenAI) and Perplexity, used for literature discovery, initial synthesis and copyediting. Add model versions and keep the prompts, as the topic card requires. • Folder naming: compliant — Folder Kolodziej_Kowalski_Kaniasty_Iwaniuk matches the four authors on p. 1 (Kołodziej, Kowalski, Kaniasty, Iwaniuk). • Template: compliant (with remark) — acl2015.sty two-column layout with the course title line “Project Proposal for NLP, Winter 2026/27”. The template credit line “Template: Anna Wróblewska (Warsaw University of Technology), adapted from the ACL 2015 conference formatting template” was deleted under the title. Restore it. • Deadline (4.11): on time — Committed 3.11, 22:23 CET.

**Proposed exceptional-research recognition: 0/1.** This optional point is not a deduction and does not change the /10 score; it is awarded only for a completed, verifiable contribution beyond the core rubric.

**Suggested literature and bibliographic checks for Phase 2**

The entries below are suggestions from an independent bibliographic review. Verify all metadata and the suitability of each source against the original publication before citing it.

1\)               Yiwei Zhou. 2017. Clickbait detection in tweets using self-attentive network. arXiv:1710.05364. https\://arxiv.org/abs/1710.05364 — This is the actual source of the “Clickbait Challenge 2017” row (zingel) in your Table 1; cite it for that number.

2\)               Abhijnan Chakraborty, Bhargavi Paranjape, Sourya Kakarla, Niloy Ganguly. 2016. Stop Clickbait: Detecting and preventing clickbaits in online news media. ASONAM 2016, pp. 9–16. doi:10.1109/ASONAM.2016.7752207 — The headline dataset behind Anand et al. (2017) and part of the seed paper’s mixed corpus; you need it to explain why random-split scores of 0.98 are not comparable with Webis-17.

3\)               Anders Søgaard, Sebastian Ebert, Jasmijn Bastings, Katja Filippova. 2021. We need to talk about random splits. EACL 2021, pp. 1823–1832. doi:10.18653/v1/2021.eacl-main.156 — Direct methodological support for your random-versus-held-out gap analysis.

4\)               Paul Röttger, Janet B. Pierrehumbert. 2021. Temporal adaptation of BERT and performance on downstream document classification: Insights from social media. Findings of EMNLP 2021, pp. 2400–2412. doi:10.18653/v1/2021.findings-emnlp.206 — Measures temporal shift in social-media text classification, the setting you have now adopted.

5\)               Shrey Desai, Greg Durrett. 2020. Calibration of pre-trained transformers. EMNLP 2020, pp. 295–302. doi:10.18653/v1/2020.emnlp-main.21 — Calibration of transformer-based text classifiers in and out of domain; closer to your setting than Guo et al. (2017).

6\)               Soveatin Kuntur, Panca D. Ningrum, Anna Wróblewska, Maria Ganzha, Marcin Paprzycki. 2026. Clickbait detection: Quick inference with maximum impact. LNCS, pp. 33–40. doi:10.1007/978-3-032-29909-3_3 — Recent lightweight clickbait detection from the seed paper’s group, relevant to your low-cost-cue framing.

For Phase 2, respond point by point to the substantive feedback and questions, indicating whether each item was corrected, rejected with justification, or deferred. Refer to the corresponding section, table, figure, code file or experiment. Additional advice above does not retroactively reduce the Phase 1 core score.

Best regards, Anna Wróblewska