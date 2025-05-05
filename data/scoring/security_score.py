import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import json
import numpy as np

def calculate_security_score(
    cctv_csv_with_dong: str,
    emd_info_csv: str,
    dong_info_json: str,
    output_json: str = "data/scoring/score/dong_security_score.json"
):
    # 데이터 불러오기
    cctv_df = pd.read_csv(cctv_csv_with_dong)
    cctv_df = cctv_df[cctv_df["EMD_CD"].notna()].copy()
    cctv_df["EMD_CD"] = cctv_df["EMD_CD"].astype(float).astype(int).astype(str) + "00"

    emd_df = pd.read_csv(emd_info_csv, dtype={"EMD_CD": str})
    dong_info = json.load(open(dong_info_json, encoding="utf-8"))

    # CCTV 수 집계
    cctv_count = cctv_df.groupby("EMD_CD").size().reset_index(name="count")

    # 면적 join
    emd_area = emd_df[["EMD_CD", "area_m2"]]
    merged = pd.merge(cctv_count, emd_area, on="EMD_CD", how="left")

    # 1㎢당 밀도 계산 + 로그 스케일 적용
    merged["cctv_density"] = merged["count"] / (merged["area_m2"] / 1_000_000)
    merged["log_density"] = np.log1p(merged["cctv_density"])
    merged = merged.dropna(subset=["log_density"]).copy()

    # 정규화
    scaler = MinMaxScaler()
    merged["security"] = scaler.fit_transform(merged[["log_density"]])
    merged["security"] = merged["security"].round(4)

    # 동 정보 매핑
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
            "security": row["security"]
        })

    # 저장
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"보안 지수 저장 완료: {output_json}")

# 실행 예시
if __name__ == "__main__":
    calculate_security_score(
        cctv_csv_with_dong="data/scoring/infra_data/cctv_with_dong.csv",
        emd_info_csv="data/scoring/infra_data/emd_info.csv",
        dong_info_json="data/seoul_dong_list_with_code.json"
    )