# AGENTS.md — NLP course project (2026/27)

Read this at the start of every conversation. When plan, code, or reports conflict with the proposal, **follow the proposal** unless the team has explicitly changed direction and updated the docs.

## What this repository is

**Course:** Natural Language Processing, winter 2026/27, Data Science MSc, WUT (FMiI). Teaching team: Anna Wróblewska, Soveatin Kuntur, Filip Kucia, Arkadiusz Modzelewski, Michał Gromadzki. Official course repo: [grant-TraDA/NLP-2026W](https://github.com/grant-TraDA/NLP-2026W) (GNU GPL v3).

**Team:** Igor Kołodziej, Hubert Kowalski, Adam Kaniasty, Mateusz Iwaniuk. Supervisor: Anna Wróblewska.

**Topic:** *Clickbait Without the Click: Linguistic Cues under Temporal Shift* — binary clickbait detection on English social-media teasers (`postText` → `truthClass`), not factual verification or click counts.

**Research question:** Does a fixed set of **twelve linguistic cues** improve **macro-F₁** out-of-time vs. the **same** frozen `all-MiniLM-L6-v2` embeddings + logistic regression (paired **C − B**)?

**Primary systems (shared splits, same LR family, `class_weight='balanced'`):**

| ID | Model |
|----|--------|
| A | Word (1–2) + char (3–5) TF–IDF + L2 logistic regression |
| B | Frozen MiniLM embeddings + LR |
| C | B’s cached embeddings + twelve cues + LR |

**Data:** Primary — Webis-Clickbait-17 (19,538 labelled posts; join labels by ID). No publisher IDs → **temporal** held-out evaluation (not unseen-publisher claims). Deduplicate empties/repeated teasers and audit article overlap. Secondary — publicly available Webis-Clickbait-16, evaluation only after local schema/overlap checks. The official Webis-17 challenge test is restricted and excluded.

**Stack:** Python **3.11+** via **[uv](https://docs.astral.sh/uv/)** (`pyproject.toml`, committed `uv.lock`); scikit-learn, sentence-transformers, PyTorch, NumPy, matplotlib. Install with `uv sync`; run tools with `uv run …`. Do not add `requirements.txt`. CPU OK for linear models; optional GPU for one-time embedding cache.

**Full-project secondary experiment:** matched teaser/title/96-word-lead A_ctx/B_ctx/C_ctx/D_ctx models and three relation cues; separate from primary A/B/C. Jeff and YouTube evaluation are optional. These are outside the immediate PoC.

**Out of scope:** spoiler generation, factual verification, multilingual work, browser extensions, live scraping.

**Ground truth:** [`NLP_Proposal_v4-1.tex`](NLP_Proposal_v4-1.tex) — hypotheses, pipeline, exact twelve-cue specification, evaluation, deliverables and limitations. Earlier code/results follow the original proposal and remain historical artifacts. Extend or deviate only with explicit justification in phase reports.

**Immediate delivery:** the presentation PoC on branch `feat/poc`, as scoped in [`PLAN.md`](PLAN.md): one temporal window, A/B/C, exact data checks, basic EDA and slide-ready artifacts. Use plain filenames without proposal-version suffixes. Full robustness/ablations/context/external studies remain later work. April was scored in an earlier pilot; disclose this prior exposure.

**Implementation plan:** [`PLAN.md`](PLAN.md) — phased tasks, executors, human run steps. After finishing a PLAN task (merged work), **update the Progress checkboxes in `PLAN.md`** so team status stays accurate.

**Authoritative course docs (full detail):**

- [`Project rules 2026-27.docx`](Project%20rules%202026-27.docx) — schedule, deadlines, submission rules, passing conditions
- [`Assessment criteria 2026-27.docx`](Assessment%20criteria%202026-27.docx) — what is graded and how (full/half/0)

## Workstreams (accountable owner → support)

| Workstream | Owner | Support |
|------------|-------|---------|
| Data and protocol | Adam | Igor |
| Classical NLP and cues | Hubert | Adam |
| Neural NLP and hybrid | Igor | Mateusz |
| Evaluation and analysis | Mateusz | Hubert |

## Milestones (project deadlines)

| When | Deliverable |
|------|-------------|
| 4 Nov | Phase 1 — proposal + SOTA (10 pts) |
| 18 Nov | Mid-term presentation + 10 min video (SOTA + PoC) |
| 25 Nov | Mid-term Q&A — prepared questions for other teams (individual, §5a) |
| 2 Dec | Phase 2 — EDA + PoC, MR, revised report, rebuttals (20 pts) |
| 13 Jan 2027 | Phase 3 — final report, presentation video, MR (30 pts) |

Proposal weekly targets: see the revised proposal's weekly table and the immediate PoC delivery scope in `PLAN.md`.

## Grading mindset (checkpoints and final)

**Core total: 100 pts** — project phases 1–3 (60), survey presentation/tutorial (10), tutorial exercises (20), Q&A questions up to 5. Bonus notebook exercises up to +5 do not change pass thresholds.

**Passing requires more than points:** ≥ **30/60** project phase points; **contribution table** (tasks + hours, consistent with git) in **every** phase report; **LLM-use declaration** every phase; milestone folder named `surname_surname_surname_surname` (order fixed at Milestone 1). Missing contribution table or LLM declaration → report **not accepted** (0 for that phase until fixed).

**Scoring:** Each listed criterion is **full / half / 0** unless noted (Q&A: 0.5 pt per unique reasonable question, max 5). Nothing is graded that is not in the assessment criteria doc.

### Phase 1 (10) — already submitted; keep aligned for later phases

SOTA table (≥15 works, dataset + split per number), dataset readiness labels, pipeline figure + metrics chosen upfront, week plan with owners, data statement, references quality.

### Phase 2 (20) — PoC and EDA checkpoint

- **2.1** End-to-end PoC on real data with a **number** (code-only or number-only → half).
- **2.2** EDA: labels, length, duplicates, **leakage across splits**, compare to another dataset or explain why not.
- **2.3** Experiment plan: baselines from **≥2 method classes** (classical / fine-tuned encoder / prompted LLM — map A/B/C accordingly), hyperparameters, splits, metrics.
- **2.4** Rebuttal: every supervisor review **and** meeting #8 Q&A point — fixed/rejected/deferred, with **checkable report location** and concrete fixes.
- **2.6** README: stranger reproduces **one** result from README alone.
- **2.7** Measured runtime and memory (not estimates).
- **2.8** Contribution table — mandatory to pass.

### Phase 3 (30) — final

Results with cross-method interpretation; **measurement procedures** for every number; **reproducibility** (seeds, versions, commands); rebuttal through meeting #13 Q&A; **≥3 runs** with spread or justified exception; **≥20** categorized errors; limitations with consequences; metric choice justified for **~24% positives** (accuracy alone insufficient); captions self-contained; code quality + current README.

**Evaluation plan:** Primary macro-F₁ and paired C−B; main train Dec–Feb / val Mar / test Apr; identical fixed regularization grid selected by validation macro-F₁ for A/B/C; train-only vocabulary/scalers/refit. The twelve cues form four three-feature families defined in Appendix A and `resources/linguistic_cues.json`. Full project adds other temporal/random runs, four family ablations, paired bootstrap, calibration, context analysis and compute cost. PoC exports point estimates and explicitly defers inferential claims.

## Agent behaviour in this repo

### Code and writing style

- **Comments:** sparse and only where logic is non-obvious; always **English**. No banner comments, no step-by-step narration. Avoid long docstrings — a one-line summary at most when a function’s purpose is not clear from its name and parameters.
- **Complexity:** implement like a **data science MSc student** on a course project: straightforward scripts, notebooks, and modules; no extra abstraction layers, design patterns, or “framework” structure unless the task clearly needs it.
- **Submission-ready artefacts:** everything committed (code, notebooks, README, report text, slide notes) must look **student-authored and ready for the instructor**. No meta-commentary about prompts, users, or agents; no TODO filler; no template placeholders (`TBC`, `your name here`, `fix later`); no chatty phrasing (“as requested”, “I updated this because…”).
- **AI attribution in deliverables:** do **not** add disclaimers such as “generated by AI/ChatGPT/Cursor” in code, comments, or prose **unless the team explicitly asks** for that wording. (The course still requires a formal **LLM-use declaration** in each phase **report** — that is separate and mandatory; do not duplicate or parody it elsewhere.)

### Project discipline

1. **Do not invent** datasets, splits, metrics, or scope beyond the proposal without flagging the mismatch.
2. **Name splits** on every reported metric; fit preprocessors on train only.
3. **Reproducibility first:** pin deps in `uv.lock`, record seeds and commands in README or config; MR-style clean code for course submission.
4. **Reports:** contribution table + LLM declaration + data statement every phase; rebuttals cite section/table/figure.
5. **Submissions:** correct template; folder naming rule; one free ≤48 h late delay per semester then −5 pts per further delay.
6. Prefer **minimal, focused diffs**; match existing conventions as the codebase grows.
7. When executing a task from [`PLAN.md`](PLAN.md), mark the corresponding **Progress** item complete in that file before closing the session (same PR/commit as the task if practical).
8. **Git commits:** use plain commit messages only — **never** add `Co-authored-by`, `Made-with: Cursor`, or other agent/cursor attribution trailers to commits.

## Pre-submit self-check (team)

Contribution table · LLM declaration · reproducible README · measured runtime/memory · split named on every table number · published versions cited · data statement · rebuttals complete · template + folder naming · temporal/leakage story consistent with proposal
