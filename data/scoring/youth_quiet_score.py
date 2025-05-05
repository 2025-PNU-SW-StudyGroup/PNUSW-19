import pandas as pd
import json
from typing import Dict, List
from sklearn.preprocessing import MinMaxScaler
import numpy as np

# 시간대 가중치 (중요한 시간대에 더 많은 가중치)
TIME_WEIGHTS = {
    0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0,
    6: 0.8, 7: 0.3, 8: 0.3, 9: 0.4,
    10: 0.5, 11: 0.5, 12: 0.5, 13: 0.5, 14: 0.5, 15: 0.5, 16: 0.5, 17: 0.5,
    18: 0.4, 19: 0.4, 20: 0.4, 21: 0.4,
    22: 1.0, 23: 1.0
}

def calculate_quiet_youth_score(
    population_csv: str,
    admin_to_legal_csv: str,
    legal_dong_json: str,
    emd_info_csv: str
) -> List[Dict[str, object]]:
    pop_df = pd.read_csv(population_csv)
    mapping_df = pd.read_csv(admin_to_legal_csv)
    legal_dong_info = json.load(open(legal_dong_json, encoding="utf-8"))
    emd_info_df = pd.read_csv(emd_info_csv, dtype={"EMD_CD": str})
    emd_info_map = emd_info_df.set_index("EMD_CD")[["area_m2"]].to_dict()["area_m2"]

    pop_df["행정동코드"] = pop_df["행정동코드"].astype(str) + "00"
    mapping_df["행정동코드"] = mapping_df["행정동코드"].astype(str)
    merged_df = pd.merge(pop_df, mapping_df[["행정동코드", "법정동코드"]], on="행정동코드", how="inner")
    merged_df["법정동코드"] = merged_df["법정동코드"].astype(str)
    merged_df["시간가중치"] = merged_df["시간대구분"].map(TIME_WEIGHTS)

    code_to_name = {}
    for gu_entry in legal_dong_info:
        gu_name = gu_entry["gu"]
        for dong in gu_entry["dong_list"]:
            code_to_name[dong["dong_code"]] = {
                "gu": gu_name,
                "dong": dong["dong"]
            }

    male_youth_cols = [
        "남자0세부터9세생활인구수", "남자10세부터14세생활인구수", "남자15세부터19세생활인구수",
        "남자20세부터24세생활인구수", "남자25세부터29세생활인구수", "남자30세부터34세생활인구수",
        "남자35세부터39세생활인구수"
    ]
    female_youth_cols = [
        "여자0세부터9세생활인구수", "여자10세부터14세생활인구수", "여자15세부터19세생활인구수",
        "여자20세부터24세생활인구수", "여자25세부터29세생활인구수", "여자30세부터34세생활인구수",
        "여자35세부터39세생활인구수"
    ]
    total_pop_col = "총생활인구수"

    quiet_data = []
    grouped = merged_df.groupby("법정동코드")

    for dong_code, group in grouped:
        if dong_code not in code_to_name or dong_code not in emd_info_map:
            continue

        weights = group["시간가중치"].fillna(0.5)
        if weights.sum() == 0:
            continue

        try:
            weighted_mean = np.average(group[total_pop_col], weights=weights)
            weighted_var = np.average((group[total_pop_col] - weighted_mean) ** 2, weights=weights)
            weighted_std = np.sqrt(weighted_var)
        except:
            continue

        total_population = group[total_pop_col].sum()
        youth_population = group[male_youth_cols + female_youth_cols].sum().sum()
        if total_population == 0:
            continue

        area_m2 = emd_info_map[dong_code]

        area_km2 = area_m2 / 1_000_000

        # 조용함 지표
        pop_density_mean = weighted_mean / area_m2
        pop_density_std  = weighted_std  / area_m2
        
        # 청년용 지표
        youth_density = youth_population / area_km2
        youth_ratio = youth_population / total_population

        quiet_data.append({
            "dong_code": dong_code,
            "std_density": pop_density_std,
            "mean_density": pop_density_mean,
            "weighted_std": weighted_std,
            "weighted_mean": weighted_mean,
            "youth_density": youth_density,
            "youth_ratio": youth_ratio
        })

    quiet_df = pd.DataFrame(quiet_data)
    scaler = MinMaxScaler()

    # [조용함 지수 보정] 밀도와 원시값 혼합
    quiet_df["std_mix"] = 0.6 * quiet_df["std_density"] + 0.4 * quiet_df["weighted_std"]
    quiet_df["mean_mix"] = 0.6 * quiet_df["mean_density"] + 0.4 * quiet_df["weighted_mean"]

    quiet_df[["norm_std", "norm_mean"]] = scaler.fit_transform(
        quiet_df[["std_mix", "mean_mix"]]
    )

    alpha, beta = 0.6, 0.4
    quiet_df["quiet"] = 1 - (
        alpha * quiet_df["norm_std"] +
        beta  * quiet_df["norm_mean"]
    )
    quiet_df["quiet"] = quiet_df["quiet"].round(4)

    # [젊음 지수] 비율 + 로그 밀도 혼합 유지
    quiet_df["log_youth_density"] = np.log1p(quiet_df["youth_density"])
    quiet_df[["norm_youth_ratio", "norm_youth_density"]] = scaler.fit_transform(
        quiet_df[["youth_ratio", "log_youth_density"]]
    )
    quiet_df["youth"] = (
        0.6 * quiet_df["norm_youth_ratio"] +
        0.4 * quiet_df["norm_youth_density"]
    ).round(4)

    # 최종 결과
    result = []
    for _, row in quiet_df.iterrows():
        dong_code = row["dong_code"]
        if dong_code not in code_to_name:
            continue
        name_info = code_to_name[dong_code]
        result.append({
            "dong_code": dong_code,
            "gu": name_info["gu"],
            "dong": name_info["dong"],
            "quiet": row["quiet"],
            "youth": row["youth"]
        })

    return result

if __name__ == "__main__":
    res = calculate_quiet_youth_score(
        "data/public_data/생활인구.csv",
        "data/public_data/행정동법정동매핑.csv",
        "data/seoul_dong_list_with_code.json",
        "data/scoring/infra_data/emd_info.csv"
    )
    # JSON 저장
    with open("data/scoring/score/dong_youth_and_quiet_score.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)

    print("저장 완료: data/scoring/score/dong_youth_and_quiet_score.json")