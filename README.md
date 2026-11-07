# NLP-2026W

The repository for open source solutions designed and developed within the NLP course conducted by Anna Wróblewska with Soveatin Kuntur, Filip Kucia, Arkadiusz Modzelewski, Michał Gromadzki @ Faculty of Mathematics and Information Sciences, Warsaw University of Technology.

Project: *Clickbait Without the Click: Linguistic Cues under Temporal Shift*. Implementation tasks and milestones: [`PLAN.md`](PLAN.md).

## Environment setup ([uv](https://docs.astral.sh/uv/))

Dependencies are managed with **uv** (`pyproject.toml` + `uv.lock`), not `requirements.txt`. Python **3.11+** is recommended.

### Install uv

**macOS**

- Official installer (works on Intel and Apple Silicon):

  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

  Then open a new terminal or run `source $HOME/.local/bin/env` (or follow the installer’s PATH hint).

- Alternatively, with [Homebrew](https://brew.sh/): `brew install uv`

**Windows**

- PowerShell (official installer):

  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

  Restart the terminal so `uv` is on your `PATH` (installer adds `%USERPROFILE%\.local\bin` by default).

- Alternatively, with [winget](https://learn.microsoft.com/en-us/windows/package-manager/winget/): `winget install --id=astral-sh.uv -e`

Check the install:

```bash
uv --version
```

### Install project libraries

From the repository root:

```bash
cd NLP-2026W
uv sync
```

This creates a local `.venv`, resolves dependencies from `uv.lock`, and installs them into that environment.

Run commands inside the project environment without activating the venv:

```bash
uv run python -c "print('ok')"
```

Optional: activate the venv manually — **macOS/Linux:** `source .venv/bin/activate` · **Windows (cmd):** `.venv\Scripts\activate.bat` · **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`

**Add or update a dependency** (team workflow):

```bash
uv add scikit-learn          # example: adds to pyproject.toml and refreshes uv.lock
uv sync                      # after pulling someone else's lockfile changes
```

Pin versions for reports by citing the lockfile (`uv.lock`) and `uv pip freeze` or `uv export --format requirements-txt` when needed.

Verify the project scaffold:

```bash
uv run python scripts/smoke_config.py
```

## Data: Webis-Clickbait-17

Primary corpus for all experiments. **`data/raw/` is gitignored** — each clone must download the archive locally. Processed tables and split manifests in the repo were built from this release; re-run the scripts below to reproduce them bit-for-bit.

### 1. Download

- **Record:** [Zenodo 5530410 — Webis-Clickbait-17](https://zenodo.org/records/5530410) (CC BY 4.0)
- **File:** `clickbait17-train-170630.zip` (~937 MB) — labelled training/validation JSONL, not the multi-part archive dumps

Direct API link (same file):

```text
https://zenodo.org/api/records/5530410/files/clickbait17-train-170630.zip/content
```

**macOS / Linux** (from repository root):

```bash
mkdir -p data/raw
curl -L -o data/raw/clickbait17-train-170630.zip \
  "https://zenodo.org/api/records/5530410/files/clickbait17-train-170630.zip/content"
```

**Windows (PowerShell)** from repository root:

```powershell
New-Item -ItemType Directory -Force -Path data/raw
curl.exe -L -o data/raw/clickbait17-train-170630.zip `
  "https://zenodo.org/api/records/5530410/files/clickbait17-train-170630.zip/content"
```

### 2. Extract JSONL into `data/raw/`

The zip contains a folder `clickbait17-validation-170630/` with large `media/` assets. For this project you only need the two JSONL files at **`data/raw/`** (paths in [`configs/experiment.yaml`](configs/experiment.yaml)):

| Required path | Role |
|---------------|------|
| `data/raw/instances.jsonl` | `postText`, `postTimestamp`, `targetTitle`, … |
| `data/raw/truth.jsonl` | `truthClass`, `truthJudgments`, … (join on `id`) |

**macOS / Linux** — extract without pulling all media into the tree:

```bash
unzip -j -o data/raw/clickbait17-train-170630.zip \
  "clickbait17-validation-170630/instances.jsonl" \
  "clickbait17-validation-170630/truth.jsonl" \
  -d data/raw
```

**Windows** — unzip the archive with Explorer or `tar -xf`, then copy `clickbait17-validation-170630\instances.jsonl` and `truth.jsonl` into `data\raw\`, or use the same `unzip` commands in Git Bash.

Check:

```bash
test -f data/raw/instances.jsonl && test -f data/raw/truth.jsonl && echo "ok"
```

### 3. Build processed dataset and splits

From the repository root (after `uv sync`):

```bash
uv run python scripts/build_dataset.py
uv run python scripts/build_splits.py
```

**Outputs (used by later tasks):**

| Path | Contents |
|------|----------|
| `data/processed/posts.parquet` | Cleaned rows (`post_id`, text, label, timestamps, …) |
| `data/processed/dataset_stats.json` | Row counts after cleaning |
| `splits/*.json` | Train/val/test ID lists (`temporal_main`, random grouped seeds, …) |

Cleaning and leakage rules: [`docs/data.md`](docs/data.md).

### Train system A (Task 4)

After the dataset and splits exist:

```bash
uv run python scripts/train_system_a.py --split temporal_main
```

Writes `results/system_a_<split>.json` (macro-F₁, AP, Brier, confusion matrix; split name in file). Cue definitions: [`docs/cues.md`](docs/cues.md).

Optional secondary corpus (Task 10 / EDA): Webis-Clickbait-16 under `data/raw/webis16/` when available.

### Frozen MiniLM cache (Task 5)

Install the locked environment and run a **64-post `temporal_main` training pilot** to download
the pinned model before measuring the full run:

```bash
uv sync --locked
uv run --locked python scripts/cache_embeddings.py --device cpu --sample-size 64
```

Without `--sample-size`, the script encodes **all processed posts**, including validation/test
texts, using the fixed pretrained encoder. No labels or dataset-fitted statistics enter encoding.
On Linux, measure the complete command with GNU time:

```bash
mkdir -p results
/usr/bin/time -v -o results/embedding_cache_time.txt \
  uv run --locked python scripts/cache_embeddings.py --device cpu --local-files-only
uv run --locked python scripts/cache_embeddings.py --check
```

`--local-files-only` excludes model downloads from this run. GNU time records total process
wall time and peak **host RSS in KiB**, including imports, model loading, token-length auditing,
encoding, verification, and writing. Separate phase timings are in `results/embedding_cache.json`.
These measurements cover cache construction, not LR training or deployment latency. CUDA runs
also record PyTorch peak allocated/reserved device bytes separately from host RSS.

The [recorded CPU run](results/embedding_cache.json) covers all **18,682 processed Webis-17 posts**
on an AMD Ryzen 7 5700U with 8 PyTorch threads and batch size 32. It took **55.34 s total wall time**,
including **49.23 s encoding**, with **1,347,620 KiB peak host RSS** ([GNU time log](results/embedding_cache_time.txt)).
These are single-run measurements with the model already downloaded. All six manifests are covered;
the longest teaser uses 104 tokens including special tokens, so none reaches the 256-token limit.

The model revision and encoding settings are pinned in [`configs/experiment.yaml`](configs/experiment.yaml).
The first run downloads the model into `cache/models/`. Encoding uses frozen float32 weights,
the existing `post_text` without additional cleaning, a 256-token maximum, and unit-normalized
384-dimensional sentence embeddings. Labels and article fields are not passed to the encoder.

Full-cache outputs under **`cache/embeddings/`** (gitignored):

- `embeddings.npz`: aligned string `post_ids`, `text_sha256`, and float32 `embeddings`.
- `meta.json`: model revision, encoding settings, hardware, installed versions, code revision,
  source/config/lockfile/archive checksums, split coverage, token-length audit, and verification results.

The script verifies finite float32 values, dimensions, unit norms, exact save/load equality, and
five seeded direct re-encodings with batch size 1 (`atol=1e-6`, `rtol=1e-5`). A small summary is
written to `results/embedding_cache.json`; retain it with the GNU time log for the report.
Pilot runs stay in `cache/embeddings/pilot/` and never overwrite the full cache.

`clickbait.embeddings.load_embeddings(directory, posts, cfg)` takes a table with `post_id` and
`post_text`, returns vectors in that table's order, and checks the model/revision, sequence limit,
normalization setting, dimensions, dtype, IDs, text fingerprints, and archive integrity. B and C
must load the same archive. Package versions and batch size are recorded as provenance; loading
saved arrays does not require matching the encoding machine or its inference batch size.

`--check` validates the existing artifact without loading MiniLM or downloading anything. It
checks every current split manifest for covered IDs and nonempty, disjoint partitions. This is
an ID-coverage check, not a new article-leakage audit. Split changes alone allow reuse of unchanged
ID–text vectors; saved manifest hashes describe the original run. Check a pilot with
`--check --sample-size 64`.

To transfer the full cache, copy `embeddings.npz` and `meta.json` together into the recipient's
`cache/embeddings/`, then run the documented `--check` command against the same processed dataset
and configuration. Large artifacts remain outside git.

Run the tests without downloading a model:

```bash
uv run --locked python -m unittest discover -s tests -v
```

### B/C feature construction (Task 6)

`clickbait.models.neural.load_neural_inputs(posts, cache_dir, cfg, system)` preserves the
requested post order and loads cached embeddings as contiguous float64 arrays. B has 384
embedding columns. C appends twelve **unscaled** cues in `CUE_NAMES` order, giving 396 columns.

For C, `build_cue_scaler()` creates a scikit-learn `ColumnTransformer` that passes through the
embedding columns and applies `StandardScaler` only to the cue columns. Fit it on training
inputs with `fit_transform`, then use that same object's `transform` on validation/test inputs.
Constant training cues are retained. The embedding values are identical in B and C.
Cue matching semantics are documented in [`docs/cues.md`](docs/cues.md).

Check feature construction on the real training/validation partitions without fitting LR or
reading test labels:

```bash
uv run --locked python scripts/check_neural_features.py --split temporal_main
```

Verified shapes for `temporal_main`: training B `(11184, 384)` and C `(11184, 396)`;
validation B `(3918, 384)` and C `(3918, 396)`. Checks cover finite float64 values,
embedding equality, and standardized training cues.

### B training and validation (Task 6)

With the full embedding cache available, run B on CPU:

```bash
uv run --locked python scripts/train_neural.py --system B --split temporal_main
```

The runner uses the manifest's training and validation rows only: December–February for
fitting and March for selecting the LR regularization strength. It draws the same 25
log-uniform `C` values in `[0.01, 100]` as A, using seed 42, and selects the highest validation
macro-F₁. Exact ties keep the first sampled candidate. The selected classifier is refitted
on training data only, with `class_weight='balanced'` and the default 0.5 decision threshold.

Outputs:

- `results/system_b_temporal_main_validation.json`: validation metrics, all candidate scores,
  convergence status, iteration counts, fit times, configuration, versions and input hashes.
- `results/runs/b_temporal_main_validation/model.pkl`: fitted LR classifier, taking the 384
  cached embedding columns as float64. Reload with `pickle.load` in the locked environment.
- `results/runs/b_temporal_main_validation/validation_predictions.parquet`: manifest-ordered
  `post_id`, `partition`, `y_true`, `y_pred` and `p_clickbait` columns.

Model and prediction files are gitignored. Each invocation replaces these split-specific
outputs. A nonconverged candidate aborts the search and writes its diagnostic history to
`results/runs/b_temporal_main_validation/tuning_failure.json`; no partial winner is selected
or new success artifacts written. Resolve the warning and rerun the complete search. Any
increase of `logistic_regression.max_iter` belongs in the shared configuration for A/B/C.
The final refit also fails on a convergence warning.

Measure the complete validation run, including loading and artifact export, with:

```bash
/usr/bin/time -v -o results/system_b_temporal_main_validation_time.txt \
  uv run --locked python scripts/train_neural.py --system B --split temporal_main
```

These are model-selection results on March validation. C training and the frozen April
test comparison remain later steps of Task 6; the runner currently accepts only `--system B`.

Further model and experiment reproduction steps will be added in [`PLAN.md`](PLAN.md) Task 10.
