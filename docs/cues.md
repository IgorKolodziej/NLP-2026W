# Twelve linguistic cues

The primary hybrid model appends exactly twelve scalar features to the same 384 frozen MiniLM coordinates used by the embedding baseline. The revised proposal's Appendix A supplies the definitions. Exact token sets and phrases are stored in [linguistic_cues.json](../resources/linguistic_cues.json), and column order is `CUE_NAMES` in `src/clickbait/cues.py`.

## Shared normalization

Apply Unicode NFKC, normalize straight/curly/modifier apostrophes to `'`, and collapse whitespace. Preserve case before token lowercasing for anchor detection. Tokens are contiguous ASCII letters with optional internal apostrophes, or contiguous digit runs. Use whole-token, case-insensitive matching without stemming. Phrase matches require word boundaries and allow repeated whitespace after normalization.

Let n = max(1, number of tokens), m = max(1, normalized character count). Empty or missing input produces twelve zeros. All indicators are 0/1; all densities/relative features lie in [0,1]. Teaser length is not itself a model cue.

| # | Column | Definition |
|---|--------|------------|
| 1 | `initial_unresolved_pointer` | First token belongs to `initial_pointer`. This is the operational proxy for an initial unresolved referent. |
| 2 | `indefinite_referent_density` | Number of tokens in `indefinite_referent` / n. |
| 3 | `delayed_revelation_frame` | Any complete phrase in `delayed_revelation`. |
| 4 | `direct_address_density` | Number of tokens in `direct_address` / n, including listed contractions. |
| 5 | `action_invitation` | First token belongs to `action_invitation`, or first two tokens are `find out`. |
| 6 | `question_hook` | First token belongs to `question_start` and the teaser contains `?`. |
| 7 | `surprise_word_density` | Number of tokens in `surprise` / n. |
| 8 | `epistemic_distance_density` | Number of tokens in `epistemic_distance` / n. A cautious-reporting proxy whose class association is empirical. |
| 9 | `narrative_reversal` | Any complete phrase in `narrative_reversal`. |
| 10 | `numbered_payoff_promise` | An integer from 1 to 99 appears among the first two tokens, followed within four tokens by a word in `payoff`. |
| 11 | `attention_punctuation` | min(1, (exclamation marks + question marks + ellipsis events) / m). Count each non-overlapping `...` once; NFKC converts a Unicode ellipsis to three dots. |
| 12 | `referent_anchor_imbalance` | P / (P + A + 1). P counts listed `referent` tokens; A counts capitalized non-initial tokens excluding ALL-CAPS tokens. |

## Families

| Family key | Columns |
|------------|---------|
| `referential_withholding` | 1–3 |
| `audience_involvement` | 4–6 |
| `affective_narrative_framing` | 7–9 |
| `specificity_presentation` | 10–12 |

All cues use `postText` only, with no labels or article content. Fit `StandardScaler` on the twelve training cue columns only; preserve embedding coordinates. Constant training cues remain present. No test-driven changes to token sets or phrases are permitted.

## Interpretation and validation

An active cue is a proxy, not a proof of clickbait or an explanation of an individual decision. Capitalized-token anchors are deliberately cheaper and less reliable than named-entity recognition. Question hooks, cautious reporting and surprise terms may also occur in ordinary news.

`tests/test_cues.py` covers phrase boundaries, apostrophes/NFKC, empty inputs, positional payoff windows, ellipses, original-case anchors and family/column order. Neural-feature tests check ID alignment, embedding equality and training-only scaling. The earlier length/count cues and legacy lexicon text files are historical; the current extractor reads only `linguistic_cues.json`.
