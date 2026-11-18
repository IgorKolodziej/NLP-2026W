# Mid-term video speaking script

English, two presenters and a ten-minute target including pauses and slide changes. **Presenter 1 ends at 05:00. Presenter 2 finishes at 10:00.** The bracketed cues are silent. Presenter notes contain the same spoken lines.

## 00:00–00:15 · Presenter 1 · Slide 1 · Clickbait Without the Click

**[Start on slide 1. Start timing with the first word.]**

Given an English social-media teaser, can we predict whether human annotators labelled it clickbait? Our project, Clickbait Without the Click, tests that question on posts collected at different times.

## 00:15–01:05 · Presenter 1 · Slide 2 · Which cities?

**[Advance to slide 2 at 00:15.]**

“These cities will overthrow Silicon Valley as the new centers for tech in coming years.” Which cities?

**[Pause briefly after “Which cities?”]**

The teaser promises a list without naming them. That gap can make readers curious. Similar wording also appears in ordinary news, so we use the dataset's human labels. Each system sees the teaser, the short message a reader sees before opening the link.

Our main question is whether twelve fixed language cues improve macro F-one on later posts when we keep the embeddings identical. We then ask whether that gain recurs across months and which groups of cues contribute.

## 01:05–01:55 · Presenter 1 · Slide 3 · What prior work tells us

**[Advance to slide 3 at 01:05.]**

Potthast and colleagues showed that observable properties of publisher tweets can help a random forest detect clickbait. Their work gives us a reason to test cues whose definitions we can inspect.

Zhou's attention model won the 2017 challenge, and Indurthi and colleagues later used transformers to improve strength prediction. That benchmark asked how clickbait-like a post is. Their results use the official challenge test. Our April posts come from the public labelled training release, and our target is its binary label. We take a learned representation as our baseline, freeze it, and measure what the explicit cues add.

## 01:55–03:05 · Presenter 1 · Slide 4 · What our experiment adds

**[Advance to slide 4 at 01:55.]**

Michaluk and colleagues show that a hybrid can work. Their model combines OpenAI embeddings with fifteen explicit features and uses boosted decision trees. Their reported ablation changes embedding size as well as adding features. We keep the vectors identical for our embedding and hybrid systems and give both the same classifier family and tuning budget.

Søgaard and colleagues show why a shuffled split can give optimistic results. We measure the cue gain across later months and use grouped random splits as a diagnostic. Grouping keeps posts with the same normalized title together in those diagnostics. We audit overlap across partitions and remove one cue family at a time to learn where the gain comes from. Our data lacks publisher IDs, so the chronological test tells us about later posts from this collection.

## 03:05–04:15 · Presenter 1 · Slide 5 · The A/B/C pipeline

**[Advance to slide 5 at 03:05.]**

In the proof of concept, we join the released labels to teasers by ID, clean and audit the data, and use a recorded chronological split. Each system sees the same teaser text.

System A weights word and character patterns with TF-IDF. B uses MiniLM to turn a teaser into a fixed vector of three hundred and eighty-four numbers. C takes that exact vector and appends twelve cue values from the same teaser. Each system fits its own logistic regression using the same five regularization options. We give more weight to the less frequent clickbait class during fitting. The common representation lets us test what the twelve cues add to B. A gives us a separate lexical benchmark using the same posts.

## 04:15–05:00 · Presenter 1 · Slide 6 · What a cue measures

**[Advance to slide 6 at 04:15.]**

Here is a March teaser. “How does your brain handle virtual reality?” It starts with “how” and contains a question mark, so the question hook fires. The word “your” matches one of seven tokens for direct address.

The twelve cues cover four families. They describe how a teaser withholds information, involves the reader, frames a story, or packages a promise. Ordinary reporting can use these patterns too. Now let's see what happened when we ran these models on later posts.

**[Handoff at 05:00.]**

## 05:00–06:00 · Presenter 2 · Slide 7 · What entered the PoC

**[Presenter 2 takes over and advances to slide 7 at 05:00.]**

We started from the public labelled Webis-17 release. After joining texts and labels, we removed empty and repeated teasers. That left nineteen thousand and seventy-three posts. A further three hundred and ninety-one shared a normalized article title with an earlier retained post. Every exclusion is recorded in the ledger.

About twenty-four percent of the cleaned posts are labelled clickbait. The chart shows that December has the largest positive share. In the cleaned corpus, the median teaser length is ten words for clickbait and twelve for the other class.

Our main partitions share zero exact IDs, normalized teasers, or normalized titles. We use titles as a proxy for articles, so related articles with different titles need a separate check. That near-duplicate audit is still pending.

## 06:00–06:50 · Presenter 2 · Slide 8 · Train, validate, test

**[Advance to slide 8 at 06:00.]**

We train on December through February, select regularization in March, and score the resulting systems on April. The training rows determine the TF-IDF vocabulary and how we scale the cues. The MiniLM encoder stays frozen.

About twenty-three percent of April posts are positive. Macro F-one gives both classes equal weight by averaging their two F-one scores. Our primary comparison subtracts B's score from C's on exactly the same April posts. We also measure positive-class precision and recall, average precision, and Brier score. Later, we will use reliability diagrams to compare predicted probabilities with observed rates.

## 06:50–07:55 · Presenter 2 · Slide 9 · April results

**[Advance to slide 9 at 06:50.]**

The pipeline ran end to end on real posts. It saved predictions for all three systems on the same test rows. A fresh environment reproduced the results. The repository includes the predictions and the commands for running the experiment.

**[Give viewers a moment to read the chart before stating the difference.]**

Adding the cues raised April macro F-one by two point six three percentage points over the MiniLM baseline. TF-IDF had the highest macro F-one in this window.

April was held out from fitting and regularization selection in this run. We had seen earlier April pilot scores, so we treat this as preliminary. We have a point estimate from one window, with the paired interval still to come.

## 07:55–08:40 · Presenter 2 · Slide 10 · What changed on individual posts?

**[Advance to slide 10 at 07:55.]**

**[Point to the first example, then to the second as it is introduced.]**

The first example is the teaser we opened with. B missed it and C correctly flagged it. On the right, the post recommends shows and movies. The corpus label is non-clickbait, and C introduces a false positive. Both posts trigger the opening-pointer cue. These are two examples of what changes when we fit the full hybrid model.

Across the April test, C corrected a hundred and sixty-two errors that B made and introduced eighty new errors. We will use such disagreements to guide a systematic error analysis.

## 08:40–09:30 · Presenter 2 · Slide 11 · What will test H1–H4?

**[Advance to slide 11 at 08:40.]**

Next, we will estimate uncertainty around the April gain, then check whether it recurs in February and March and how it compares with grouped random splits. We will remove one cue family at a time, examine at least twenty categorized errors, and check calibration alongside class prevalence.

Wu and colleagues motivate our context study. Both systems get the same posts, teasers, titles and the first ninety-six word tokens from available article paragraphs. Both already use the twelve teaser cues. D adds three measurements of how the teaser relates to that excerpt.

## 09:30–10:00 · Presenter 2 · Slide 12 · Before the Phase 2 checkpoint

**[Advance to slide 12 at 09:30.]**

Before Phase Two, our priorities are near-duplicate checking and selecting an additional method class. A fine-tuned encoder on the same teaser splits is one candidate. Webis-16 transfer also needs schema, label and overlap checks. For the Q-and-A, we'd like feedback on validating near-duplicate detection when related articles have different titles. Thank you.

**[End the recording on slide 12. The three appendix slides are for Q&A.]**

## Rehearsal timings

| Slide | Time | Presenter | Spoken words |
|---|---|---|---:|
| 1 | 00:00–00:15 | 1 | 29 |
| 2 | 00:15–01:05 | 1 | 96 |
| 3 | 01:05–01:55 | 1 | 98 |
| 4 | 01:55–03:05 | 1 | 132 |
| 5 | 03:05–04:15 | 1 | 121 |
| 6 | 04:15–05:00 | 1 | 80 |
| 7 | 05:00–06:00 | 2 | 124 |
| 8 | 06:00–06:50 | 2 | 95 |
| 9 | 06:50–07:55 | 2 | 106 |
| 10 | 07:55–08:40 | 2 | 87 |
| 11 | 08:40–09:30 | 2 | 91 |
| 12 | 09:30–10:00 | 2 | 52 |

**1,111 spoken words.** Presenter 1 has **556** words and Presenter 2 has **555**. The planned windows sum to **600 seconds**. Time a joint read with pauses and the handoff. If a section runs long, shorten literature details and optional work before touching the result or the April disclosure.
