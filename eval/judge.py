import json
import re
import ollama

MODEL = "llama3.1:8b"

def judge_reply(customer_text, gold_resolution, generated_reply):
    prompt = f"""Rate this customer support reply from 1-5 on each dimension. Be strict.

Customer message: "{customer_text}"
How this brand actually resolved similar issues before: "{gold_resolution}"
Generated reply to evaluate: "{generated_reply}"

Score 1-5 for each: groundedness, correctness, actionability.
Respond ONLY as JSON: {{"groundedness": X, "correctness": X, "actionability": X}}"""
    resp = ollama.generate(model=MODEL, prompt=prompt)
    text = resp['response'].strip()
    match = re.search(r'\{[^{}]*\}', text)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
    return {"groundedness": None, "correctness": None, "actionability": None}

if __name__ == "__main__":
    golden = [json.loads(l) for l in open("eval/golden_set.jsonl", encoding="utf-8")]
    preds = {p['id']: p for p in (json.loads(l) for l in open("eval/system_predictions.jsonl", encoding="utf-8"))}

    scores = []
    total = len(golden)
    for i, g in enumerate(golden, 1):
        p = preds.get(g['id'])
        if not p:
            continue
        s = judge_reply(g['customer_text'], g['gold_resolution_summary'], p['pred_reply'])
        s['id'] = g['id']
        scores.append(s)
        print(f"  [{i}/{total}] judged (groundedness={s['groundedness']})")

    with open("eval/judge_scores.jsonl", "w", encoding="utf-8") as f:
        for s in scores:
            f.write(json.dumps(s) + "\n")

    valid = [s for s in scores if s['groundedness'] is not None]
    avg_g = sum(s['groundedness'] for s in valid) / len(valid)
    avg_c = sum(s['correctness'] for s in valid) / len(valid)
    avg_a = sum(s['actionability'] for s in valid) / len(valid)
    print(f"\nAvg groundedness: {avg_g:.2f}, correctness: {avg_c:.2f}, actionability: {avg_a:.2f}")
    print(f"Parsed successfully: {len(valid)}/{len(scores)}")