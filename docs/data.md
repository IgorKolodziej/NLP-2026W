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
