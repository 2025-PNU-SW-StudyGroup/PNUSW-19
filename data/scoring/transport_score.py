import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import json
import numpy as np

def calculate_transport_score(
    subway_csv_with_dong: str,
    busstop_csv_with_dong: str,
    emd_info_csv: str,
    dong_info_json: str,
    output_json: str = "data/scoring/score/dong_transport_score.json"
):
    # 데이터 로딩 및 전처리
    subway_df = pd.read_csv(subway_csv_with_dong)
    bus_df = pd.read_csv(busstop_csv_with_dong)

    for df in [subway_df, bus_df]:
        df.dropna(subset=["EMD_CD"], inplace=True)
        df["EMD_CD"] = df["EMD_CD"].astype(float).astype(int).astype(str) + "00"

    # 지하철 + 버스 정류장 수 합산
    subway_count = subway_df.groupby("EMD_CD").size().reset_index(name="subway_count")
    bus_count = bus_df.groupby("EMD_CD").size().reset_index(name="bus_count")

    merged_count = pd.merge(subway_count, bus_count, on="EMD_CD", how="outer").fillna(0)
    merged_count["total_count"] = merged_count["subway_count"] + merged_count["bus_count"]

    # 면적 로딩
    emd_df = pd.read_csv(emd_info_csv, dtype={"EMD_CD": str})
    merged = pd.merge(merged_count, emd_df[["EMD_CD", "area_m2"]], on="EMD_CD", how="left")

    # 밀도 계산 및 log 변환
    merged["transport_density"] = merged["total_count"] / (merged["area_m2"] / 1_000_000)
    merged["log_density"] = np.log1p(merged["transport_density"])
    merged = merged.dropna(subset=["log_density"]).copy()

    # 정규화
    scaler = MinMaxScaler()
    merged["transport"] = scaler.fit_transform(merged[["log_density"]])
    merged["transport"] = merged["transport"].round(4)

    # 이름 매핑
    dong_info = json.load(open(dong_info_json, encoding="utf-8"))
    code_to_name = {}
    for gu_entry in dong_info:
        gu = gu_entry["gu"]
        for dong in gu_entry["dong_list"]:
            code_to_name[dong["dong_code"]] = {
                "gu": gu,
                "dong": dong["dong"]
            }

    result = []
    for _, row in merged.iterrows():
        code = row["EMD_CD"]
        if code not in code_to_name:
            continue
        info = code_to_name[code]
        result.append({
            "dong_code": code,
            "gu": info["gu"],
            "dong": info["dong"],
            "transport": row["transport"]
        })

    # 저장
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"🚉 교통 지수 저장 완료: {output_json}")

# 실행 예시
if __name__ == "__main__":
    calculate_transport_score(
        subway_csv_with_dong="data/scoring/infra_data/subway_with_dong.csv",
        busstop_csv_with_dong="data/scoring/infra_data/bus_stop_with_dong.csv",
        emd_info_csv="data/scoring/infra_data/emd_info.csv",
        dong_info_json="data/seoul_dong_list_with_code.json"
    )