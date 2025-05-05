import pandas as pd
import json

# 1. emd_info.csv 불러오기
emd_info = pd.read_csv("data/scoring/infra_data/emd_info.csv", dtype={"EMD_CD": str})

# 2. JSON 지수 불러오기 함수
def load_score(path, score_key):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df.rename(columns={"dong_code": "EMD_CD", score_key: f"{score_key}_score"}, inplace=True)
    return df[["EMD_CD", f"{score_key}_score"]]

# 3. 각 지수 JSON → DataFrame으로 변환
infra_df     = load_score("data/scoring/score/dong_food_infra_score.json", "infra")
security_df  = load_score("data/scoring/score/dong_security_score.json", "security")
transport_df = load_score("data/scoring/score/dong_transport_score.json", "transport")
quiet_df     = load_score("data/scoring/score/dong_youth_and_quiet_score.json", "quiet")
youth_df     = load_score("data/scoring/score/dong_youth_and_quiet_score.json", "youth")

# 4. 모든 지수 merge (EMD_CD 기준)
merged = emd_info.copy()
for score_df in [infra_df, security_df, transport_df, quiet_df, youth_df]:
    merged = pd.merge(merged, score_df, on="EMD_CD", how="left")
    
merged.fillna(0, inplace=True)

# 5. dong_code → gu 이름 및 gu_code 매핑
with open("data/seoul_dong_list_with_code.json", encoding="utf-8") as f:
    dong_info = json.load(f)

# 6. dong_code 기반 매핑 딕셔너리 생성
dong_to_gu_name = {}
dong_to_gu_code = {}

for gu_entry in dong_info:
    gu_name = gu_entry["gu"]
    gu_code = gu_entry["gu_code"]
    gu_prefix = gu_code[:5]
    
    for dong in gu_entry["dong_list"]:
        dong_code = dong["dong_code"]
        if dong_code[:5] == gu_prefix:
            dong_to_gu_name[dong_code] = gu_name
            dong_to_gu_code[dong_code] = gu_code

# 7. merged에 gu, gu_code 컬럼 추가
merged["gu"] = merged["EMD_CD"].map(lambda code: dong_to_gu_name.get(code, ""))
merged["gu_code"] = merged["EMD_CD"].map(lambda code: dong_to_gu_code.get(code, ""))

# 8. 컬럼 순서 정리 (선택)
cols = [
    "EMD_CD", "gu", "gu_code", "EMD_NM", "area_m2", "centroid_lon", "centroid_lat",
    "infra_score", "security_score", "transport_score", "quiet_score", "youth_score"
]
merged = merged[cols]


# 9. 저장
merged.to_csv("data/scoring/score/emd_with_all_scores.csv", index=False)
