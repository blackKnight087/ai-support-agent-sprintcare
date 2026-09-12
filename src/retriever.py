from sentence_transformers import SentenceTransformer
import numpy as np

class Retriever:
    def __init__(self, pairs_sample):
        self.pairs = pairs_sample.reset_index(drop=True)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.embeddings = self.model.encode(self.pairs['customer_text'].fillna("").tolist(), show_progress_bar=True)

    def top_k(self, query, k=3):
        q_emb = self.model.encode([query])[0]
        sims = self.embeddings @ q_emb / (np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(q_emb) + 1e-8)
        top_idx = np.argsort(sims)[-k:][::-1]
        return [{"customer_text": self.pairs.iloc[i]['customer_text'], "brand_reply": self.pairs.iloc[i]['brand_reply'], "similarity": float(sims[i])} for i in top_idx]