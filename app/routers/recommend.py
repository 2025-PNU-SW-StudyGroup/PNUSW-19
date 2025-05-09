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

router = APIRouter(tags=["추천 API"])

@router.post(
    "/recommend/area",
    response_model=AreaRecommendationResponse,
    summary="행정동 추천",
    description="""
    행정동 추천 API

    사용자 조건에 따라 서울시의 행정동(dong) 단위 추천 결과 제공
    
    ▷ 입력 데이터
        - (필수) age : 사용자 나이. 예) 30
        
        - (필수) gender : 성별. male 또는 female
        
        - (필수) job_location : 직장 위치. [경도, 위도] 형식 좌표값. 
            예) [127.1, 37.5]
        
        - (필수) transportation : 주요 통근 수단. 'car' (자가) 또는 'public' (대중교통) 
            예) ["car"]
        
        - (필수) budget : 예산 조건
            : 옵션이지만, budget 자체는 필수 입력값
            : 조건을 설정하지 않을 경우, 빈 리스트([])로 입력
            : 비어있는 값을 보낼 경우, 전체 범위 리턴
            : 범위 값 중, 하나만 입력할 경우, 해당 값을 최대값으로 조건을 설정
            
            - deposit : 보증금 범위. 예) [0, 100000000]
            - monthly_rent : 월세 범위. 예) [0, 800000]
            - maintenance_cost : 관리비 범위. 예) [0, 100000]
            - transaction_type : 거래 유형. 예) ["월세", "전세"]
            - property_type : 주택 유형. 예) ["원룸", "빌라", "오피스텔"]
            - room_type : 방 구조. 예) ["원룸", "투룸", "기타 or 그 이상 (아무 문자열)"] 내부에서 Else로 원룸, 투룸이 아닌 건 전부 다 기타로 처리됨.
            - floor_type : 층 구분. 예) ["지상", "반지하", "옥탑방"]
            - direction : 방향. 예) ["동", "서", "남", "북"] 남동향 -> ["남"], ["동"]에서 모두 검색됨. (글씨 포함 여부 검색 기반)
            - area : 전용면적 범위 (제곱미터단위). 예) [10, 20]
            
        - (옵션) priority : 추천 시 고려할 항목 우선순위 (최대 3개까지)
            우선순위 데이터가 없을 시, 자동으로 설정된 기본값으로 추천
            한개, 두개, 세개 모두 가능
            예 ) ["commute"]
            예 ) ["infra", "security"]
            예 ) ["quiet", "youth", "commute"]
            
            - 전체 입력가능한 priority 항목
            ["infra", "security", "transport", "quiet", "youth", "commute"]

        - (옵션) max_commute_min : 허용 가능한 최대 통근 시간 (분 단위). 
           지정되지 않을시, 기본값 30분 내의 범위에서 추천


    ▷ 결과 데이터
    - gu : 구 이름
    - dong : 동 이름
    - dong_code : 행정동 코드
    - total_score : 종합 점수
    - property_count : 조건 충족 매물 수
    - commute_min : 평균 통근 시간
    - infra_score, security_score, quiet_score, youth_score, transport_score, commute_score : 지표별 점수
    - dong_list : 추천된 동(dong) 리스트
        - property_ids : 해당 동(dong) 내 조건 충족 매물 ID 리스트
    
    ▷ 지표 산정 방식
    - infra_score : 음식점 수를 행정동 면적으로 나눈 밀도(개/㎢) 지표 
        → 로그 변환 후 MinMaxScaler 정규화, 밀집도가 높을수록 높은 점수
        
    - security_score : CCTV 수를 행정동 면적으로 나눈 밀도 기반 지표 + 구별 범죄율 보정
        → 로그 변환 후 MinMaxScaler 정규화, 상대적으로 범죄율이 낮고 조밀하게 CCTV가 배치된 지역에 높은 점수 부여
        
    - transport_score : 버스 정류장 수 + 지하철역 수의 총합 밀도(개/㎢) 지표 
        → 로그 변환 후 MinMaxScaler 정규화, 대중교통 접근성이 높을수록 점수 증가
        
    - quiet_score : 시간 가중 평균을 반영한 생활인구 평균/표준편차 활용 
        → 단위면적당 평균인구와 변동성(표준편차)을 결합, 1 - (0.6 * 정규화 표준편차 + 0.4 * 정규화 평균)로 조용한 정도 표현
        
    - youth_score : 전체 인구 대비 0~39세 인구 비율과 밀도 기반 지표 -> 0.6 * 젊은 인구 비율 정규화 + 0.4 * 로그 밀도 정규화의 혼합 방식
    
    - commute_score : 유클리디언 통근 거리 기반 `exp(-거리/시간)` 감쇠 함수 적용
    
    ▷ total_score 계산 공식
    total_score = Σ (지표 점수 × 개인화 계수 × 우선순위 가중치) 
    - 우선순위 가중치: ex) [0.5, 0.3, 0.2]
    - 개인화 계수: 성별/연령 기반으로 일부 항목에 +0.05~0.1 보정

    ▷ 구 정렬 기준
    1. avg_total_score 내림차순
    2. total_property_count 내림차순
    
    ▷ 동 정렬 기준
    1. total_score 내림차순
    2. property_count 내림차순
    3. commute_min 오름차순
    
    **** 아래 Example 요청 파라미터 참고. ****
    예시 데이터에 입력한 직장 위치는 서울시 광진구 광장동에 위치한 신광빌딩이라는 곳.
    - 서울 광진구 아차산로76길 5
    {
        "age": 30,
        "gender": "male",
        "job_location": [127.107623723989, 37.5480148978373],
        "transportation": ["car"],
        "budget": {
            "deposit": [5000000, 100000000],
            "monthly_rent": [0, 800000],
            "property_type" : ["원룸"],
            "transaction_type": ["월세"],
            "maintenance_cost": [],
            "room_type": [],
            "floor_type": ["지상"],
            "direction": [],
            "area": []
        },
        "priority": ["commute", "infra", "security"],
        "max_commute_min": 30
    }
    """
)
async def recommend_area(user_input: UserInput, db: AsyncSession = Depends(get_db)):
    return await recommend_dongs(user_input, db)


@router.post(
    "/recommend/property",
    summary="개별 매물 추천",
    description="""
    개별 매물 추천 API

    특정 동(dong)에 속한 매물 중, 사용자의 예산, 통근 위치, 우선순위에 따라 추천 점수를 계산해 제공
    
    ▷ 사용 방법
    - 이 API는 `/recommend/area`에서 추천받은 동(dong)의 `property_ids` 리스트를 기반으로 개별 매물들을 추천합니다.
    - ** 반드시 /recommend/area에서 반환받은 `property_ids` 리스트와 함께 해당 동(dong)의 정보 및 사용자 입력(user_input)을 함께 전달해야 합니다.

    ▷ 페이징 처리
    - 반환되는 매물 목록은 `page_size`, `page` 입력값에 따라 분할해서 요청 바랍니다.
    - /recommend/area API에서 반환된 `property_ids` 리스트의 길이를 기반으로 전체 매물 수를 계산하여 페이지 수를 결정합니다.
    - 예: 총 매물이 43개이고, page_size가 10이면 → total_pages = 5 (1~5페이지 가능)
    - 이때, 전체 매물을 확인하려면 page=1부터 5까지, page_size=10으로 연속 요청하면 됩니다. 
    - 이렇게 클라이언트는 필요 시 페이지를 이동하면서 추가 매물 요청이 가능
    
    ▷ 입력 데이터
    - dong, dong_code: 행정동 이름 및 코드
    - property_ids: 해당 동 내 조건 만족 매물 ID 리스트
    - user_input: 이전 사용자 설정값 (age, gender, budget, commute 등)
    - page, page_size: 페이징 설정

    ▷ 점수 계산 방식
    - total_score = Σ (우선순위 점수 × 개인화 보정 × 우선순위 가중치) + 매물별 옵션 점수 보정
    - 거리 기반 점수는 감쇠 함수(exp(-거리/감쇠값)) 적용
    - 매물별 옵션 점수 보정: 월세/보증금/관리비/시설 기반으로 +0.1~0.3 보정

    ▷ 점수 항목
    - infra_score : 주변 인프라 거리 기반 점수
    - security_score : CCTV+구별 범죄율 기반 안전 점수
    - transport_score : 버스/지하철 거리 기반 교통 점수
    - quiet_score : 조용한 환경 점수 (0~1)
    - youth_score : 젊은 인구 밀집도 점수 (0~1)
    - commute_score : 통근 거리 및 시간 감쇠 점수 (0~1)
    - score : 위 모든 요소를 종합한 최종 점수

    ▷ 정렬 기준
    - score 내림차순

    ▷ 반환 필드
    - property_id, address, deposit, monthly_rent_cost, maintenance_cost 등 매물 정보
    - commute_min : 통근 시간 (분)
    - infra_count, cctv_count, bus_count, subway_count : 주변 시설물 수 및 평균 거리
    - 각 점수별 세부 항목 포함 (infra_score 등)
    
    -------------[업데이트 내역]-------------
    - 거리 기반 감쇠 점수 개선 : 기존 지수 함수에서 1 / (1 + dist / decay) sigmoid 함수로 완만하게 변경
    - 거리 + 개수 + 동 단위 특성 반영한 복합 스코어 반영 : infra_score, security_score, transport_score 등은 다음 3요소의 가중 평균으로 계산
        base_score: 거리 기반 감쇠 점수
        count_score: 시설 수에 따른 점수 (로그 정규화)
        dong_score: 해당 행정동의 전체 특성 점수
        (base 70%, count 10%, dong 20%)
    - 교통 점수는 버스 + 지하철 가중 평균 버스점수 * 0.4 + 지하철점수 * 0.6
    - 조용함 점수 (quiet_score) 양방향 조정 개선
        기본은 해당 동의 조용함 점수 (quiet_score_map)
        주변 음식점 수와 평균 거리 기반으로 조용하면 보너스, 복잡하면 감점
        이상적인 조용함 기준:
        음식점 개수 ≈ 50개, 평균 거리 ≈ 500m
        이 기준보다 멀고 적으면 보너스, 가깝고 많으면 페널티가 부여됨
        조정값은 -0.15 ~ +0.15 사이로 제한되어, 조용함 점수를 자연스럽게 부드럽게 조정

    
    **** 아래 Example value 요청 파라미터 참고. ****
    {
        "dong": "광장동",
        "dong_code": "1121510400",
        "total_score": 0.8,
        "property_count": 9,
        "commute_min": 1.55,
        "infra_score": 0.424,
        "security_score": 0.655,
        "quiet_score": 0.833,
        "youth_score": 0.35,
        "transport_score": 0.436,
        "commute_score": 1,
        "property_ids": [
            28570,
                    28574,
                    28573,
                    28572,
                    28571,
                    28569,
                    28568,
                    28566,
                    28565
        ],
        "user_input": {
            "age": 30,
            "gender": "male",
            "job_location": [127.107623723989, 37.5480148978373],
            "transportation": ["car"],
            "budget": {
            "deposit": [5000000, 100000000],
            "monthly_rent": [0, 800000],
            "transaction_type": ["월세"],
            "property_type" : ["원룸"],
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
    """
)
async def recommend_property(input_data: DongPropertiesInput, db: AsyncSession = Depends(get_db)):
    result = await recommend_properties(input_data, db)
    return {"result": result}

@router.get("/health", summary="Health Check", description="API 상태 확인, 정상 결과 : 200 OK")
async def health_check():
    return {"status": "ok"}

@router.post("/test-input", summary="입력값 테스트", description="입력값을 테스트하는 API, 입력값을 그대로 반환")
async def test_input(user_input: UserInput):
    return {
        "received_input": user_input.dict(),
    }