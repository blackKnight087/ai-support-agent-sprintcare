from collections import Counter

def trivial_baseline(golden_set):
    counts = Counter(g['gold_intent'] for g in golden_set)
    majority_intent = counts.most_common(1)[0][0]
    canned_reply = "Thanks for reaching out! We're looking into this for you."
    return [{
        "id": g["id"],
        "pred_intent": majority_intent,
        "pred_reply": canned_reply,
        "pred_escalate": False,
    } for g in golden_set]


def simple_baseline(golden_set, pairs_sample):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    corpus = pairs_sample['customer_text'].fillna("").tolist()
    vec = TfidfVectorizer(max_features=5000).fit(corpus)
    corpus_vecs = vec.transform(corpus)

    results = []
    ESCALATE_KEYWORDS = ["lawyer", "sue", "refund me now", "cancel my account", "never again", "fraud"]

    for g in golden_set:
        q_vec = vec.transform([g['customer_text']])
        sims = cosine_similarity(q_vec, corpus_vecs)[0]
        best_idx = sims.argmax()
        best_reply = pairs_sample.iloc[best_idx]['brand_reply']

        text_lower = g['customer_text'].lower()
        escalate = any(kw in text_lower for kw in ESCALATE_KEYWORDS)

        results.append({
            "id": g["id"],
            "pred_intent": "other", 
            "pred_reply": best_reply,
            "pred_escalate": escalate,
        })
    return results