import aiohttp
import asyncio
import urllib.parse
from bs4 import BeautifulSoup
import math
import random
import json
import os
from itertools import product
from fake_useragent import UserAgent
import random
import re
from datetime import datetime

# 비동기 세마포어 설정
semaphore = asyncio.Semaphore(5)

# 임시 저장 파일 이름
PROGRESS_FILE = "data/progress.jsonl"

# 거래 유형 매핑
TRADE_TYPE_MAP = {
    "매매": "A1",
    "전세": "B1",
    "월세": "B2",
    "단기임대": "B3",
}

# 부동산 유형 매핑
PROPERTY_TYPE_MAP = {
    "아파트": "APT",
    "오피스텔": "OPST",
    "빌라": "VL",
    "원룸": "OR",
}

# 중간 저장 및 로드
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"processed_articles": []}


def save_article(article):
    with open(PROGRESS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(article, ensure_ascii=False) + "\n")


# 비동기 HTTP 요청
async def fetch(session, url):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        print(f"Fetch Error: {url}\n{e}")
        return None


async def fetch_json(session, url):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()
    except Exception as e:
        print(f"Fetch JSON Error: {url}\n{e}")
        return None


# URL 인코딩
def encode_keyword(keyword):
    return urllib.parse.quote(keyword)


# 위치 정보 파싱
def extract_location_info(response_text):
    soup = str(BeautifulSoup(response_text, "lxml"))
    try:
        value = (
            soup.split("filter: {")[1].split("}")[0].replace(" ", "").replace("'", "")
        )
    except IndexError:
        raise ValueError("위치 정보를 찾을 수 없습니다.")

    return {
        "lat": value.split("lat:")[1].split(",")[0],
        "lon": value.split("lon:")[1].split(",")[0],
        "z": value.split("z:")[1].split(",")[0],
        "cortarNo": value.split("cortarNo:")[1].split(",")[0],
    }


# 클러스터 URL 생성
def build_cluster_url(
    location_info, property_code, trade_code, lat_margin=0.5, lon_margin=0.5
):
    lat = float(location_info["lat"])
    lon = float(location_info["lon"])
    return (
        "https://m.land.naver.com/cluster/clusterList?"
        f"view=atcl&cortarNo={location_info['cortarNo']}&"
        f"rletTpCd={property_code}&tradTpCd={trade_code}&z={location_info['z']}&"
        f"lat={lat}&lon={lon}&"
        f"btm={lat - lat_margin}&lft={lon - lon_margin}&"
        f"top={lat + lat_margin}&rgt={lon + lon_margin}"
    )


# 상세 매물 리스트 URL 생성
def build_article_list_url(
    lgeo, z, lat, lon, count, cortarNo, page, property_code, trade_code
):
    return (
        "https://m.land.naver.com/cluster/ajax/articleList?"
        f"itemId={lgeo}&mapKey=&lgeo={lgeo}&showR0=&"
        f"rletTpCd={property_code}&tradTpCd={trade_code}&z={z}&"
        f"lat={lat}&lon={lon}&totCnt={count}&"
        f"cortarNo={cortarNo}&page={page}"
    )


def refine_summary(item):
    base_img_url = "https://landthumb-phinf.pstatic.net"
    rep_img = item.get("repImgUrl")
    full_rep_img = f"{base_img_url}{rep_img}" if rep_img else None

    return {
        "매물번호": item.get("atclNo"),
        "행정구역코드": item.get("cortarNo"),
        "매물명": item.get("atclNm"),
        "매물상태": item.get("atclStatCd"),
        "매물유형코드": item.get("rletTpCd"),
        "매물유형명": item.get("rletTpNm"),
        "거래유형코드": item.get("tradTpCd"),
        "거래유형명": item.get("tradTpNm"),
        "확인유형": item.get("vrfcTpCd"),
        "층정보": item.get("flrInfo"),
        "보증금": item.get("prc"),
        "월세": item.get("rentPrc"),
        "한글가격": item.get("hanPrc"),
        "공급면적": item.get("spc1"),
        "전용면적": item.get("spc2"),
        "방향": item.get("direction"),
        "매물확인일": item.get("atclCfmYmd"),
        "대표이미지": full_rep_img,
        "썸네일타입": item.get("repImgTpCd"),
        "썸네일": item.get("repImgThumb"),
        "위도": item.get("lat"),
        "경도": item.get("lng"),
        "매물특징": item.get("atclFetrDesc"),
        "매물태그": ", ".join(item.get("tagList", [])),
        "중개사명": item.get("rltrNm"),
        "직거래여부": item.get("directTradYn"),
        "중개사수": item.get("cpCnt"),
        "광고매체명": item.get("cpNm"),
        "중개사무소": item.get("rltrNm"),
        "소요시간": item.get("minute"),
        "상세주소여부": item.get("dtlAddrYn"),
        "상세주소": item.get("dtlAddr"),
        "가상현실노출여부": item.get("isVrExposed"),
    }

# 매물 상세 정보 파싱
def extract_detail_info(soup):
    result = {}

    def get_text(selector):
        element = soup.select_one(selector)
        return element.text.strip() if element else None

    def get_all_texts(selector):
        return [el.text.strip() for el in soup.select(selector)]

    # 매물 번호
    result["매물번호"] = get_text('li:-soup-contains("매물번호") .DataList_definition__d9KY1')

    # 가격 전체
    result["가격"] = get_text(".ArticleSummary_info-price__BD9wv")

    # 보증금/월세 분리
    if result["가격"]:
        price_split = result["가격"].replace(",", "").split("/")
        if len(price_split) == 2:
            result["보증금"] = price_split[0].strip()
            result["월세"] = price_split[1].strip()
        else:
            result["보증금"], result["월세"] = None, None
    else:
        result["보증금"] = result["월세"] = None

    # 관리비 — 금액만
    maintenance_items = soup.select('li:has(.DataList_term__Tks7l:-soup-contains("관리비"))')
    result["관리비"] = None
    for item in maintenance_items:
        value = item.select_one(".DataList_definition__d9KY1").text.strip()
        if "원" in value or "만원" in value:
            result["관리비"] = value
            result["관리비"] = result["관리비"].replace("상세보기", "")
            break

    # 면적
    result["공급면적"] = get_text('li:-soup-contains("공급면적") .DataList_definition__d9KY1')
    result["전용면적"] = get_text('li:-soup-contains("전용면적") .DataList_definition__d9KY1')

    # 층수
    result["층수"] = get_text('li:-soup-contains("층") .DataList_definition__d9KY1')

    # 방향
    result["방향"] = get_text('li:-soup-contains("향") .DataList_definition__d9KY1')

    # 방/욕실 수
    result["방/욕실"] = get_text('li:-soup-contains("방/욕실") .DataList_definition__d9KY1')

    # 복층 여부
    result["복층여부"] = get_text('li:-soup-contains("복층여부") .DataList_definition__d9KY1')

    # 입주 가능일
    result["입주가능일"] = get_text(
        'li:-soup-contains("입주가능일") .DataList_definition__d9KY1'
    )

    # 설명
    result["매물설명"] = get_text(".ArticleSummary_description__5iFRy")

    # 이미지 URL 목록
    result["이미지목록"] = [
        img["src"] for img in soup.select(".ThumbnailMapGroup_image__kG4k5")
    ]

    # 중개사 정보
    result["중개사명"] = get_text(".ArticleAgent_broker-name__IrVqj")
    result["중개사사무소"] = get_text(".ArticleAgent_info-agent__tWe2j")

    broker_phones = soup.select(
        'li:-soup-contains("전화") .ArticleAgent_link-telephone__RPK6B'
    )
    result["중개사전화"] = [phone.text.strip() for phone in broker_phones]

    result["중개사주소"] = get_text('li:-soup-contains("위치") .DataList_definition__d9KY1')
    result["중개사등록번호"] = get_text(
        'li:-soup-contains("등록번호") .DataList_definition__d9KY1'
    )
    result["중개사확인매물수"] = get_text(
        'li:-soup-contains("중개사 매물") .DataList_definition__d9KY1'
    )

    return result

# 매물 저장 형태 변환
def transform_article_to_property_row(article_data):
    summary = article_data["summary"]
    detail = article_data["detail"]

    def parse_floor(floor_str):
        try:
            return int(floor_str.split("/")[0].replace("층", "").strip())
        except:
            return None
    
    def check_top_floor(floor_str):
        if (floor_str.split("/")[0].replace("층", "").strip()) == "고":
            return True
        return False
    
    def check_bottom_floor(floor_str):
        if (floor_str.split("/")[0].replace("층", "").strip()) == "저":
            return True
        return False
    
    def parse_all_floor(floor_str):
        try:
            return int(floor_str.split("/")[1].replace("층", "").strip())
        except:
            return None

    def parse_confirmation_date(date_str):
        try:
            # 예: "25.04.19." → "2025-04-19"
            date_str = date_str.strip().replace(".", "-").strip("-")
            return datetime.strptime("20" + date_str, "%Y-%m-%d").date()
        except:
            return None
    
    def parse_korean_currency(value):
        if not value:  # None, '', 0 등 비어있을 경우
            return 0

        value = str(value).replace("원", "").replace(" ", "").replace(",", "").strip()

        try:
            return int(re.sub(r"[^\d]", "", value)) if re.search(r"\d", value) else 0
        except ValueError:
            print(f"⚠️ [관리비 파싱 실패] 원본 값: {value}")
            return 0
        

    return {
        "monthly_rent_cost": int(summary.get("월세", 0)),
        "deposit": int(summary.get("보증금", 0)),
        "area": float(summary.get("전용면적", 0)),
        "floor": parse_floor(summary.get("층정보", "")),
        "total_floors": parse_all_floor(summary.get("층정보", "")),
        "is_top_floor": check_top_floor(summary.get("층정보", "")),
        "is_bottom_floor": check_bottom_floor(summary.get("층정보", "")),
        "property_type": summary.get("매물유형명"),
        "features": summary.get("매물특징"),
        "direction": summary.get("방향"),
        "location": f"POINT({summary['경도']} {summary['위도']})",
        "description": detail.get("매물설명"),
        "agent_name": detail.get("중개사명"),
        "agent_office": detail.get("중개사사무소"),
        "agent_phone": ", ".join(detail.get("중개사전화", [])),
        "agent_address": detail.get("중개사주소"),
        "agent_registration_no": detail.get("중개사등록번호"),
        "property_number": summary.get("매물번호"),
        "administrative_code": summary.get("행정구역코드"),
        "property_name": summary.get("매물명"),
        "transaction_type": summary.get("거래유형명"),
        "confirmation_type": summary.get("확인유형"),
        "supply_area": float(summary.get("공급면적", 0)),
        "property_confirmation_date": parse_confirmation_date(summary.get("매물확인일", "")).isoformat(),
        "main_image_url": summary.get("대표이미지", ""),
        "photo": detail.get("이미지목록", []),
        "tags": summary.get("매물태그", ""),
        "maintenance_cost": parse_korean_currency(detail.get("관리비", "0원")),
        "rooms_bathrooms": detail.get("방/욕실"),
        "duplex": detail.get("복층여부", "").strip() != "단층" if detail.get("복층여부") else False,
        "available_move_in_date": detail.get("입주가능일", ""),
    }

# 매물 상세 정보
async def fetch_article_detail(session, atcl_no, list_item, existing_atcl_numbers):
    async with semaphore:
        if atcl_no in existing_atcl_numbers:
            print(f"🚫 [중복 건너뜀] atclNo: {atcl_no}")
            return

        url = f"https://m.land.naver.com/article/info/{atcl_no}"
        response_text = await fetch(session, url)

        useful_info = {}
        if response_text:
            soup = BeautifulSoup(response_text, "lxml")
            useful_info = extract_detail_info(soup)

        refined_summary = refine_summary(list_item)

        article_data = {
            "atclNo": atcl_no,
            "summary": refined_summary,
            "detail": useful_info
        }
        
        property_row = transform_article_to_property_row(article_data)

        save_article(property_row)
        existing_atcl_numbers.add(atcl_no)

        print(f"✅ [매물 저장] atclNo: {atcl_no}")

        await asyncio.sleep(random.uniform(0.5, 1.5))

# 매물 목록 처리
async def process_articles(session, article_json, existing_atcl_numbers):
    tasks = []
    body = article_json.get("body", [])
    if not body:
        return

    for item in body:
        atcl_no = item.get("atclNo")
        if atcl_no:
            tasks.append(fetch_article_detail(session, atcl_no, item, existing_atcl_numbers))

    await asyncio.gather(*tasks)

# 클러스터 하나 처리
async def process_single_cluster(session, cluster, cortarNo, property_code, trade_code, existing_atcl_numbers):
    lgeo = cluster["lgeo"]
    count = cluster["count"]
    z = cluster["z"]
    lat = cluster["lat"]
    lon = cluster["lon"]
    total_pages = math.ceil(count / 20)

    print(f"\n[클러스터] lgeo: {lgeo}, 총 매물: {count}, 페이지: {total_pages}")

    for page in range(1, total_pages + 1):
        article_url = build_article_list_url(lgeo, z, lat, lon, count, cortarNo, page, property_code, trade_code)
        article_json = await fetch_json(session, article_url)

        if article_json:
            await process_articles(session, article_json, existing_atcl_numbers)

        await asyncio.sleep(random.uniform(0.5, 1.5))

# 클러스터 병렬 처리
async def process_clusters(session, clusters, cortarNo, property_code, trade_code, existing_atcl_numbers):
    tasks = []

    for cluster in clusters:
        tasks.append(process_single_cluster(session, cluster, cortarNo, property_code, trade_code, existing_atcl_numbers))

    await asyncio.gather(*tasks)

# 조합 처리
async def process_combinations(session, location_info, property_types, trade_types, existing_atcl_numbers):
    combinations = list(product(property_types, trade_types))
    for property_type, trade_type in combinations:
        property_code = PROPERTY_TYPE_MAP.get(property_type, "OR")
        trade_code = TRADE_TYPE_MAP.get(trade_type, "B2")

        print(f"\n[조합] 부동산유형: {property_type} ({property_code}), 거래유형: {trade_type} ({trade_code})")

        cluster_url = build_cluster_url(location_info, property_code, trade_code)
        cluster_json = await fetch_json(session, cluster_url)

        if not cluster_json or "data" not in cluster_json or "ARTICLE" not in cluster_json["data"]:
            print("클러스터 없음")
            continue

        clusters = cluster_json["data"]["ARTICLE"]
        await process_clusters(session, clusters, location_info["cortarNo"], property_code, trade_code, existing_atcl_numbers)

# 기존 매물 번호 로드
def load_existing_atcl_numbers(filepath=PROGRESS_FILE):
    atcl_numbers = set()
    if not os.path.exists(filepath):
        return atcl_numbers

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            try:
                article = json.loads(line)
                atcl_no = article.get("atclNo")
                if atcl_no:
                    atcl_numbers.add(atcl_no)
            except json.JSONDecodeError:
                continue

    print(f"✅ 이미 저장된 매물 수: {len(atcl_numbers)}")
    return atcl_numbers

# 랜덤 User-Agent 생성
ua = UserAgent()

def get_random_headers():
    # Accept-Language 다양화
    accept_language_list = [
        "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "en-US,en;q=0.9,ko;q=0.8",
        "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
        "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "en-GB,en;q=0.9",
    ]
    
    # Accept 헤더 다양화
    accept_list = [
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "text/html,application/xml;q=0.9,image/webp,*/*;q=0.8",
    ]
    
    # Connection 헤더 다양화
    connection_list = [
        "keep-alive",
        "close",
    ]
    
    # Referer 다양화 (실제 페이지 흐름에서 유도)
    referer_list = [
        "https://m.land.naver.com/",
        "https://m.land.naver.com/map/37.5665:126.9780:15/0",
        "https://m.land.naver.com/search/result/서울",
        "https://m.land.naver.com/article/info/{}".format(random.randint(1000000000, 9999999999)),
    ]
    
    # Cache-Control 다양화
    cache_control_list = [
        "max-age=0",
        "no-cache",
        "no-store",
    ]
    
    # Upgrade-Insecure-Requests 다양화
    upgrade_insecure_list = ["1", "0"]

    # DNT (Do Not Track) 랜덤
    dnt_list = ["1", "0"]

    return {
        "User-Agent": ua.random,
        "Accept-Language": random.choice(accept_language_list),
        "Accept": random.choice(accept_list),
        "Connection": random.choice(connection_list),
        "Referer": random.choice(referer_list),
        "Cache-Control": random.choice(cache_control_list),
        "Upgrade-Insecure-Requests": random.choice(upgrade_insecure_list),
        "DNT": random.choice(dnt_list),
        # 실제 쿠키 적용 시 더 좋음
        "Cookie": "cookie",  # 실제 쿠키 있으면 넣기!
    }

# 메인 함수
async def house_crawler(keyword):
    print(f"🏠 [검색어] {keyword}")
    existing_atcl_numbers = load_existing_atcl_numbers()
    cookie_jar = aiohttp.CookieJar()

    async with aiohttp.ClientSession(headers=get_random_headers(), cookie_jar=cookie_jar) as session:
        encoded_keyword = encode_keyword(keyword)
        search_url = f"https://m.land.naver.com/search/result/{encoded_keyword}"
        search_response_text = await fetch(session, search_url)

        if not search_response_text:
            print("검색 결과 없음")
            return

        location_info = extract_location_info(search_response_text)

        property_types = ["원룸"]
        trade_types = ["월세"]

        await process_combinations(session, location_info, property_types, trade_types, existing_atcl_numbers)

        print("모든 작업이 완료되었습니다.")

if __name__ == "__main__":
    asyncio.run(house_crawler("서울시 광진구 광장동"))
