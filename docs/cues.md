# Twelve linguistic cues (system C; defined here for Task 4)

Fixed **12** numeric features per teaser (`postText`). Names match `src/clickbait/cues.py` column order.

## Length and word structure (4)

| # | Feature | Description |
|---|---------|-------------|
| 1 | `n_chars` | Character count |
| 2 | `n_words` | Token count (alphanumeric words) |
| 3 | `avg_word_len` | Mean token length |
| 4 | `unique_word_ratio` | Unique tokens / word count |

## Punctuation and capitalization (4)

| # | Feature | Description |
|---|---------|-------------|
| 5 | `n_exclamation` | Count of `!` |
| 6 | `n_question` | Count of `?` |
| 7 | `uppercase_char_ratio` | Uppercase letters / all letters |
| 8 | `n_digits` | Count of digit characters |

## Pronoun and forward-reference lexicons (4)

| # | Feature | Description |
|---|---------|-------------|
| 9 | `second_person_lexicon_hits` | Matches in [`resources/second_person.txt`](../resources/second_person.txt) |
| 10 | `first_person_plural_lexicon_hits` | Matches in [`resources/first_person_plural.txt`](../resources/first_person_plural.txt) |
| 11 | `forward_reference_hits` | Word and phrase matches in [`resources/forward_reference.txt`](../resources/forward_reference.txt) |
| 12 | `all_caps_word_count` | Words (letters only) with length > 1 that are all uppercase |

Lexicon lines are lowercase; matching is case-insensitive. Multi-word lines are phrase matches; single-token lines use word boundaries.

**Ablation groups** (Task 9): `length_structure`, `punctuation_caps`, `pronoun_forward_lexicon` — see `CUE_GROUPS` in `cues.py`.
