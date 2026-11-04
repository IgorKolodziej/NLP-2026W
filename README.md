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

### Webis-Clickbait-17 (Task 2)

Download `clickbait17-train-170630.zip` from [Zenodo 5530410](https://zenodo.org/records/5530410) into `data/raw/`, extract `instances.jsonl` and `truth.jsonl` (see [`docs/data.md`](docs/data.md)). Then:

```bash
uv run python scripts/build_dataset.py
uv run python scripts/build_splits.py
```

Writes `data/processed/posts.parquet`, `data/processed/dataset_stats.json`, and manifests under `splits/`.

Further reproduction steps (models, experiments) will be added in [`PLAN.md`](PLAN.md) Task 10.
