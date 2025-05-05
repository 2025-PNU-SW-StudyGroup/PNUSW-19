import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from shapely.wkt import loads as wkt_loads
from pyproj import CRS
from tqdm import tqdm

def load_admin_boundaries(shp_path):
    gdf = gpd.read_file(shp_path, encoding='euc-kr')
    if gdf.crs is None or gdf.crs.to_epsg() != 5186:
        gdf = gdf.to_crs(epsg=5186)
    return gdf

def preprocess_admin_boundaries(shp_path, save_path='data/scoring/infra_data/emd_info.csv'):
    # 행정동 경계 불러오기
    gdf = gpd.read_file(shp_path, encoding='euc-kr')
    
    # 좌표계를 EPSG:5186로 변환 (면적 계산용)
    gdf = gdf.to_crs(epsg=5186)

    # 면적 계산 (단위: m^2)
    gdf['area_m2'] = gdf.geometry.area

    # 중심 좌표 계산 후 위경도 변환
    centroids = gdf.geometry.centroid
    centroids_wgs84 = centroids.to_crs(epsg=4326)

    gdf['centroid_lon'] = centroids_wgs84.x
    gdf['centroid_lat'] = centroids_wgs84.y
    
    gdf['EMD_CD'] = gdf['EMD_CD'].astype(str) + '00'

    # 필요한 열만 추출
    result_df = gdf[['EMD_CD', 'EMD_NM', 'area_m2', 'centroid_lon', 'centroid_lat']].copy()

    # CSV 저장
    result_df.to_csv(save_path, index=False, encoding='utf-8-sig')

    return result_df

def find_admin_dong(lat, lon, admin_gdf):
    # 입력 좌표를 포인트로 생성 (위경도 기준)
    point = gpd.GeoSeries([Point(lon, lat)], crs='EPSG:4326')
    # shp 좌표계에 맞춰 변환
    point = point.to_crs(epsg=5186)
    
    # 해당 포인트가 포함된 행정동 찾기
    matched = admin_gdf[admin_gdf.contains(point.iloc[0])]
    if matched.empty:
        return None
    else:
        # 예시: 'ADM_DR_NM'이라는 컬럼이 행정동명일 경우
        result = matched.iloc[0]
        return {
            'EMD_CD': result['EMD_CD'],
            'EMD_NM': result['EMD_NM']
        }

def assign_admin_dong(df: pd.DataFrame, admin_gdf: gpd.GeoDataFrame, location_col: str = "location") -> pd.DataFrame:
    tqdm.pandas()
    
    def extract_lat_lon_from_point(wkt_str: str):
        try:
            point = wkt_loads(wkt_str)
            return point.y, point.x  # lat, lon
        except:
            return None, None

    def match_dong(wkt_str: str):
        lat, lon = extract_lat_lon_from_point(wkt_str)
        if lat is None or lon is None:
            return {"EMD_CD": None, "EMD_NM": None}
        result = find_admin_dong(lat, lon, admin_gdf)
        return result or {"EMD_CD": None, "EMD_NM": None}

    matched = df[location_col].progress_apply(match_dong)
    df["EMD_CD"] = matched.apply(lambda x: x["EMD_CD"])
    df["EMD_NM"] = matched.apply(lambda x: x["EMD_NM"])
    
    return df

if __name__ == "__main__":
    shp_path = 'data/public_data/서울행정동경계/LSMD_ADM_SECT_UMD_11_202504.shp'
    admin_gdf = load_admin_boundaries(shp_path)
    files = [
        "data/public_data/bus_stop.csv",
        "data/public_data/cctv.csv",
        "data/public_data/rest_food_permit.csv",
        "data/public_data/subway.csv"
    ]

    # 각 파일 처리
    for file_path in files:
        df = pd.read_csv(file_path)
        df = assign_admin_dong(df, admin_gdf, location_col="location")
        save_path = file_path.replace(".csv", "_with_dong.csv")
        df.to_csv(save_path, index=False, encoding="utf-8-sig")
        print(f"저장 완료: {save_path}")


# shp_path = 'data/서울행정동경계/LSMD_ADM_SECT_UMD_11_202504.shp'
# emd_info = preprocess_admin_boundaries(shp_path)
# print(emd_info.head())