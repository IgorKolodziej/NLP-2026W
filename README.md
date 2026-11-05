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

### MiniLM cache pilot (Task 5)

The first cache increment encodes a seeded sample of **64 `temporal_main` training posts** on CPU:

```bash
uv sync --locked
uv run --locked python scripts/cache_embeddings.py --device cpu --sample-size 64
```

The model revision and encoding settings are pinned in [`configs/experiment.yaml`](configs/experiment.yaml).
The first run downloads the model into `cache/models/`. Encoding uses frozen float32 weights,
the existing `post_text` without additional cleaning, a 256-token maximum, and unit-normalized
384-dimensional sentence embeddings. Labels and article fields are not passed to the encoder.

Outputs under **`cache/embeddings/pilot/`** (gitignored):

- `embeddings.npz`: aligned string `post_ids`, `text_sha256`, and float32 `embeddings`.
- `meta.json`: model revision, sample seed/scope, encoding settings, installed versions,
  source/lockfile/archive checksums, and model-loading and encoding times.

The script verifies exact save/load equality. `clickbait.embeddings.load_embeddings(directory, posts)`
accepts a table with `post_id` and `post_text`, returns vectors in that table's order, and rejects
missing IDs, changed text, or a damaged archive. Re-running replaces the pilot; it does not produce
the full dataset cache. Model-loading time can include the initial download and is separate from
encoding time. Full-cache coverage and runtime/memory measurement remain part of Task 5.

Run the cache tests without downloading a model:

```bash
uv run --locked python -m unittest discover -s tests -v
```

Further model and experiment reproduction steps will be added in [`PLAN.md`](PLAN.md) Task 10.
