from pydantic import BaseModel
from typing import Optional, List


class PropertyResult(BaseModel):
    property_id: int
    score: float
    commute_min: float
    image: Optional[str]
    address: Optional[str]
    deposit: Optional[int]
    monthly_rent_cost: Optional[int]
    maintenance_cost: Optional[int]
    area: Optional[float]
    floor: Optional[int]
    property_type: Optional[str]
    features: Optional[str]
    direction: Optional[str]
    property_number: Optional[str]
    property_name: Optional[str]
    transaction_type: Optional[str]
    property_confirmation_date: Optional[str]
    rooms_bathrooms: Optional[str]
    duplex: Optional[bool]
    total_floor: Optional[int]
    room_type: Optional[str]
    parking_spaces: Optional[int]
    elevator_count: Optional[int]
    approval_date: Optional[str]
    cctv_count: Optional[int]
    infra_count: Optional[int]
    avg_cctv_distance: Optional[float]
    avg_infra_distance: Optional[float]
    bus_count: Optional[int]
    subway_count: Optional[int]
    avg_bus_stop_distance: Optional[float]
    avg_subway_distance: Optional[float]
    infra_score: Optional[float]
    security_score: Optional[float]
    transport_score: Optional[float]
    quiet_score: Optional[float]
    youth_score: Optional[float]
    commute_score: Optional[float]


class PropertyRecommendationResponse(BaseModel):
    total: int
    total_pages: int
    page: int
    page_size: int
    results: List[PropertyResult]

    class Config:
        json_schema_extra = {
            "example": {
                "total": 9,
                "total_pages": 1,
                "page": 1,
                "page_size": 10,
                "results": [
                    {
                        "property_id": 28573,
                        "score": 0.43333,
                        "commute_min": 0.93,
                        "image": None,
                        "address": "서울특별시 광진구 아차산로 607",
                        "deposit": 100000000,
                        "monthly_rent_cost": 630000,
                        "maintenance_cost": 198000,
                        "area": 39.96,
                        "floor": 5,
                        "property_type": "원룸",
                        "features": "대로변 보안철저 최상급원룸 실사용면적넓은 분리형원룸 ",
                        "direction": "남동향",
                        "property_number": "2519802943",
                        "property_name": "일반원룸",
                        "transaction_type": "월세",
                        "property_confirmation_date": "2025-04-14",
                        "rooms_bathrooms": "1/1개",
                        "duplex": False,
                        "total_floor": 5,
                        "room_type": "지상",
                        "parking_spaces": None,
                        "elevator_count": None,
                        "approval_date": None,
                        "cctv_count": 310,
                        "infra_count": 77,
                        "avg_cctv_distance": 542.43,
                        "avg_infra_distance": 398.06,
                        "bus_count": 35,
                        "subway_count": 1,
                        "avg_bus_stop_distance": 445.42,
                        "avg_subway_distance": 324.17,
                        "infra_score": 0.4511,
                        "security_score": 0.164,
                        "transport_score": 0.2266,
                        "quiet_score": 0.833,
                        "youth_score": 0.35,
                        "commute_score": 0.9795
                    }
                ]
            }
        }
