from app.models.user_input import UserInput, Budget
from app.models.dong_input import DongPropertiesInput
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.property_db import Property
from sqlalchemy import func
from app.models.property_db import PropertyCCTVMap, PropertyRestFoodPermitMap, PropertyBusStopMap, PropertySubwayMap
from app.utils.scoring_loader import load_score_data
from decimal import Decimal
from geopy.distance import geodesic
from sqlalchemy import select, func, and_, or_
from sklearn.preprocessing import MinMaxScaler
from collections import defaultdict
import math

TRANSPORT_PROFILE = {
        "car": {"speed_kmh": 25, "correction_factor": 2.5},
        "public": {"speed_kmh": 15, "correction_factor": 3},  # 환승 고려
    }

def float_or_none(val):
    return float(val) if isinstance(val, Decimal) else None

from math import exp

def decay_score(dist, decay):
    if dist is None:
        return 0
    return round(exp(-dist / decay), 4)

def parse_point_string(point_str):
    try:
        parts = point_str.strip().replace("POINT(", "").replace(")", "").split()
        if len(parts) != 2:
            return None, None
        lon, lat = map(float, parts)
        return lat, lon
    except Exception as e:
        print(f"[POINT • 파싱 실패] {e} | 원본: {point_str}")
        return None, None

def compute_commute_time_min(prop_location: str, job_location: list, transport_profile: dict):
    try:
        lat, lon = parse_point_string(prop_location)
        if lat is None or lon is None:
            return None
        job_lat, job_lon = job_location[1], job_location[0]
        distance_km = geodesic((lat, lon), (job_lat, job_lon)).km
        speed_kmh = transport_profile["speed_kmh"]
        correction = transport_profile["correction_factor"]
        return round(distance_km * correction / speed_kmh * 60, 2)
    except:
        return None

async def recommend_properties(input_data: DongPropertiesInput, db: AsyncSession):
    property_ids = input_data.property_ids
    user_input = input_data.user_input
    page, page_size = input_data.page, input_data.page_size
    quiet_score_map = {input_data.dong_code: input_data.quiet_score}
    youth_score_map = {input_data.dong_code: input_data.youth_score}

    if not property_ids:
        return {"total": 0, "total_pages": 0, "page": page, "page_size": page_size, "results": []}

    result = await db.execute(
        select(Property, func.ST_AsText(Property.location).label("location_wkt"))
        .where(Property.id.in_(property_ids))
    )
    rows = result.all()

    async def fetch_maps(model):
        rows = await db.execute(
            select(
                model.property_id,
                func.count().label("count"),
                func.avg(model.distance_meters).label("avg_distance")
            ).where(model.property_id.in_(property_ids)).group_by(model.property_id)
        )
        return rows.fetchall()

    cctv_data = await fetch_maps(PropertyCCTVMap)
    infra_data = await fetch_maps(PropertyRestFoodPermitMap)
    bus_data = await fetch_maps(PropertyBusStopMap)
    subway_data = await fetch_maps(PropertySubwayMap)

    cctv_map = {r.property_id: r.count for r in cctv_data}
    cctv_dist_map = {r.property_id: float(r.avg_distance) for r in cctv_data}
    infra_map = {r.property_id: r.count for r in infra_data}
    infra_dist_map = {r.property_id: float(r.avg_distance) for r in infra_data}
    bus_count_map = {r.property_id: r.count for r in bus_data}
    bus_dist_map = {r.property_id: float(r.avg_distance) for r in bus_data}
    subway_count_map = {r.property_id: r.count for r in subway_data}
    subway_dist_map = {r.property_id: float(r.avg_distance) for r in subway_data}

    transport_mode = user_input.transportation[0] if user_input.transportation else "public"
    transport_profile = TRANSPORT_PROFILE.get(transport_mode, TRANSPORT_PROFILE["public"])

    score_map = {
        "infra": "infra_score",
        "safety": "security_score",
        "transport": "transport_score",
        "quiet": "quiet_score",
        "youth": "youth_score",
        "commute": "commute_score"
    }

    if not user_input.priority:
        age = user_input.age
        gender = user_input.gender.lower()
        if 0 <= age <= 34:
            user_input.priority = ["youth", "commute", "infra"]
        elif gender == "female":
            user_input.priority = ["safety", "quiet", "commute"]
        else:
            user_input.priority = ["commute", "infra", "safety"]

    priority_len = len(user_input.priority)
    weights = {1: [1.0], 2: [0.6, 0.4], 3: [0.5, 0.3, 0.2]}.get(priority_len, [1.0 / priority_len] * priority_len)

    adjustments = {
        "security_score": 1.0,
        "youth_score": 1.0,
        "quiet_score": 1.0,
        "infra_score": 1.0,
        "transport_score": 1.0,
        "commute_score": 1.0,
    }

    if 0 <= user_input.age <= 34:
        adjustments["youth_score"] += 0.1
    if user_input.gender.lower() == "female":
        adjustments["security_score"] += 0.1
        adjustments["quiet_score"] += 0.05
    elif user_input.gender.lower() == "male":
        adjustments["transport_score"] += 0.1
        adjustments["infra_score"] += 0.05

    recommendations = []
    for row in rows:
        prop = row[0]
        location_str = row.location_wkt
        pid = prop.id
        dong_code = prop.administrative_code

        commute_min = compute_commute_time_min(location_str, user_input.job_location, transport_profile)
        if commute_min is None:
            print(f"[commute 오류] 매물 ID: {pid}, location: {location_str}, job: {user_input.job_location}")

        base_scores = {
            "infra_score": decay_score(infra_dist_map.get(pid), 500),
            "security_score": decay_score(cctv_dist_map.get(pid), 300),
            "transport_score": decay_score(bus_dist_map.get(pid), 300),
            "quiet_score": quiet_score_map.get(dong_code, 0),
            "youth_score": youth_score_map.get(dong_code, 0),
            "commute_score": decay_score(commute_min * 60 if commute_min else None, 45 * 60),
        }

        total_score = 0
        for i, key in enumerate(user_input.priority):
            col = score_map[key]
            base = base_scores.get(col, 0)
            adj = adjustments.get(col, 1.0)
            total_score += base * weights[i] * adj

        rent_score = max(0, 100 - math.log(prop.monthly_rent_cost + 1, 1.07)) if prop.monthly_rent_cost else 0
        total_score += rent_score

        recommendations.append({
            "property_id": pid,
            "score": round(total_score, 5),
            "commute_min": commute_min,
            "image": prop.main_image_url,
            "address": prop.address,
            "deposit": prop.deposit,
            "monthly_rent_cost": prop.monthly_rent_cost,
            "maintenance_cost": prop.maintenance_cost,
            "area": float_or_none(prop.area),
            "floor": prop.floor,
            "property_type": prop.property_type,
            "features": prop.features,
            "direction": prop.direction,
            "property_number": prop.property_number,
            "property_name": prop.property_name,
            "transaction_type": prop.transaction_type,
            "property_confirmation_date": str(prop.property_confirmation_date) if prop.property_confirmation_date else None,
            "rooms_bathrooms": prop.rooms_bathrooms,
            "duplex": prop.duplex,
            "total_floor": prop.total_floor,
            "room_type": prop.room_type,
            "parking_spaces": prop.parking_spaces,
            "elevator_count": prop.elevator_count,
            "approval_date": str(prop.approval_date) if prop.approval_date else None,
            "cctv_count": cctv_map.get(pid, 0),
            "infra_count": infra_map.get(pid, 0),
            "avg_cctv_distance": cctv_dist_map.get(pid),
            "avg_infra_distance": infra_dist_map.get(pid),
            "bus_count": bus_count_map.get(pid, 0),
            "subway_count": subway_count_map.get(pid, 0),
            "avg_bus_stop_distance": bus_dist_map.get(pid),
            "avg_subway_distance": subway_dist_map.get(pid),
            **base_scores,
        })

    recommendations.sort(key=lambda x: x["score"], reverse=True)
    total = len(recommendations)
    start = (page - 1) * page_size

    return {
        "total": total,
        "total_pages": (total + page_size - 1) // page_size,
        "page": page,
        "page_size": page_size,
        "results": recommendations[start:start + page_size]
    }


def build_property_filters(budget: Budget):
    filters = []

    # 거래 유형
    if budget.transaction_type and len(budget.transaction_type) > 0:
        filters.append(Property.transaction_type.in_(budget.transaction_type))
    
    # 매물 유형
    if budget.property_type:
        filters.append(Property.property_type.in_(budget.property_type))

    # 보증금
    if budget.deposit:
        if len(budget.deposit) == 2:
            filters.append(Property.deposit.between(budget.deposit[0], budget.deposit[1]))
        elif len(budget.deposit) == 1:
            filters.append(Property.deposit >= budget.deposit[0])

    # 월세
    if budget.monthly_rent:
        if len(budget.monthly_rent) == 2:
            filters.append(Property.monthly_rent_cost.between(budget.monthly_rent[0], budget.monthly_rent[1]))
        elif len(budget.monthly_rent) == 1:
            filters.append(Property.monthly_rent_cost >= budget.monthly_rent[0])

    # 관리비
    if budget.maintenance_cost:
        if len(budget.maintenance_cost) == 2:
            filters.append(Property.maintenance_cost.between(budget.maintenance_cost[0], budget.maintenance_cost[1]))
        elif len(budget.maintenance_cost) == 1:
            filters.append(Property.maintenance_cost <= budget.maintenance_cost[0])

    # 면적
    if budget.area:
        if len(budget.area) == 2:
            filters.append(Property.area.between(budget.area[0], budget.area[1]))
        elif len(budget.area) == 1:
            filters.append(Property.area >= budget.area[0])

    # 방향 (문자열 포함 여부)
    if budget.direction:
        filters.append(or_(*[Property.direction.contains(d) for d in budget.direction]))

    # 층 구조 유형
    if budget.floor_type and len(budget.floor_type) > 0:
        filters.append(Property.room_type.in_(budget.floor_type))

    return filters

async def recommend_dongs(user_input: UserInput, db):
    df = load_score_data()

    TRANSPORT_PROFILE = {
        "자가용": {"speed_kmh": 25, "correction_factor": 2.5},
        "대중교통": {"speed_kmh": 15, "correction_factor": 3},  # 환승 고려
    }

    # 1. 직장 기준 통근 시간 계산 (km / 25km/h * 60분)
    mode = "자가용"
    if "대중교통" in user_input.transportation:
        mode = "대중교통"

    profile = TRANSPORT_PROFILE.get(mode, TRANSPORT_PROFILE["자가용"])
    speed_kmh = profile["speed_kmh"]
    correction = profile["correction_factor"]

    # 2. 통근 시간 계산
    user_lon, user_lat = user_input.job_location
    df["commute_min"] = df.apply(
        lambda row: geodesic(
            (row["centroid_lat"], row["centroid_lon"]),
            (user_lat, user_lon)
        ).km * correction / speed_kmh * 60,
        axis=1
    )

    # 2. 통근 시간 필터링 (1.2배 여유 허용)
    MARGIN_FACTOR = 1.2
    commute_threshold = user_input.max_commute_min * MARGIN_FACTOR
    filtered = df[df["commute_min"] <= commute_threshold].copy()

    # 3. commute_score (낮을수록 좋음)
    scaler = MinMaxScaler()
    filtered["norm_commute"] = scaler.fit_transform(filtered[["commute_min"]])
    filtered["commute_score"] = 1 - filtered["norm_commute"]

    # 4. 우선순위 가중치 반영
    score_map = {
        "infra": "infra_score",
        "safety": "security_score",
        "transport": "transport_score",
        "quiet": "quiet_score",
        "youth": "youth_score",
        "commute": "commute_score"
    }
    
    # 기본값 설정
    if not user_input.priority:
        age = user_input.age
        gender = user_input.gender.lower()
        if 0 <= age <= 34:
            user_input.priority = ["youth", "commute", "infra"]
        elif gender == "female":
            user_input.priority = ["safety", "quiet", "commute"]
        else:
            user_input.priority = ["commute", "infra", "safety"]
    
    # 우선순위 가중치 설정
    priority_len = len(user_input.priority)
    if priority_len == 1:
        weights = [1.0]
    elif priority_len == 2:
        weights = [0.6, 0.4]
    elif priority_len >= 3:
        weights = [0.5, 0.3, 0.2][:priority_len]
        
    # 사용자 특성 기반 보정 인자 설정
    adjustments = {
        "security_score": 1.0,
        "youth_score": 1.0,
        "quiet_score": 1.0,
        "infra_score": 1.0,
        "transport_score": 1.0,
        "commute_score": 1.0,
    }

    age = user_input.age
    gender = user_input.gender.lower()

    if 0 <= age <= 34:
        adjustments["youth_score"] += 0.1
    if gender == "female":
        adjustments["security_score"] += 0.1
        adjustments["quiet_score"] += 0.05
    elif gender == "male":
        adjustments["transport_score"] += 0.1
        adjustments["infra_score"] += 0.05

    for i, key in enumerate(user_input.priority):
        col = score_map[key]
        adjusted_weight = weights[i] * adjustments.get(col, 1.0)
        filtered[f"w_{col}"] = filtered[col] * adjusted_weight

    score_cols = [f"w_{score_map[p]}" for p in user_input.priority]
    filtered["total_score"] = filtered[score_cols].sum(axis=1)
    
    

    # 5. 매물 조건 필터링 및 count
    filters = build_property_filters(user_input.budget)
    
    stmt = select(Property.id, Property.administrative_code).where(and_(*filters))
    result = await db.execute(stmt)
    property_rows = result.all()

    count_map = defaultdict(int)
    property_map_by_dong = defaultdict(list)
    for prop_id, admin_code in property_rows:
        count_map[admin_code] += 1
        property_map_by_dong[admin_code].append(prop_id)

    # 6. 매물 수 매핑
    filtered["property_count"] = filtered["EMD_CD"].map(lambda code: count_map.get(code, 0))

    grouped_result = []

    filtered_sorted = filtered.sort_values(
        by=["property_count", "total_score"], ascending=[False, False]
    )[
        [
            "gu", "gu_code", "EMD_NM", "EMD_CD", "total_score", "commute_min", "property_count",
            "infra_score", "security_score", "quiet_score", "youth_score",
            "transport_score", "commute_score"
        ]
    ]

    for gu, group in filtered_sorted.groupby("gu"):
        total_property_count = int(group["property_count"].sum())
        if total_property_count == 0:
            continue

        dong_list = group.sort_values(
            by=["total_score","property_count","commute_min"], ascending=[False, False, True]
        ).apply(lambda row: {
            "dong": row["EMD_NM"],
            "dong_code": row["EMD_CD"],
            "total_score": round(row["total_score"], 3),
            "property_count": int(row["property_count"]),
            "commute_min": round(row["commute_min"], 2),
            "infra_score": round(row["infra_score"], 3),
            "security_score": round(row["security_score"], 3),
            "quiet_score": round(row["quiet_score"], 3),
            "youth_score": round(row["youth_score"], 3),
            "transport_score": round(row["transport_score"], 3),
            "commute_score": round(row["commute_score"], 3),
            "property_ids": property_map_by_dong.get(row["EMD_CD"], []),
        }, axis=1).tolist()

        grouped_result.append({
            "gu": str(gu),
            "gu_code": str(group["gu_code"].iloc[0]),
            "avg_total_score": float(round(group["total_score"].mean(), 3)),
            "total_property_count": int(total_property_count),
            "avg_scores": {
                "infra_score": float(round(group["infra_score"].mean(), 3)),
                "security_score": float(round(group["security_score"].mean(), 3)),
                "quiet_score": float(round(group["quiet_score"].mean(), 3)),
                "youth_score": float(round(group["youth_score"].mean(), 3)),
                "transport_score": float(round(group["transport_score"].mean(), 3)),
                "commute_score": float(round(group["commute_score"].mean(), 3)),
            },
            "dong_list": dong_list
        })
        
        grouped_result = sorted(
            grouped_result,
            key=lambda x: (x["avg_total_score"], x["total_property_count"]),
            reverse=True
        )


    return {
        "recommended_area": grouped_result
    }

