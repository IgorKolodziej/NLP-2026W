import unittest

import numpy as np
import pandas as pd

from clickbait.cues import CUE_GROUPS, CUE_NAMES, cues_matrix, extract_cues, normalize_cue_text


class CueTests(unittest.TestCase):
    def test_empty_and_missing_text_has_twelve_zeros(self):
        for text in (None, "", " \t\n"):
            self.assertEqual(list(extract_cues(text)), CUE_NAMES)
            self.assertEqual(list(extract_cues(text).values()), [0.0] * 12)
        np.testing.assert_array_equal(cues_matrix(pd.Series([None, np.nan])), np.zeros((2, 12)))

    def test_four_ordered_families_cover_all_columns_once(self):
        self.assertEqual([len(names) for names in CUE_GROUPS.values()], [3] * 4)
        self.assertEqual([name for group in CUE_GROUPS.values() for name in group], CUE_NAMES)

    def test_referential_withholding(self):
        self.assertEqual(extract_cues("This is something anyone can try")["initial_unresolved_pointer"], 1)
        self.assertEqual(extract_cues("Report this event")["initial_unresolved_pointer"], 0)
        self.assertEqual(extract_cues("someone saw something")["indefinite_referent_density"], 2 / 3)
        self.assertEqual(extract_cues("here’s\t why")["delayed_revelation_frame"], 1)
        self.assertEqual(extract_cues("find out whysoever")["delayed_revelation_frame"], 0)
        self.assertEqual(extract_cues("You won't believe what happens next")["delayed_revelation_frame"], 1)

    def test_audience_involvement_and_contractions(self):
        self.assertEqual(extract_cues("YOU’VE seen your results")["direct_address_density"], 0.5)
        for text in ("Watch the event", "Find out today", "SEE the news"):
            self.assertEqual(extract_cues(text)["action_invitation"], 1)
        self.assertEqual(extract_cues("We watch the event")["action_invitation"], 0)
        self.assertEqual(extract_cues("What happened?")["question_hook"], 1)
        self.assertEqual(extract_cues("What happened")["question_hook"], 0)
        self.assertEqual(extract_cues("The event: what happened?")["question_hook"], 0)

    def test_affect_uncertainty_and_reversal(self):
        self.assertEqual(extract_cues("Amazing stunning news")["surprise_word_density"], 2 / 3)
        self.assertEqual(extract_cues("reportedly rumoured")["epistemic_distance_density"], 1)
        self.assertEqual(extract_cues("but then it turned out fine")["narrative_reversal"], 1)
        self.assertEqual(extract_cues("it turns outward")["narrative_reversal"], 0)

    def test_numbered_payoff_boundaries(self):
        for text in ("12 ways to travel", "These 99 surprising little known facts", "１ ways to travel"):
            self.assertEqual(extract_cues(text)["numbered_payoff_promise"], 1, text)
        for text in ("100 ways", "0 tips", "Here are 12 tips", "12 one two three four ways", "12 tip"):
            self.assertEqual(extract_cues(text)["numbered_payoff_promise"], 0, text)

    def test_punctuation_normalization_and_nonoverlapping_ellipses(self):
        for text in ("Wow…!?", "Wow...!?"):
            normalized = normalize_cue_text(text)
            self.assertEqual(extract_cues(text)["attention_punctuation"], 3 / len(normalized))
        self.assertEqual(extract_cues("......")["attention_punctuation"], 2 / 6)
        self.assertEqual(extract_cues("!!!")["attention_punctuation"], 1)

    def test_anchor_case_and_first_token_exclusion(self):
        self.assertEqual(extract_cues("They met Alice in NASA")["referent_anchor_imbalance"], 1 / 3)
        self.assertEqual(extract_cues("Alice said they left")["referent_anchor_imbalance"], 1 / 2)
        self.assertEqual(extract_cues("they met alice")["referent_anchor_imbalance"], 1 / 2)


if __name__ == "__main__":
    unittest.main()
