from pydantic import BaseModel, Field
from typing import List, Dict

class AvgScores(BaseModel):
    infra_score: float
    security_score: float
    quiet_score: float
    youth_score: float
    transport_score: float
    commute_score: float

class RecommendedDong(BaseModel):
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

class RecommendedArea(BaseModel):
    gu: str
    gu_code: str
    avg_total_score: float
    total_property_count: int
    avg_scores: AvgScores
    dong_list: List[RecommendedDong]

class AreaRecommendationResponse(BaseModel):
    recommended_area: List[RecommendedArea]

    class Config:
        json_schema_extra = {
            "example": {
                "recommended_area": [
                    {
                        "gu": "광진구",
                        "gu_code": "11215",
                        "avg_total_score": 0.723,
                        "total_property_count": 39,
                        "avg_scores": {
                            "infra_score": 0.432,
                            "security_score": 0.621,
                            "quiet_score": 0.812,
                            "youth_score": 0.295,
                            "transport_score": 0.444,
                            "commute_score": 0.982
                        },
                        "dong_list": [
                            {
                                "dong": "광장동",
                                "dong_code": "1121510400",
                                "total_score": 0.8,
                                "property_count": 13,
                                "commute_min": 1.55,
                                "infra_score": 0.424,
                                "security_score": 0.655,
                                "quiet_score": 0.833,
                                "youth_score": 0.35,
                                "transport_score": 0.436,
                                "commute_score": 1,
                                "property_ids": [
                                    28570, 28574, 28573, 28572, 28571, 28569, 28568, 28566, 28565
                                ]
                            }
                        ]
                    }
                ]
            }
        }
