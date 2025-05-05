from pydantic import BaseModel, Field
from typing import List, Literal

PriorityType = Literal["infra", "safety", "transport", "quiet", "youth", "commute"]
TransportType = Literal["car", "public"]

from enum import Enum

class Gender(str, Enum):
    male = "male"
    female = "female"

class Budget(BaseModel):
    deposit: List[int] = [] # e.g., [0, 100000000]
    monthly_rent: List[int] = [] # e.g., [0, 100000]
    maintenance_cost: List[int] = []  # e.g., [0, 100000]
    transaction_type: List[str] = []  # e.g., ["전세", "월세"]
    property_type: List[str] = [] # e.g., ["원룸", "빌라", "오피스텔"]
    room_type: List[str] = []  # e.g., ["원룸", "투룸"]
    floor_type: List[str] = []  # e.g., ["지상", "반지하", "옥탑"]
    direction: List[str]  # e.g., ["남향", "북향", "동향", "서향"]
    area: List[int] = []  # e.g., [10, 20] (m2 미터제곱)
    

class UserInput(BaseModel):
    age: int # e.g., 30
    gender: Gender  # e.g., male, female
    job_location: List[float]  # [lng, lat]
    transportation: List[TransportType]  # e.g., ["car", "public"]
    budget: Budget
    priority: List[PriorityType]  # e.g., ["infra", "safety", "transport", "quiet", "youth", "commute"]
    max_commute_min: int = Field(30, description="최대 통근 시간(분), 기본값은 30분") # e.g., 30 (minutes)
    
    class Config:
            json_schema_extra  = {
                "example": {
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
                    "priority": ["commute", "infra", "quiet"],
                    "max_commute_min": 30
                }
            }