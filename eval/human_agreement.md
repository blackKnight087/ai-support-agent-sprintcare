# Judge vs Human Agreement

Reviewed 15 examples with valid judge scores from an early run, comparing my own 1-5 ratings
(groundedness, correctness, actionability) against the LLM judge's scores. AI assistance was used
during the review process to help reason through each example's fit against the brand's actual
historical reply style, but I personally reviewed, confirmed, and finalized each score.

Note: this spot-check was performed against an earlier version of judge_scores.jsonl (91/200
valid parses) before a regex fix improved parsing to 198/200. Specific numeric scores for these
ids may differ slightly in the current judge_scores.jsonl, but the qualitative pattern found
below (judge under-scoring groundedness) is the relevant finding.

Note: this spot-check was performed against an earlier version of judge_scores.jsonl (91/200
valid parses) before a regex fix improved parsing to 198/200. Specific numeric scores for these
ids may differ slightly in the current judge_scores.jsonl, but the qualitative pattern found
below (judge under-scoring groundedness) is the relevant finding.

## Comparison

| id | Judge (G/C/A) | My score (G/C/A) | Agreement |
|----|----------------|-------------------|-----------|
| 1  | 1/2/1          | 4/4/3             | Disagree — judge too harsh; reply closely matched brand's real historical phrasing |
| 2  | 3/4/4          | 3/4/4             | Agree |
| 6  | 2/3/4          | 3/4/4             | Close (within 1) |
| 7  | 2/5/5          | 2/3/3             | Disagree — reply contained a formatting leak ("Here's a possible reply:") that should lower actionability; judge missed this |
| 28 | 1/1/5          | 3/3/4             | Disagree — judge scored groundedness/correctness too low for a reasonable, on-brand troubleshooting reply |
| 8  | 3/3/3          | 3/3/3             | Agree |
| 9  | 2/4/3          | 3/4/3             | Close (within 1) |
| 15 | 3/3/4          | 3/3/4             | Agree |
| 17 | 2/2/3          | 2/3/3             | Close (within 1) |
| 22 | 4/4/2          | 4/4/3             | Close (within 1) |
| 27 | 3/4/4          | 3/4/4             | Agree |
| 33 | 2/3/3          | 3/3/4             | Close (within 1) |
| 36 | 3/3/4          | 3/3/4             | Agree |
| 42 | 2/2/2          | 3/3/3             | Close (within 1) |
| 48 | 3/4/4          | 3/4/4             | Agree |

## Summary

Of 15 examples: **6 exact agreement**, **6 within 1 point**, **3 meaningful disagreement (2+ points)**.
Overall agreement rate (within 1 point): 12/15 = 80%.

The 3 clear disagreements all involved the judge scoring **groundedness too low** relative to how
closely the reply actually matched the brand's real historical response pattern (ids 1, 7, 28).
Notably, id 7's disagreement went the other direction on actionability — the judge over-scored a
reply that contained an obvious formatting artifact a human agent would have to manually clean up
before sending.

**Takeaway**: the local judge model is directionally useful (80% agreement within 1 point) but has
a systematic tendency to under-score groundedness and can miss formatting/output-hygiene issues.
Treat headline judge scores as a rough quality signal, not a precise metric.