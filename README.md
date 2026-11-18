# Clickbait Without the Click

English clickbait detection under chronological evaluation. The presentation checkpoint compares word/character TF–IDF, frozen MiniLM embeddings, and the same embeddings plus twelve linguistic cues. All use balanced logistic regression with a shared validation-selected regularization grid.

The working branch is `feat/poc`. See [PLAN.md](PLAN.md) for the smaller presentation checkpoint and remaining project work, and [presentation/PLAN.md](presentation/PLAN.md) for the ten-minute video storyboard.

## Setup

Use Python 3.11+ and [uv](https://docs.astral.sh/uv/). Dependencies are pinned in `uv.lock`.

```bash
uv sync --locked
uv run --locked python scripts/smoke_config.py
```

## Data

Download the public Webis-Clickbait-17 labelled training archive, not the restricted challenge test. Source: [Zenodo record 5530410](https://zenodo.org/records/5530410), `clickbait17-train-170630.zip`, CC BY 4.0. The archive is about 937 MB; extract only its two JSONL files. Raw data and caches are gitignored.

```bash
mkdir -p data/raw
curl -fL --retry 2 -o data/raw/clickbait17-train-170630.zip \
  https://zenodo.org/api/records/5530410/files/clickbait17-train-170630.zip/content
unzip -j data/raw/clickbait17-train-170630.zip \
  'clickbait17-validation-170630/instances.jsonl' \
  'clickbait17-validation-170630/truth.jsonl' -d data/raw
```

The repository includes the processed pilot table and existing main split. The PoC independently rebuilds cleaning from raw inputs and rejects a processed table that differs. It records the 54 empty, 411 repeated-teaser and 391 repeated-title exclusions in an ID-only ledger. Final pilot size is 18,682, with 4,448 positive labels. Official `truthClass` is the target; annotation ratings support interpretation only.

Cleaning details: [docs/data.md](docs/data.md). The current checkpoint checks exact teaser/title overlap and chronological months. Article titles are imperfect identity proxies, and the full near-duplicate audit remains future work. Publisher IDs are unavailable.

## Frozen embedding cache

```bash
uv run --locked python scripts/cache_embeddings.py --device cpu
uv run --locked python scripts/cache_embeddings.py --check
```

The first command downloads the pinned `sentence-transformers/all-MiniLM-L6-v2` revision, creates unit-normalized 384-dimensional vectors and records encoding metadata. It encodes text without labels or dataset-fitted statistics. To reuse the team cache, copy both `embeddings.npz` and `meta.json` into `cache/embeddings/`, then run `--check`. IDs, text fingerprints, encoder settings and archive checksums must agree. For a small training-only encoding check, use `--sample-size 64`; this does not replace the full cache.

## Reproduce one PoC result

After setup, raw-data extraction and cache creation, run:

```bash
uv run --locked python scripts/run_poc.py --output results/poc/local
uv run --locked python scripts/run_poc.py --verify results/poc/local
```

The pinned presentation result lives in `results/poc/main/`; `local` is a fresh reproduction directory. Use another new name for additional runs; existing results are not overwritten. The runner uses `temporal_main`: December 2016–February 2017 training (11,184 posts), March validation (3,918), April test (3,580, including 830 positives). It selects `C` from `[0.01, 0.1, 1, 10, 100]` by validation macro-F₁, resolves ties with smallest `C`, refits on training only and uses the default 0.5 decision rule. Vocabulary/IDF and cue scaling are fitted on training rows only. Nonconvergence aborts the run.

Systems:

- **A:** word 1–2 and character 3–5 TF–IDF + L2 logistic regression.
- **B:** frozen MiniLM + the same LR family.
- **C:** B's identical embedding coordinates + twelve train-standardized cues + LR.

Cue definitions and exact lexicons: [docs/cues.md](docs/cues.md). All twelve cues use teaser text only and form four families of three.

Outputs include a data audit/ledger, pre-scoring protocol snapshot, all candidate validation scores, test metrics and ID-aligned predictions, measured timings/peak host RSS, and presentation charts/tables/examples. Large fitted pipelines live in documented gitignored storage under `results/runs/`. The verifier checks frozen inputs/models and recomputes predictions and metrics without fitting.

Runtime and memory measurements describe the current process/hardware. Distinguish cache construction, model selection/training and test inference when citing cost. Shared-process peak RSS is not a separate per-model memory estimate. Run times can vary across machines.

## Presentation

The editable reveal.js deck and two-person script live in [presentation/](presentation/). Its README explains rendering, presenting and recording the ten-minute video. Main slides distinguish observed pilot results from future hypotheses. The script includes slide timings and the presenter handoff.

The video covers the problem, revised SOTA, methodology, working PoC, preliminary findings and next steps. It supports the 25 November Q&A and 2 December assessed Phase 2 submission. Contribution hours, formal LLM declaration and full report/rebuttal requirements remain team submission responsibilities.

## Tests

```bash
uv run --locked python -m unittest discover -s tests -v
```

Tests cover cue rules, cache alignment/compatibility, training-only transforms, the fixed selection grid, exact data auditing, frozen evaluation and presentation artifact alignment. They require no model download. The real-data PoC and verifier provide integration evidence beyond these fixtures.

## Scope and interpretation

This checkpoint runs one main chronological window. A positive C−B point estimate does not establish significance, robustness across months or publisher generalization. April had an earlier pilot evaluation, which must be disclosed. No current model predicts factual truth or observed click rates.

Other temporal windows, grouped-random diagnostics, four family ablations, paired uncertainty, detailed calibration/error analysis, matched teaser–article context models and external Webis-16 evaluation remain later work. Jeff and YouTube are optional. Historical results and snapshots under `results/` retain their original definitions; reproducing those hash-frozen experiments requires their recorded historical code/configuration, rather than the current cue extractor.

Course repository: [grant-TraDA/NLP-2026W](https://github.com/grant-TraDA/NLP-2026W), GNU GPL v3. Team: Igor Kołodziej, Hubert Kowalski, Adam Kaniasty and Mateusz Iwaniuk. Supervisor: Anna Wróblewska.
