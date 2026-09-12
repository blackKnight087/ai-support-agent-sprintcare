# Decision Log

Non-obvious decisions made during this project, and why.

- **Chose sprintcare as the brand** — it had the largest volume of clean, joinable customer↔brand
  reply pairs (22,313) among recognizable brands in the dataset.

- **Fixed a datatype join bug early** — `in_response_to_tweet_id` contained nulls, which forced
  pandas to store it as float, silently breaking the string-based join to `tweet_id` (0 pairs
  matched at first). Converted through nullable `Int64` before stringifying to fix it. Left as a
  reminder that "messy real-world data" bugs can be structural, not just noisy text.

- **Derived the 8-intent taxonomy from reading real sprintcare traffic**, not by importing
  Banking77's 77 banking-specific categories — carrier support traffic doesn't map well to
  banking intents, and a taxonomy built from the actual data is more defensible than one
  transplanted from an unrelated domain.

- **Used a 5,000-pair random subsample** (not the full ~22K pairs, and nowhere near the full ~3M
  row dataset) for both the retrieval corpus and golden-set sampling, per the assignment's
  explicit encouragement to subsample.

- **Used local Ollama (`llama3.1:8b`) instead of a paid API** — zero cost, fully reproducible by
  a grader with no API key setup, at the acknowledged tradeoff of weaker output quality than a
  frontier model (quantified in the report's limitations section).

- **Used the pretrained `all-MiniLM-L6-v2` embedding model unmodified** for retrieval grounding —
  no fine-tuning, standard off-the-shelf choice for this scale of data.

- **Golden-set labels were entirely hand-labeled, with some AI assistance, rather than labeled directly by an LLM. Labels were reviewed, reasoned through, and finalized personally by hand. AI was used only as an assisting tool during the labeling process, such as helping interpret the taxonomy or flag potentially ambiguous examples. The final intent decisions were made and reviewed by a human.
Disclosed explicitly rather than presented as entirely AI-independent labeling, since AI assistance was used during the process. Verified my own reasoning against the most ambiguous cases (billing disputes, competitor-switching messages) before finalizing.

- **Defined "historically resolved"** as simply "the brand replied to this tweet" — not a
  verified fix. This is a known heuristic weakness, flagged in the report, not hidden.

- **Escalation logic is a hybrid, not a single LLM judgment call**: hard safety/legal keyword
  rules fire first, then intent-based policy (billing/device issues escalate by default), then a
  retrieval-confidence fallback. Chosen so safety-critical cases don't depend entirely on model
  judgment. Tradeoff: this design caught the money-risk intents but missed churn-threat language
  in other intents, producing the low escalation recall (15.7%) documented as the top failure
  mode.

- **Kept the golden set's content separate from the classifier's few-shot prompt examples** to
  avoid the classifier being evaluated on data it had effectively already "seen."

- **Initial LLM-judge prompt caused a 54.5% parse failure rate** (109/200) because the model
  sometimes wrapped its JSON output in extra text. Fixed with a regex extraction step pulling the
  `{...}` object out of the raw response, improving success to 99% (198/200) without needing to
  change the underlying scoring prompt.

- **Human-agreement spot-check (15 examples) was done with AI assistance** to reason through each
  score before I confirmed it, rather than scored in complete isolation — disclosed rather than
  presented as a fully solo review. Performed against an earlier, noisier judge run (91/200
  valid); qualitative findings (judge under-scores groundedness) are more reliable than an exact
  score-by-score comparison would be against the current, fixed judge output.

- **Did not attempt multilingual handling** despite a handful of Spanish-language examples
  appearing in the sprintcare data — volume was too low relative to the time budget to justify
  separate handling.

- **Did not fine-tune any model** — relied entirely on retrieval-grounded few-shot prompting,
  which is cheaper to iterate on and easier to audit (any given reply's grounding examples can be
  inspected directly) than a fine-tuned model's behavior.
