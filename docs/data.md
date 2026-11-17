# Webis-Clickbait-17 (training release)

Source: Zenodo record [5530410](https://zenodo.org/records/5530410), file `clickbait17-train-170630.zip` (CC BY 4.0). After unzip, labelled JSONL lives under `clickbait17-validation-170630/`; we copy `instances.jsonl` and `truth.jsonl` to `data/raw/`.

## Join

- **Instances** (`instances.jsonl`): `id`, `postText` (list of strings), `postTimestamp`, `targetTitle`, `targetParagraphs`, …
- **Truth** (`truth.jsonl`): `id`, `truthClass` (`clickbait` / `no_clickbait`), `truthJudgments`, …
- Join on `id` (row order differs between files).

## Cleaning (see `src/clickbait/dataset.py`)

1. Drop rows with empty teaser text after normalizing `postText`.
2. **Teaser dedupe:** normalize teaser (lowercase, collapse whitespace); keep the row with the **earliest** `postTimestamp`.
3. **Article overlap:** `article_group_key` = normalized `targetTitle`, or the instance `id` if the title is empty. Keep the **earliest** post per `article_group_key` so no normalized title group crosses splits. Titles are a proxy for article identity: one article with different titles may remain, while distinct articles with the same title may be merged.

## Splits

- **Temporal:** calendar month from `postTimestamp` (UTC). Three expanding train windows; main manifest `temporal_main` = train Dec–Feb, val Mar, test Apr 2017.
- **Random grouped:** group key = `article_group_key` (same as cleaning); stratified 70/15/15 train/val/test; seeds 42, 43, 44. No group crosses partitions.

The immediate PoC uses only `temporal_main`. Existing random manifests are historical diagnostics, not newly rerun results. The full plan replaces their ratios with the main temporal proportions and uses majority group labels.

## PoC audit

`scripts/run_poc.py` validates unique raw IDs and matching instance/truth ID sets, rebuilds the existing cleaning policy, and compares its retained IDs/text/labels with the processed pilot. Its ID-only `exclusion_ledger.csv` records each row's stage, reason and representative. The verified stages are 19,538 raw, 54 empty removals, 411 repeated-teaser removals, 391 repeated-title removals, and 18,682 retained (4,448 positive).

Main-window checks validate disjoint IDs, exact normalized teaser/title overlap, expected months and minimum April test size 1,000. These do not certify near-duplicate or publisher independence. Cross-corpus auditing and development-reviewed near-duplicate thresholds belong to later experiments.

The official published `truthClass` is the training target. The proposal documents its five-annotator construction; no `truthMean` threshold replaces it. `truthJudgments` support interpretation of disagreement. The raw loader also retains `truthMean` and paragraphs for later work, while the existing processed pilot is kept unchanged for this teaser-only checkpoint.

The official additional Webis-17 challenge test is restricted through TIRA and is not used. Webis-16 is publicly available from Zenodo record 3251557 (CC BY 4.0), but schema compatibility and external evaluation are deferred for this presentation checkpoint. No new personal-data collection or profile enrichment occurs; posts can contain names/handles/links, so exported examples remain corpus-attributed illustrative records.
