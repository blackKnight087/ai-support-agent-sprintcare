import json
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, precision_score, recall_score
import sys, os
sys.path.append(os.path.abspath("."))
from src.pipeline import run_pipeline
from src.retriever import Retriever
from src.baselines import trivial_baseline, simple_baseline

def load_golden_set():
    with open("eval/golden_set.jsonl", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def run_full_system(golden_set, retriever):
    results = []
    total = len(golden_set)
    for i, g in enumerate(golden_set, 1):
        out = run_pipeline(g['customer_text'], retriever)
        out['id'] = g['id']
        results.append(out)
        print(f"  [{i}/{total}] processed (intent={out['pred_intent']}, escalate={out['pred_escalate']})")
    return results

def score_intent(golden_set, preds):
    gold = [g['gold_intent'] for g in golden_set]
    pred = [p['pred_intent'] for p in preds]
    return accuracy_score(gold, pred), f1_score(gold, pred, average='macro', zero_division=0), confusion_matrix(gold, pred)

def score_escalation(golden_set, preds):
    gold = [g['gold_escalate'] for g in golden_set]
    pred = [p['pred_escalate'] for p in preds]
    return precision_score(gold, pred, zero_division=0), recall_score(gold, pred, zero_division=0)

if __name__ == "__main__":
    golden_set = load_golden_set()
    pairs_sample = pd.read_csv("data/brand_pairs_sample.csv")
    retriever = Retriever(pairs_sample)

    trivial_preds = trivial_baseline(golden_set)
    simple_preds = simple_baseline(golden_set, pairs_sample)
    system_preds = run_full_system(golden_set, retriever)

    for name, preds in [("TRIVIAL", trivial_preds), ("SIMPLE", simple_preds), ("YOUR SYSTEM", system_preds)]:
        acc, f1, cm = score_intent(golden_set, preds)
        prec, rec = score_escalation(golden_set, preds)
        print(f"\n=== {name} ===")
        print(f"Intent accuracy: {acc:.3f}, macro-F1: {f1:.3f}")
        print(f"Escalation precision: {prec:.3f}, recall: {rec:.3f}")

    with open("eval/system_predictions.jsonl", "w", encoding="utf-8") as f:
        for p in system_preds:
            f.write(json.dumps(p) + "\n")