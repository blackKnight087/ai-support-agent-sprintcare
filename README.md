# AI Customer Support Agent — sprintcare

An AI support agent built on the Kaggle *Customer Support on Twitter* dataset, focused on
**sprintcare** (Sprint's Twitter support account). Given an incoming customer message, the
system:

1. **Classifies** it into one of 8 intents derived from the brand's real traffic
2. **Drafts a reply** grounded in how sprintcare has historically resolved similar issues
3. **Decides** whether to auto-handle or escalate to a human — with a stated reason

Full methodology, results, and  limitations are in [`report/REPORT.md`](report/REPORT.md).

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Pull the local model (free, no API key required)
ollama pull llama3.1:8b

# 3. Reproduce headline results (~15–40 min on a laptop CPU, depending on hardware)
python -m eval.harness    # baselines + full system → prints comparison table
python -m eval.judge      # LLM-as-judge reply-quality scoring
```

That's it — no API keys, no cloud dependencies. Everything runs locally against a bundled
5,000-pair subsample of sprintcare's real historical traffic.

---

## Headline Results

| System | Intent Accuracy | Macro-F1 | Escalation Precision | Escalation Recall |
|---|---|---|---|---|
| Trivial baseline | 0.235 | 0.048 | 0.000 | 0.000 |
| Simple baseline (TF-IDF + rules) | 0.195 | 0.041 | 0.500 | 0.024 |
| **This system** | **0.635** | **0.576** | **0.722** | **0.157** |

See [`report/REPORT.md`](report/REPORT.md) Section 4 for why the headline number above is *not*
the full story, and Section 3 for the concrete failure driving the low escalation recall.

---

## Repository Structure

```
support-agent/
├── data/
│   ├── twcs.csv                    # full Kaggle dataset (downloaded via kagglehub)
│   └── brand_pairs_sample.csv      # 5,000-pair sprintcare subsample used throughout
├── src/
│   ├── taxonomy.py                 # 8 intent definitions, derived from real data
│   ├── baselines.py                # trivial + simple (TF-IDF) baselines
│   ├── retriever.py                # embedding-based retrieval for reply grounding
│   └── pipeline.py                 # classify → ground → draft → escalate
├── eval/
│   ├── golden_set.jsonl            # 200 hand-reviewed evaluation examples
│   ├── sampling_note.md            # how the golden set was sampled and labeled
│   ├── build_golden_set.py         # golden-set candidate sampling
│   ├── label_golden_set.py         # interactive labeling tool
│   ├── harness.py                  # automated metrics: baselines vs. system
│   ├── judge.py                    # LLM-as-judge reply-quality scoring
│   └── human_agreement.md          # judge-vs-human agreement spot-check
├── report/
│   ├── REPORT.md                   # full writeup: framing, results, failures, next steps
│   └── decision_log.md             # non-obvious decisions and why
└── requirements.txt
```

---

## How the Pipeline Works

- **Classification**: prompts `llama3.1:8b` (via Ollama) with the 8 intent definitions and the
  incoming message; falls back to `other` if the model's response doesn't match a known intent.
- **Grounding**: embeds the incoming message with `sentence-transformers/all-MiniLM-L6-v2`
  (unmodified, pretrained) and retrieves the 3 most similar historical customer messages, along
  with sprintcare's real replies to them.
- **Reply drafting**: the retrieved historical examples are passed to the LLM as few-shot
  context, asking it to match the brand's tone and typical next steps.
- **Escalation**: a hybrid decision — hard safety/legal keyword rules fire first, then
  intent-based policy (billing/device issues escalate by default), then a retrieval-confidence
  fallback for anything the system can't ground well. Every decision includes a stated reason
  string, not just a boolean.

## Data & Attribution

- Dataset: [Customer Support on Twitter](https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter)
  (Kaggle, `thoughtvector/customer-support-on-twitter`), downloaded via `kagglehub`.
- Embedding model: `all-MiniLM-L6-v2` from
  [sentence-transformers](https://www.sbert.net/), used unmodified.
- LLM: `llama3.1:8b`, run locally via [Ollama](https://ollama.com/), used unmodified.
- - Golden-set labels were entirely hand-labeled, with some AI assistance. AI was used only as an assisting tool during the labeling process, such as helping interpret the taxonomy or flag potentially ambiguous examples. All final intent decisions were reviewed and finalized by hand — see `report/decision_log.md` for the full disclosure.

## Known Limitations

**Limitations:**
- Intent classification may misclassify ambiguous or overlapping customer queries.
- Reply quality depends on the relevance and coverage of historical support conversations.
- Escalation recall is limited, meaning some queries requiring human intervention may not be flagged.
- Response generation and evaluation depend on the capabilities of the local Llama 3.1 8B model.
- The system is trained and evaluated on a limited dataset focused on @sprintcare, so performance may vary across other brands and support domains.
