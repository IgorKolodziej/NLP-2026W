# Independent presentation review

Historical review of an earlier draft. Slide numbers and timing below refer to that draft. Current resolutions and validation are recorded in [review.md](review.md).

Review target: `poc.qmd`, `speaking_script.md`, `README.md`, and `PLAN.md`, checked against the course rules/assessment criteria and the verified pilot artifacts. The review is intentionally strict about what the mid-term video can claim.

## Must fix before recording

1. **Correct the repeated wording that reverses the split.** Slide 7 and the script say “3,580 April rows held out for fitting”. The test rows are held out *from fitting* and are evaluated after fitting. Replace this in the metric label, slide note, and script. The same wording appears on slide 8’s small caption (“April test held out for fitting”).

2. **State the missing external-dataset comparison explicitly.** Criterion 2.2 asks for a comparison with another dataset, or a sentence explaining why it is not yet included. The deck currently only lists Webis-16 as future work. Add a sentence to slide 10 or 11: “No external-dataset result is included in this PoC; Webis-16 is deferred until the in-domain protocol is stable, so we do not mix datasets or protocols prematurely.” This makes the omission deliberate and checkable.

3. **Make the method-class gap explicit as a Phase 2 action.** The honest caveat that A, B, and C are all logistic regression is good, but the next-step slide must say what will be delivered before Phase 2: name the distinct class (for example, a fine-tuned encoder or a clearly specified tree/boosting baseline), its split, and its fixed evaluation protocol. Otherwise criterion 2.3 remains visibly incomplete. Do not present the current three systems as three method classes.

4. **Resolve the generated title slide before distributing HTML.** The source contains a manual title slide but the rendered reveal deck was observed to generate an additional automatic title slide. Rendered output must begin with exactly one title slide, and the script’s slide numbers must match the visible deck. Remove/disable the automatic metadata title slide or remove the metadata that triggers it, then re-render and inspect the complete deck.

5. **Bring the spoken script into the 10-minute range.** The body is about 1,417 words before natural pauses and technical pronunciation. That requires roughly 142 words/minute even before handoffs, which is too fast for a recorded scientific talk. Target approximately 1,200–1,300 spoken words. The densest section is slide 3 (about 182 words for 70 seconds); cut repeated framing there. Use the stated slide windows as maximums, not evidence that the recording will actually last 600 seconds.

## Should fix for a strong, defensible video

- Keep the “pilot”, “one temporal window”, “point estimate”, and “not blind/unseen” disclosures. They are unusually valuable because the April partition had earlier team exposure. Never call it an unseen test.
- Keep the distinction between C−B (+0.0263) and A’s overall score. Do not imply cues beat the lexical baseline or establish causality. The examples slide already says examples are not an error taxonomy; retain that restraint.
- On the result slide, label the metric as **April temporal-main test macro-F1 (n=3,580)** and keep the positive rate (23.2%) nearby. This avoids a common question about which split produced each number.
- Add a small “current status” phrase to the method-class caveat: `2.3 status: partial in PoC; distinct method planned before Phase 2`. This helps reviewers distinguish a deliberate scope boundary from an accidental omission.
- Backup references are adequate for a short video, but the speaker should not read them. The main SOTA slide should continue to say that scores are not a common leaderboard because datasets, fields, splits, and metrics differ.
- The title slide should use the actual project title and complete team names once the automatic-title issue is fixed; avoid leaving a generic generated title in the shareable HTML.

## Requirements check

| Requirement | Review result |
|---|---|
| Problem, SOTA, methodology, PoC, findings, next steps | Present in the planned order |
| Working end-to-end PoC and number | Present; verified pilot values are used |
| EDA, imbalance, duplicate/leakage check | Present, with near-duplicate audit correctly marked deferred |
| External dataset comparison or reason | **Add explicit reason; currently only implicit future work** |
| Two method classes | **Not complete in current PoC; caveat and named Phase 2 action required** |
| Runtime, hardware, memory | Present; keep “held out from fitting” wording |
| Two presenters and exact script | Present; shorten script and recheck after title-slide correction |
| Ten-minute reveal.js source | Source present; rendered deck requires title-slide QA |
| Less-than-half scope | Clearly stated and credible |
| Q&A preparation | Three useful project-specific questions present |

## Verdict

The presentation is substantively strong and appropriately cautious. After the five must-fix items—especially the split wording, explicit external-dataset rationale, method-class plan, duplicate-title removal, and script shortening—it should be ready to record. No new results are needed for this mid-term video; the priority is accurate wording, timing, and a one-to-one match between source, rendered slides, and script.
