import pandas as pd
import json
from src.taxonomy import INTENTS

df = pd.read_csv("eval/golden_candidates.csv")
intent_keys = list(INTENTS.keys())

results = []
print("Intents:")
for i, k in enumerate(intent_keys):
    print(f"  {i}: {k} - {INTENTS[k]}")
print()

for idx, row in df.iterrows():
    print(f"\n--- Example {idx+1}/{len(df)} ---")
    print("CUSTOMER:", row['customer_text'])
    print("BRAND REPLIED (historically):", row['brand_reply'])

    intent_choice = input("Intent number (or 'skip'): ").strip()
    if intent_choice == "skip":
        continue
    gold_intent = intent_keys[int(intent_choice)]

    escalate = input("Should a human handle this? (y/n): ").strip().lower() == "y"
    reason = input("One-line reason for that escalate call: ").strip()

    results.append({
        "id": idx,
        "customer_text": row['customer_text'],
        "gold_intent": gold_intent,
        "gold_resolution_summary": row['brand_reply'],
        "gold_escalate": escalate,
        "gold_escalate_reason": reason,
    })

    with open("eval/golden_set.jsonl", "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

print(f"\nDone. Labeled {len(results)} examples -> eval/golden_set.jsonl")