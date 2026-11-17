# Mid-term video speaking script

English, two presenters, target **10:00** including slide changes, handoff and natural pauses. **Presenter 1: 00:00-05:00. Presenter 2: 05:00-10:00.** The first five minutes cover the problem, SOTA approaches and research gap. The PoC occupies 07:10-08:10.

Read the prose exactly. Do not read headings or bracketed instructions. The same speech appears in presenter notes. Sources in the notes are not spoken. Timing windows are rehearsal targets, not a measured recording.

## 00:00-00:25 - Presenter 1 - Slide 1: Clickbait Without the Click

**[Start recording on slide 1. Start the timer with the first word.]**

Hello. Our project is Clickbait Without the Click. We ask whether simple language cues help a model detect clickbait, and whether that benefit lasts when we test on later posts. We will explain the problem, review existing approaches, and then present our study and first results.

**[Advance to slide 2 at 00:25. Pause briefly while the audience reads the slide.]**

## 00:25-01:20 - Presenter 1 - Slide 2: Clickbait and the curiosity gap

Consider this teaser: “These cities will overthrow Silicon Valley as the new centers for tech in coming years.” Which cities? The text promises an answer without naming the cities. This creates a curiosity gap: readers need to open the article to learn the answer.

But detecting clickbait takes more than spotting certain words. Ordinary news can also use “these,” questions or emotional language. People may disagree about whether a post is clickbait. We classify English social-media teasers using the labels supplied with the dataset. We are not predicting clicks or checking facts. We also ask whether patterns learned from earlier posts still help on later ones.

**[Advance to slide 3 at 01:20. Pause briefly while the audience reads the slide.]**

## 01:20-02:05 - Presenter 1 - Slide 3: Explicit linguistic features

Early work uses explicit features of the text. Potthast and colleagues measure wording and style in publisher tweets, then use a random forest to classify them. Biyani and colleagues use boosted trees with information from the title, article body and URL, including how informal the article is.

These studies motivate our use of simple, readable cues. They also show why the available input matters: a model given an article has more information than one given only its teaser. We ask whether cues add value to a model that already uses learned text representations.

**[Advance to slide 4 at 02:05. Pause briefly while the audience reads the slide.]**

## 02:05-02:55 - Presenter 1 - Slide 4: Learning patterns from text

Neural approaches learn patterns from text. Zhou's system uses a recurrent network that reads a tweet in both directions. Attention helps it focus on important words. It learns features without defining each one by hand, and won the 2017 Clickbait Challenge.

Indurthi and colleagues use transformer representations and boosted regression to predict clickbait strength. They ask how clickbait-like a post is, rather than only whether it is clickbait.

These studies motivate our embedding baseline. An embedding is a vector of numbers representing a text. We keep that representation fixed and ask what explicit cues add. Scores from different tasks and test sets are not directly comparable.

**[Advance to slide 5 at 02:55. Pause briefly while the audience reads the slide.]**

## 02:55-03:45 - Presenter 1 - Slide 5: Michaluk et al.: our starting point

Michaluk and colleagues combine OpenAI embeddings with fifteen linguistic features and XGBoost. The features include pronouns and attention-grabbing punctuation. They evaluate headlines from mixed sources using a random split.

Their reported comparison changes embedding width as well as adding features. Our B and C models use exactly the same embedding vectors and classifier family, so the added cue block is the controlled difference. We will test that difference across later months and remove cue groups to see which help. Our contribution is a controlled test of cue value and its stability over time.

**[Advance to slide 6 at 03:45. Pause briefly while the audience reads the slide.]**

## 03:45-04:10 - Presenter 1 - Slide 6: Title style and article context

Wu and colleagues study title style and title-body relationships using attention. This motivates our separate context experiment with word overlap, missing named entities and text similarity. Every compared model will receive the same teaser, title and article lead. We will test whether relation cues add further information.

**[Advance to slide 7 at 04:10. Pause briefly while the audience reads the slide.]**

## 04:10-05:00 - Presenter 1 - Slide 7: Evidence for generalization

How we split the data matters. Søgaard and colleagues show that random splits can give optimistic estimates of performance on new samples. We plan to compare later-month tests with random splits that keep posts linked to the same article together.

Röttger and Pierrehumbert found that extra pretraining on text from a specific period did not improve their classifier beyond pretraining on the same type of text. We therefore need to measure whether language changes affect our results.

RoCliCo tests articles from unseen publishers. Our data lacks publisher IDs, so later-month tests cannot establish that kind of transfer. Presenter Two will now explain our study.

**[Handoff to Presenter 2 at 05:00.]**

## 05:00-06:15 - Presenter 2 - Slide 8: Our proposed study

**[Presenter 2 takes over at 05:00. Advance to slide 8.]**

We compare three systems. A uses TF-IDF, which weights word and character patterns, followed by logistic regression. B uses fixed MiniLM embeddings with logistic regression. C uses exactly the same embeddings as B and adds twelve cue values. All three use the same classifier family and five regularization settings to choose from.

The cues form four groups of three. They cover withheld information, direct reader involvement, emotional or narrative wording, and how specific or attention-grabbing the text is. Examples include an opening “these,” direct address, surprise words and promises such as “7 reasons”. A cue is a possible signal, not proof of clickbait.

We ask whether these cues improve B, whether the benefit lasts across months, and which groups matter. In the context experiment, every model will receive the same teaser, title and first ninety-six words of the article lead. We will test three extra relation cues beyond a baseline that already has the twelve teaser cues.

**[Advance to slide 9 at 06:15. Pause briefly while the audience reads the slide.]**

## 06:15-07:10 - Presenter 2 - Slide 9: Data and evaluation design

We use the public labelled Webis-17 training release, covering December 2016 to April 2017. We join texts and labels by ID, then remove empty teasers, repeated teasers and repeated article titles. This leaves eighteen thousand six hundred and eighty-two posts, with about twenty-four percent labelled clickbait.

We train on December through February, choose regularization using March, and test on three thousand five hundred and eighty April posts. We learn the TF-IDF vocabulary and cue scaling from training data only. Macro F-one averages the F-one scores of both classes. We compare C minus B on the same test posts. Two earlier time windows and three grouped random splits are planned. Webis-16 transfer checks remain unfinished.

**[Advance to slide 10 at 07:10. Pause briefly while the audience reads the slide.]**

## 07:10-08:10 - Presenter 2 - Slide 10: PoC: cues improve B, A remains strongest

The proof of concept saves predictions for all three models on the same test posts. Reloading the models reproduced those predictions. A separate run in a fresh environment with the same package versions also matched.

On April, A scores macro F-one zero point seven four seven nine. B scores zero point seven one one one. C scores zero point seven three seven four. Adding cues to B gives about two point six three percentage points.

So cues improve B in this run, but A remains strongest. This PoC covers one time window, and we have not calculated a confidence interval for the difference. April was excluded from training and model selection, but the team had already seen earlier pilot results on it. These findings are preliminary.

**[Advance to slide 11 at 08:10. Pause briefly while the audience reads the slide.]**

## 08:10-09:10 - Presenter 2 - Slide 11: Remaining experiments

Next, we will calculate uncertainty for C minus B using paired bootstrap resampling of the test posts. We will compare the gain across all three time windows and the grouped random splits. A gain seen only in random splits would not show that it lasts over time.

We will also remove one cue group at a time, examine changes in cue values, and study at least twenty errors or model disagreements. The context experiment will compare models on the same posts and article text.

We still need to check near duplicates and cross-dataset overlap, and how well predicted probabilities match observed labels. For Phase Two, we still need a baseline from another classifier family. A Jeff language-model comparison and YouTube title tests remain optional.

**[Advance to slide 12 at 09:10. Pause briefly while the audience reads the slide.]**

## 09:10-10:00 - Presenter 2 - Slide 12: Intended contribution and next checkpoint

We want to understand when simple language cues improve clickbait detection, which groups help, and whether their value lasts over time. Finding no benefit, or a benefit that changes between months, would still answer part of our question.

Our data is historical, and the labels reflect human judgment. Topics and language may change together. We use article titles to approximate article identity, and have no publisher IDs. These limits rule out claims about current deployment or unseen publishers.

Before December second, we will strengthen the experiments, data checks, literature review and reproduction instructions, and address supervisor and Q-and-A feedback. Thank you.

**[Finish by 10:00. End the video.]**

## Rehearsal and recording

| Slide | Time | Presenter | Topic | Spoken words |
|---|---|---|---|---:|
| 1 | 00:00-00:25 | 1 | Clickbait Without the Click | 46 |
| 2 | 00:25-01:20 | 1 | Clickbait and the curiosity gap | 106 |
| 3 | 01:20-02:05 | 1 | Explicit linguistic features | 93 |
| 4 | 02:05-02:55 | 1 | Learning patterns from text | 106 |
| 5 | 02:55-03:45 | 1 | Michaluk et al.: our starting point | 93 |
| 6 | 03:45-04:10 | 1 | Title style and article context | 47 |
| 7 | 04:10-05:00 | 1 | Evidence for generalization | 103 |
| 8 | 05:00-06:15 | 2 | Our proposed study | 157 |
| 9 | 06:15-07:10 | 2 | Data and evaluation design | 114 |
| 10 | 07:10-08:10 | 2 | PoC: cues improve B, A remains strongest | 125 |
| 11 | 08:10-09:10 | 2 | Remaining experiments | 124 |
| 12 | 09:10-10:00 | 2 | Intended contribution and next checkpoint | 101 |

Total spoken words: **1,215**. Presenter 1: **594** words. Presenter 2: **621** words. The twelve windows total **600 seconds**. Slide targets range from 110 to 127 words per minute, allowing for pronunciation, pointing and pauses.

Rehearse aloud with a stopwatch, especially the paper names, decimal scores and 05:00 handoff. If ahead, pause after the example, tables and result. If behind, practise a steadier delivery. Keep the qualifications about incomplete experiments and earlier April exposure.

Record full-screen slides with microphone audio. Check both presenters' levels and that the result chart is readable. End on slide 12. No video has been recorded or uploaded.
