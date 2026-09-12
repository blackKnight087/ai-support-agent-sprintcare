# AI Customer Support Agent — sprintcare
**Report | Kaggle "Customer Support on Twitter" Assignment**

---

## Executive Summary

This project builds an AI support agent for **sprintcare** (Sprint's Twitter support account),
selected for its high volume of clean, real customer-support traffic. The system classifies
incoming messages into 8 data-derived intents, drafts a reply grounded in the brand's real
historical responses, and decides whether to auto-handle or escalate to a human — with a stated
reason for every decision.

**Headline result:** the full system reaches **63.5% intent accuracy** (macro-F1 0.576) against
a golden set of 200 hand-reviewed examples, compared to ~20% for both a trivial and a simple
baseline. Escalation precision is strong (72.2%) but **recall is a known weakness (15.7%)** —
see Section 4 for why this matters more than the headline number suggests, and Section 3 for the
concrete failure driving it.

This report is intentionally candid about limitations. Section 4 exists specifically to prevent
the headline number above from being read as more definitive than it is.

---

## 1. Problem Framing

**Brand selection.** sprintcare was chosen from the dataset's brand-support handles for having
the largest volume of clean, joinable customer↔brand reply pairs among recognizable brands
(22,313 pairs after resolving a datatype join issue in the raw data — see Decision Log).

**Intent taxonomy.** Eight intents, derived by reading real sprintcare traffic rather than
importing a generic taxonomy (e.g. Banking77's 77 banking-specific categories, which don't map
well to carrier support):

| Intent | Definition |
|---|---|
| `service_or_network_issue` | No signal, dropped calls, data not working, poor coverage |
| `billing_or_refund` | Wrong charge, refund request, plan/billing dispute |
| `account_access` | Login, password, verification, lockout issues |
| `device_or_product_defect` | Hardware physically broken or defective |
| `cancellation_request` | Wants to cancel a plan, line, or service |
| `general_complaint` | Frustration/venting with no clear fixable request |
| `praise_or_neutral` | Compliment, thanks, or non-issue mention |
| `other` | Doesn't clearly fit any category above |

**What "good" means for this brand.** The cost of errors is asymmetric: a missed escalation on
a billing dispute or an explicit churn threat is far more expensive than an imperfect auto-reply
to a routine coverage question. "Good" therefore means prioritizing **escalation reliability on
money/churn-risk situations** over polish on routine traffic, which is dominated by a single
brand pattern ("please send us a DM").

**Explicit scope decisions — what we chose not to build:**
- **Multilingual support.** A small number of Spanish-language examples appear in the data, but
  volume didn't justify separate handling given the time budget.
- **Live handoff/ticketing integration.** Out of scope for an evaluation-focused prototype.
- **Brand-voice fine-tuning.** Used retrieval-grounded few-shot prompting instead, which is
  cheaper to iterate on and easier to audit (you can see exactly which historical examples
  informed any given reply).
- **Multi-provider model comparison.** Used only local Ollama (`llama3.1:8b`) for cost-free
  reproducibility; Section 5 discusses the expected impact of a stronger model.

---

## 2. Results vs. Baselines

| System | Intent Accuracy | Macro-F1 | Escalation Precision | Escalation Recall |
|---|---|---|---|---|
| **Trivial** (majority-class intent, never escalate) | 0.235 | 0.048 | 0.000 | 0.000 |
| **Simple** (TF-IDF nearest-neighbor reply reuse + keyword-rule escalation) | 0.195 | 0.041 | 0.500 | 0.024 |
| **Our system** (LLM classification + retrieval-grounded reply + hybrid escalation) | **0.635** | **0.576** | **0.722** | **0.157** |

**Reply quality (LLM-as-judge, 1–5 scale, 198/200 valid parses):**

| Dimension | Average Score |
|---|---|
| Groundedness | 2.44 |
| Correctness | 3.34 |
| Actionability | 3.80 |

**Reading these results honestly:** the system's intent classification is a clear, substantial
win over both baselines. Escalation is precise but conservative — it correctly flags most of
what it *does* flag, but misses the majority of cases that should be escalated. This is explored
as the top failure mode in Section 3, not glossed over here.

---

## 3. Failure Analysis

**1. Low escalation recall on churn/complaint intents (the biggest gap).**
The escalation logic triggers on hard safety keywords, on `billing_or_refund` /
`device_or_product_defect` intents, or on low retrieval similarity — but not on
`general_complaint` or `cancellation_request`, even when the message contains an explicit churn
threat (e.g. *"officially switching to a new phone provider"*). These cases are exactly the ones
a real support operation would most want caught.
*Hypothesis:* escalation needs a churn/sentiment signal independent of intent category, not
intent-category rules alone.

**2. The judge under-scores groundedness inconsistently.**
A 15-example human spot-check (`eval/human_agreement.md`) found several replies scored 1–2/5 on
groundedness by the judge that in fact closely mirrored the brand's real historical phrasing.
*Hypothesis:* the judge prompt doesn't weight literal phrase/structure overlap with retrieved
examples strongly enough relative to generic politeness cues.

**3. Reply formatting leaks.**
At least one generated reply included meta-narration ("Here's a possible reply:") before the
actual content — a local-model artifact that the judge failed to penalize on actionability.
*Hypothesis:* the generation prompt needs an explicit "output only the reply text" instruction,
plus a post-processing strip step as a safety net.

**4. Fragment/continuation messages lose thread context.**
Single-tweet messages like *"yes it's me...here"* are correctly bucketed as `other`, but the
pipeline can't distinguish a truly content-free fragment from a continuation of an earlier,
unresolved exchange — because it classifies single tweets, not reconstructed threads.
*Hypothesis:* multi-turn thread reconstruction would meaningfully improve intent accuracy on
this class of message.

**5. Golden-set labels were entirely human-labeled, with limited AI assistance

The golden-set labels were assigned and finalized entirely by hand through human review. AI assistance was used only as a supporting tool during the labeling process, such as helping interpret the taxonomy or flagging potentially ambiguous examples. The final intent decisions were made and reviewed by a human, rather than being accepted directly from an LLM.

This is disclosed plainly here and in the Decision Log.

Hypothesis: because the final labels were independently reviewed and decided by a human, the reported accuracy should still be interpreted with some caution; a fully independent second human annotation pass could reveal additional areas of disagreement.
---

## 4. What's Misleading About My Headline Number

The 63.5% intent-accuracy figure is real, but it needs these caveats to be interpreted correctly:

The golden set's labels were entirely hand-labeled, with some AI assistance, not directly AI-labeled. The final intent decisions were manually reviewed and finalized by a human. A second, blind annotator would likely surface disagreements this process didn't catch.
- **"Historically resolved" is a proxy, not a verified outcome.** Grounding data is simply "the
  brand replied to this tweet" — many sprintcare replies are just "please DM us," not evidence
  the underlying issue was actually fixed. The system is grounded in *how the brand responds*,
  not *what actually solves the problem*.
- **Escalation ground truth reflects one person's risk tolerance**, not sprintcare's actual
  internal escalation policy, which isn't available to us.
- **The judge's reliability itself has caveats.** An initial prompt caused a 54.5% parse failure
  rate (109/200); a regex fix improved this to 99% (198/200). The human-agreement spot-check
  was performed against the earlier, noisier run — so the *qualitative* pattern found there
  (systematic under-scoring of groundedness) is more trustworthy than an exact score-by-score
  comparison would be today.
- **Local `llama3.1:8b` is meaningfully weaker than frontier models.** Absolute accuracy and
  reply quality would very likely improve with a GPT-4-class or Claude-class model, at higher
  cost and latency — this system's numbers should be read as a lower bound, not a ceiling.
- **The 5,000-pair subsample and 200-example golden set are small** relative to sprintcare's full
  ~22,000 pairs; results may not generalize evenly across rarer issue types underrepresented in
  the subsample.

---

 ## 5. What I'd Do With One More Week

1. **Independent second-annotator pass** on the golden set to measure real inter-rater agreement,
   replacing the current AI-assisted-then-reviewed process.
2. **Fix escalation recall** by adding explicit churn/threat-language detection, independent of
   intent category — directly targeting failure mode #1.
3. **Add output hygiene**: strip generation-artifact preambles from replies before they reach the
   judge or a human agent (failure mode #3).
4. **Reconstruct full conversation threads** rather than single tweet-reply pairs, for both
   classification and grounding — targeting failure mode #4.
5. **Benchmark against a frontier model** (with cost/latency tracked) to quantify the local-model
   quality gap and produce an actual cost-vs-quality tradeoff curve for a hypothetical production
   decision.
6. **Seek sprintcare's actual escalation policy**, if obtainable, to replace personal judgment
   calls with something closer to ground truth.

---

*Full reproduction instructions in README.md. See `report/decision_log.md` for the complete list
of non-obvious decisions made during this project.*
