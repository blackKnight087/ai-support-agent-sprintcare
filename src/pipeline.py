import ollama
from src.taxonomy import INTENTS

MODEL = "llama3.1:8b"
ESCALATE_HARD_RULES = ["lawyer", "sue", "suicide", "kill myself", "threat", "police", "fraud", "unsafe"]

def classify_intent(customer_text):
    intent_list = "\n".join(f"- {k}: {v}" for k, v in INTENTS.items())
    prompt = f"""You are classifying a customer support tweet into exactly one intent.

Intents:
{intent_list}

Customer message: "{customer_text}"

Reply with ONLY the intent key (one of: {', '.join(INTENTS.keys())}), nothing else."""
    resp = ollama.generate(model=MODEL, prompt=prompt)
    text = resp['response'].strip().lower()
    for k in INTENTS:
        if k in text:
            return k
    return "other"

def draft_reply(customer_text, retrieved_examples):
    context = "\n\n".join(f"Similar past case:\nCustomer said: {e['customer_text']}\nBrand replied: {e['brand_reply']}" for e in retrieved_examples)
    prompt = f"""You are a customer support agent. Use the past examples below as a guide to how this brand
typically resolves similar issues -- match their tone and typical next steps.

{context}

New customer message: "{customer_text}"

Write a short, on-brand reply:"""
    resp = ollama.generate(model=MODEL, prompt=prompt)
    return resp['response'].strip()

def decide_escalation(customer_text, intent, retrieved_examples):
    text_lower = customer_text.lower()
    for kw in ESCALATE_HARD_RULES:
        if kw in text_lower:
            return True, f"hard-rule keyword match: '{kw}'"
    if intent in ("billing_or_refund", "device_or_product_defect"):
        return True, f"intent '{intent}' involves money/liability -- escalate by policy"
    avg_sim = sum(e['similarity'] for e in retrieved_examples) / max(len(retrieved_examples), 1)
    if avg_sim < 0.35:
        return True, f"low retrieval confidence (avg similarity {avg_sim:.2f})"
    return False, "routine intent, good grounding match, no risk keywords"

def run_pipeline(customer_text, retriever):
    intent = classify_intent(customer_text)
    retrieved = retriever.top_k(customer_text, k=3)
    reply = draft_reply(customer_text, retrieved)
    escalate, reason = decide_escalation(customer_text, intent, retrieved)
    return {"pred_intent": intent, "pred_reply": reply, "pred_escalate": escalate, "pred_escalate_reason": reason, "retrieved": retrieved}