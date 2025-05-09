from app.logging_config import *
from fastapi import FastAPI
from app.routers.recommend import router as recommend_router

app = FastAPI(
    title="서울시 1인가구 부동산 추천 시스템 API",
    description="""
    📌 API 흐름 안내

    1. /recommend/area  
       → 사용자 조건(예산, 통근, 우선순위 등)에 따라 추천 동네 리스트 반환  
       → 각 동네는 property_id 목록을 포함

    2. /recommend/property 
       → 선택된 동네의 매물들 중에서 개별 매물에 대한 추천 점수 계산 및 정렬 결과 반환  
       → page, page_size를 통해 페이징 가능

    ▷ 전체 추천 흐름  
    사용자 입력 → 동네 추천(area) → 동네 선택 → 매물 추천(property)
    
    1. 사용자는 /recommend/area API에 나이, 성별, 직장 위치, 교통수단, 예산, 우선순위 정보를 입력
    2. 각 동(dong)은 6개 지표(infra, security, quiet, youth, transport, commute)를 기반으로 점수를 계산
    3. 구(gu) 단위로 동들을 그룹핑하여 추천 결과를 제공
    4. 추천 결과에서 특정 동(dong)을 선택하면 → /recommend/property API에 해당 동과 함께 요청 → 개별 매물 리스트 조회 가능
    
    ------- Update 내역  -------
      1.0.0 : 초기 배포
      1.0.1 : API 문서화 및 버전 관리 추가
      1.0.2 : 유저 선호 우선순위 값 Safety -> Security로 변경
      1.1.0 : Gunicorn 프로덕션 배포
    """,
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
app.include_router(recommend_router)
