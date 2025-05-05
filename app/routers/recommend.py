from fastapi import APIRouter, Depends
from app.db.session import get_db
from app.models.user_input import UserInput
from app.models.dong_input import DongPropertiesInput
from app.services.recommender import recommend_properties, recommend_dongs
from app.models.property_db import Property
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.area_response import AreaRecommendationResponse
from app.models.property_response import PropertyRecommendationResponse

router = APIRouter()

@router.post(
    "/recommend/area",
    response_model=AreaRecommendationResponse,
    summary="행정동 추천",
    description="""
    행정동 추천 API

    사용자 조건에 따라 서울시의 행정동(dong) 단위 추천 결과 제공
    
    ▷ 전체 추천 흐름
    1. 사용자는 `/recommend/area` API에 나이, 성별, 직장 위치, 교통수단, 예산, 우선순위 정보를 입력
    2. 각 동(dong)은 6개 지표(infra, security, quiet, youth, transport, commute)를 기반으로 점수를 계산
    3. 구(gu) 단위로 동들을 그룹핑하여 추천 결과를 제공
    4. 추천 결과에서 특정 동(dong)을 선택하면 → `/recommend/property` API에 해당 동과 함께 요청 → 개별 매물 리스트 조회 가능
    
    ▷ 입력 데이터
    - age: 사용자 나이
    - gender: 성별 ("male", "female")
    - job_location: 직장 위치 [longitude, latitude]
    - transportation: ["car" | "public"]
    - budget: 예산 조건 (보증금, 월세, 유형 등)
    - priority: 우선 고려 항목 리스트 (최대 3개 선택)
    - max_commute_min: 허용 가능한 최대 통근 시간 (기본값: 30분)

    ▷ 결과 데이터
    - gu : 구 이름
    - dong : 동 이름
    - dong_code : 행정동 코드
    - total_score : 종합 점수
    - property_count : 조건 충족 매물 수
    - commute_min : 평균 통근 시간
    - infra_score, security_score, quiet_score, youth_score, transport_score, commute_score : 지표별 점수
    
    ▷ 지표 산정 방식
    - infra_score : 음식점 수를 행정동 면적으로 나눈 밀도(개/㎢) 지표 
        → 로그 변환 후 MinMaxScaler 정규화, 밀집도가 높을수록 높은 점수
        
    - security_score : CCTV 수를 행정동 면적으로 나눈 밀도 기반 지표 
        → 로그 변환 후 MinMaxScaler 정규화, 조밀하게 CCTV가 배치된 지역에 높은 점수 부여
        
    - transport_score : 버스 정류장 수 + 지하철역 수의 총합 밀도(개/㎢) 지표 
        → 로그 변환 후 MinMaxScaler 정규화, 대중교통 접근성이 높을수록 점수 증가
        
    - quiet_score : 시간 가중 평균을 반영한 생활인구 평균/표준편차 활용 
        → 단위면적당 평균인구와 변동성(표준편차)을 결합, 1 - (0.6 * 정규화 표준편차 + 0.4 * 정규화 평균)로 조용한 정도 표현
        
    - youth_score : 0~39세 인구 비율과 밀도 기반 지표 -> 0.6 * 젊은 인구 비율 정규화 + 0.4 * 로그 밀도 정규화의 혼합 방식
    
    - commute_score : 유클리디언 통근 거리 기반 `exp(-거리/시간)` 감쇠 함수 적용
    
    ▷ total_score 계산 공식
    total_score = Σ (지표 점수 × 개인화 계수 × 우선순위 가중치)
    - 우선순위 가중치: ex) [0.5, 0.3, 0.2]
    - 개인화 계수: 성별/연령 기반으로 일부 항목에 +0.05~0.1 보정

    ▷ 동 정렬 기준 (gu 내부)
    1. total_score 내림차순
    2. property_count 내림차순
    3. commute_min 오름차순

    ▷ 구 정렬 기준
    1. avg_total_score 내림차순
    2. total_property_count 내림차순
    """
)
async def recommend_area(user_input: UserInput, db: AsyncSession = Depends(get_db)):
    return await recommend_dongs(user_input, db)


@router.post(
    "/recommend/property",
    response_model=PropertyRecommendationResponse,
    summary="개별 매물 추천",
    description="""
    개별 매물 추천 API

    특정 동(dong)에 속한 매물 중, 사용자의 예산, 통근 위치, 우선순위에 따라 추천 점수를 계산해 제공
    
    ▷ 사용 흐름
    - 이 API는 `/recommend/area`에서 추천받은 동(dong)의 `property_ids` 리스트를 기반으로 개별 매물들을 추천합니다.
    - ** 반드시 /recommend/area에서 반환받은 `property_ids` 리스트와 함께 해당 동(dong)의 정보 및 사용자 입력(user_input)을 함께 전달해야 합니다.

    ▷ 페이징 처리
    - 반환되는 매물 목록은 `page_size`, `page` 입력값에 따라 분할해서 요청 바랍니다.
    - /recommend/area API에서 반환된 `property_ids` 리스트의 길이를 기반으로 전체 매물 수를 계산하여 페이지 수를 결정합니다.
    - 예: 총 매물이 43개이고, page_size가 10이면 → total_pages = 5 (1~5페이지 가능)
    - 이때, 전체 매물을 확인하려면 page=1부터 5까지, page_size=10으로 연속 요청하면 됩니다. 
    - 이렇게 클라이언트는 필요 시 페이지를 이동하면서 추가 매물 요청이 가능합니다.
    
    ▷ 입력 데이터
    - dong, dong_code: 행정동 이름 및 코드
    - property_ids: 해당 동 내 조건 만족 매물 ID 리스트
    - user_input: 사용자 설정값 (age, gender, budget, commute 등)
    - page, page_size: 페이징 설정

    ▷ 점수 계산 방식
    - total_score = Σ (우선순위 점수 × 개인화 보정 × 우선순위 가중치) + rent_score
    - 거리 기반 점수는 감쇠 함수(exp(-거리/감쇠값)) 적용

    ▷ 점수 항목
    - infra_score : 주변 인프라 거리 기반 점수
    - security_score : CCTV 거리 기반 안전 점수
    - transport_score : 버스/지하철 거리 기반 교통 점수
    - quiet_score : 조용한 환경 점수 (0~1)
    - youth_score : 젊은 인구 밀집도 점수 (0~1)
    - commute_score : 통근 거리 및 시간 감쇠 점수 (0~1)
    - rent_score : 월세 기반 가성비 점수 (최대 100점)
    - score : 위 모든 요소를 종합한 최종 점수

    ▷ 정렬 기준
    - score 내림차순

    ▷ 반환 필드
    - property_id, address, deposit, monthly_rent_cost, maintenance_cost 등 매물 정보
    - commute_min : 통근 시간 (분)
    - infra_count, cctv_count, bus_count, subway_count : 주변 시설물 수
    - 각 점수별 세부 항목 포함 (infra_score 등)
    """
)
async def recommend_property(input_data: DongPropertiesInput, db: AsyncSession = Depends(get_db)):
    result = await recommend_properties(input_data, db)
    return {"result": result}

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.post("/test-input")
async def test_input(user_input: UserInput):
    return {
        "received_input": user_input.dict(),
    }