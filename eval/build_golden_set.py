import pandas as pd

pairs = pd.read_csv("data/brand_pairs_sample.csv")
golden_candidates = pairs.sample(n=200, random_state=7).reset_index(drop=True)
golden_candidates.to_csv("eval/golden_candidates.csv", index=False)
print("saved 200 candidates")