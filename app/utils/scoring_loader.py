import pandas as pd

def load_score_data():
    return pd.read_csv("data/scoring/score/emd_with_all_scores.csv", dtype={"EMD_CD": str})