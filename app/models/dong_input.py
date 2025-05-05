from pydantic import BaseModel
from typing import List, Optional
from app.models.user_input import UserInput

class DongPropertiesInput(BaseModel):
    dong: str
    dong_code: str
    total_score: float
    property_count: int
    commute_min: float
    infra_score: float
    security_score: float
    quiet_score: float
    youth_score: float
    transport_score: float
    commute_score: float
    property_ids: List[int]
    user_input: UserInput
    page: Optional[int] = 1
    page_size: Optional[int] = 10

    class Config:
            json_schema_extra  = {
                "example": {
                    "dong": "광장동",
                    "dong_code": "1121510400",
                    "total_score": 0.8,
                    "property_count": 3,
                    "commute_min": 1.55,
                    "infra_score": 0.424,
                    "security_score": 0.655,
                    "quiet_score": 0.833,
                    "youth_score": 0.35,
                    "transport_score": 0.436,
                    "commute_score": 1,
                    "property_ids": [28570, 28574, 28573, 28572, 28571, 28569, 28568, 28566, 28565],
                    "user_input": {
                        "age": 30,
                        "gender": "male",
                        "job_location": [127.107623723989, 37.5480148978373],
                        "transportation": ["car"],
                        "budget": {
                            "deposit": [5000000, 100000000],
                            "monthly_rent": [0, 800000],
                            "transaction_type": ["월세"],
                            "property_type": ["원룸"],
                            "maintenance_cost": [],
                            "room_type": [],
                            "floor_type": ["지상"],
                            "direction": [],
                            "area": []
                        },
                        "priority": ["transport", "infra", "quiet"],
                        "max_commute_min": 30
                    },
                    "page": 1,
                    "page_size": 10
                }
            }
