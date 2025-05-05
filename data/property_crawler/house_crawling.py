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
import time

# 비동기 세마포어 설정
semaphore = asyncio.Semaphore(5)

# 최대 재시도 횟수
max_retries=3

# 요청 카운터
request_counter = 0

# 임시 저장 파일 이름
PROGRESS_FILE = "data/property_crawler/progress.jsonl"

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
            if response.status == 307:
                print("[307 Too Many Requests] 대기 중...")
                await asyncio.sleep(random.uniform(30, 60))  # 과도 요청 감지 시 대기
                return None
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        print(f"Fetch Error: {url}\n{e}")
        return None


async def fetch_json(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 429:
                print("[307 Too Many Requests] 대기 중...")
                await asyncio.sleep(random.uniform(30, 60))  # 과도 요청 감지 시 대기
                return None
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
    location_info, property_code, trade_code, lat_margin=0.3, lon_margin=0.3
):
    lat = float(location_info["lat"])
    lon = float(location_info["lon"])
    time.sleep(0.5)
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
    time.sleep(0.5)
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

    # 매물 정보 추출
    def extract_value_by_term(term_text):
        for li in soup.select("li"):
            term_div = li.find(
                lambda tag: tag.name == "div"
                and any(
                    cls.startswith("DataList_term__") for cls in tag.get("class", [])
                )
                and term_text in tag.get_text()
            )
            if term_div:
                divs = li.find_all("div", recursive=False)
                if len(divs) >= 2:
                    content_div = divs[1]

                    # 중첩 div 안의 데이터 추출
                    value_candidate = content_div.find(
                        lambda tag: tag.name == "div" and tag.get_text(strip=True)
                    )
                    if value_candidate:
                        for tag in value_candidate.find_all(
                            ["button", "svg", "span"], recursive=True
                        ):
                            tag.decompose()
                        return value_candidate.get_text(strip=True)

                    # 기본 처리 (fallback)
                    for tag in content_div.find_all(
                        ["button", "svg", "span", "div"], recursive=True
                    ):
                        tag.decompose()
                    return content_div.get_text(strip=True)
        return None

    # 관리비 처리
    def extract_maintenance_fee(soup):
        for li in soup.select("li"):
            term_div = li.find(
                lambda tag: tag.name == "div"
                and any(
                    cls.startswith("DataList_term__") for cls in tag.get("class", [])
                )
                and tag.get_text(strip=True) == "관리비"
            )
            if not term_div:
                continue

            definition_div = li.find(
                lambda tag: tag.name == "div"
                and any(
                    cls.startswith("DataList_definition__")
                    for cls in tag.get("class", [])
                )
            )
            if not definition_div:
                continue

            value_div = definition_div.find(
                lambda tag: tag.name == "div"
                and any(char.isdigit() for char in tag.get_text())
            )
            if value_div:
                for tag in value_div.find_all(
                    ["button", "svg", "span"], recursive=True
                ):
                    tag.decompose()
                return value_div.get_text(strip=True)

            # fallback
            for tag in definition_div.find_all(
                ["button", "svg", "span", "div"], recursive=True
            ):
                tag.decompose()
            return definition_div.get_text(strip=True)
        return None

    # 중개사 정보 처리
    def extract_agent_info():
        agent_info = {}
        broker_info = soup.find(
            lambda tag: tag.name == "div"
            and any("ArticleAgent_info-agent" in cls for cls in tag.get("class", []))
        )
        if broker_info:
            broker_name_tag = broker_info.find(
                lambda tag: tag.name == "b"
                and any("broker-name" in cls for cls in tag.get("class", []))
            )
            agent_info["중개사명"] = (
                broker_name_tag.get_text(strip=True) if broker_name_tag else None
            )
            if agent_info["중개사명"]:
                broker_info_text = broker_info.get_text(strip=True).replace(
                    agent_info["중개사명"], ""
                )
                agent_info["중개사사무소"] = broker_info_text.strip()
            else:
                agent_info["중개사사무소"] = broker_info.get_text(strip=True)
        else:
            agent_info["중개사명"] = agent_info["중개사사무소"] = None
        return agent_info

    # 중개사 전화번호 처리
    def extract_agent_phones():
        return [a.get_text(strip=True) for a in soup.select("a[href^='tel:']")]

    # 매물 설명 처리
    def extract_description():
        desc_span = soup.find(
            lambda tag: tag.name == "span"
            and any("description" in cls for cls in tag.get("class", []))
        )
        return desc_span.get_text(strip=True) if desc_span else None

    # 이미지 목록 처리
    def extract_images():
        return [
            img["src"]
            for img in soup.find_all("img")
            if img.has_attr("src")
            and "thumb" in img["src"]
            and "cropImage" not in img["src"]
        ]

    # 가격 처리
    result["가격"] = extract_value_by_term("보증금/월세") or extract_value_by_term(
        "전세가"
    )
    if result["가격"] and "/" in result["가격"]:
        parts = result["가격"].replace(",", "").split("/")
        result["보증금"] = parts[0].strip()
        result["월세"] = parts[1].strip() if len(parts) > 1 else None
    else:
        result["보증금"] = result["가격"]
        result["월세"] = None

    # 일반 항목
    result["관리비"] = extract_maintenance_fee(soup)
    result["공급면적"] = extract_value_by_term("공급면적")
    result["전용면적"] = extract_value_by_term("전용면적")
    result["층수"] = extract_value_by_term("층")
    result["방향"] = extract_value_by_term("향")
    result["방/욕실"] = extract_value_by_term("방/욕실")
    result["복층여부"] = extract_value_by_term("복층여부")
    result["입주가능일"] = extract_value_by_term("입주가능일")
    result["매물번호"] = extract_value_by_term("매물번호")

    # 설명
    result["매물설명"] = extract_description()

    # 이미지
    result["이미지목록"] = extract_images()

    # 중개사 정보
    result.update(extract_agent_info())
    result["중개사전화"] = extract_agent_phones()
    result["중개사주소"] = extract_value_by_term("위치")
    result["중개사등록번호"] = extract_value_by_term("등록번호")
    result["중개사확인매물수"] = extract_value_by_term("중개사 매물")

    return result


# 매물 저장 형태 변환
def transform_article_to_property_row(article_data):
    summary = article_data["summary"]
    detail = article_data["detail"]

    # 층 정보 파싱
    def parse_floor(floor_str):
        if not floor_str:
            return None
        try:
            return int(floor_str.split("/")[0].replace("층", "").strip())
        except:
            return None

    def check_top_floor(floor_str):
        if not floor_str:
            return False
        if (floor_str.split("/")[0].replace("층", "").strip()) == "고":
            return True
        elif (floor_str.split("/")[0].replace("층", "").strip()) == "옥탑":
            return True
        elif (floor_str.split("/")[0].replace("층", "").strip()) == "옥탑방":
            return True
        return False

    def check_bottom_floor(floor_str):
        if not floor_str:
            return False
        if "B" in (floor_str.split("/")[0]):
            return True
        elif (floor_str.split("/")[0].replace("층", "").strip()) == "저":
            return True
        return False

    def check_room_type(floor_str):
        try:
            if check_bottom_floor(floor_str):
                return "반지하"
            elif check_top_floor(floor_str):
                return "옥탑방"
            else:
                return "지상"
        except:
            return "기타"

    def parse_all_floor(floor_str):
        try:
            return int(floor_str.split("/")[1].replace("층", "").strip())
        except:
            return None

    # 매물 확인일 파싱
    def parse_confirmation_date(date_str):
        try:
            # 예: "25.04.19." → "2025-04-19"
            date_str = date_str.strip().replace(".", "-").strip("-")
            return datetime.strptime("20" + date_str, "%Y-%m-%d").date()
        except:
            return None

    # 관리비 파싱
    def parse_korean_currency(value):
        if not value:
            return 0
        value = str(value).replace("원", "").replace(",", "").replace(" ", "").strip()
        try:
            # 1. 혼합 표기: "19만8000", "3만500", 등
            if "만" in value:
                만_split = value.split("만")
                만 = int(만_split[0]) * 10000
                나머지 = (
                    int(re.sub(r"[^\d]", "", 만_split[1]))
                    if len(만_split) > 1 and 만_split[1]
                    else 0
                )
                return 만 + 나머지

            elif "천" in value:
                return int(float(value.replace("천", "")) * 1000)

            else:
                return (
                    int(re.sub(r"[^\d]", "", value)) if re.search(r"\d", value) else 0
                )

        except ValueError:
            print(f"⚠️ [관리비 파싱 실패] 원본 값: {value}")
            return 0

    def safe_float(value):
        try:
            value = str(value).replace(",", "").strip()
            return float(value) if value not in ["", "-", "없음", None] else 0.0
        except ValueError:
            return 0.0

    return {
        "monthly_rent_cost": int(summary.get("월세", 0)) * 10000,
        "deposit": int(summary.get("보증금", 0)) * 10000,
        "area": safe_float(summary.get("전용면적")),
        "floor": parse_floor(summary.get("층정보", "")),
        "total_floors": parse_all_floor(summary.get("층정보", "")),
        "room_type": check_room_type(summary.get("층정보", "")),
        "property_type": summary.get("매물유형명"),
        "features": summary.get("매물특징"),
        "direction": summary.get("방향"),
        "location": f"POINT({summary['경도']} {summary['위도']})",
        "description": detail.get("매물설명"),
        "agent_name": detail.get("중개사명"),
        "agent_office": detail.get("중개사사무소"),
        "agent_phone": ", ".join(detail.get("중개사전화", [])),
        "agent_address": (detail.get("중개사주소") or "").replace("지도보기", "").strip(),
        "agent_registration_no": detail.get("중개사등록번호"),
        "property_number": summary.get("매물번호"),
        "administrative_code": summary.get("행정구역코드"),
        "property_name": summary.get("매물명"),
        "transaction_type": summary.get("거래유형명"),
        "confirmation_type": summary.get("확인유형"),
        "supply_area": safe_float(summary.get("공급면적")),
        "property_confirmation_date": parse_confirmation_date(
            summary.get("매물확인일", "")
        ).isoformat(),
        "main_image_url": summary.get("대표이미지", ""),
        "photo": detail.get("이미지목록", []),
        "tags": summary.get("매물태그", ""),
        "maintenance_cost": parse_korean_currency(detail.get("관리비", "0원")),
        "rooms_bathrooms": detail.get("방/욕실"),
        "duplex": (
            detail.get("복층여부", "").strip() != "단층"
            if detail.get("복층여부")
            else False
        ),
        "available_move_in_date": detail.get("입주가능일", ""),
    }


# 매물 상세 정보
async def fetch_article_detail(session, atcl_no, list_item, existing_atcl_numbers):
    async with semaphore:
        if atcl_no in existing_atcl_numbers:
            return

        url = f"https://m.land.naver.com/article/info/{atcl_no}"
        
        for attempt in range(1, max_retries + 1):
            try:
                response_text = await fetch(session, url)

                if not response_text:
                    raise ValueError("빈 응답")

                soup = BeautifulSoup(response_text, "lxml")
                useful_info = extract_detail_info(soup)
                refined_summary = refine_summary(list_item)

                article_data = {
                    "atclNo": atcl_no,
                    "summary": refined_summary,
                    "detail": useful_info,
                }

                property_row = transform_article_to_property_row(article_data)
                save_article(property_row)
                existing_atcl_numbers.add(atcl_no)

                print(f"[매물 저장] atclNo: {atcl_no}")
                await asyncio.sleep(random.uniform(2.0, 4.0))
                break  # 성공 시 루프 탈출

            except Exception as e:
                print(f"[상세정보 실패] atclNo: {atcl_no}, 시도 {attempt}/{max_retries} — {e}")
                if attempt < max_retries:
                    await asyncio.sleep(1.5 * attempt)  # 재시도 전 점진적 대기
                else:
                    print(f"[최종 실패] atclNo: {atcl_no} — 스킵")



# 매물 목록 처리
async def process_articles(session, article_json, existing_atcl_numbers):
    global request_counter
    tasks = []
    body = article_json.get("body", [])
    if not body:
        return

    for item in body:
        atcl_no = item.get("atclNo")
        if atcl_no:
            tasks.append(
                fetch_article_detail(session, atcl_no, item, existing_atcl_numbers)
            )
            if atcl_no in existing_atcl_numbers:
                continue
            request_counter += 1
            if request_counter % 50 == 0:
                print(f"[요청 {request_counter}개] 과부하 방지 대기 중...")
                await asyncio.sleep(random.uniform(15.0, 20.0))
    await asyncio.gather(*tasks)


# 클러스터 하나 처리
async def process_single_cluster(
    session, cluster, cortarNo, property_code, trade_code, existing_atcl_numbers
):
    lgeo = cluster["lgeo"]
    count = cluster["count"]
    z = cluster["z"]
    lat = cluster["lat"]
    lon = cluster["lon"]
    total_pages = math.ceil(count / 20)

    print(f"\n[클러스터] lgeo: {lgeo}, 총 매물: {count}, 페이지: {total_pages}")

    for page in range(1, total_pages + 1):
        article_url = build_article_list_url(
            lgeo, z, lat, lon, count, cortarNo, page, property_code, trade_code
        )
        print(f"[매물 목록] 페이지 {page}/{total_pages} - URL: {article_url}")
        article_json = await fetch_json(session, article_url)
        if article_json:
            await process_articles(session, article_json, existing_atcl_numbers)
        await asyncio.sleep(random.uniform(2.0, 8.0))


# 클러스터 병렬 처리
async def process_clusters(
    session, clusters, cortarNo, property_code, trade_code, existing_atcl_numbers
):
    tasks = []

    for i, cluster in enumerate(clusters):
        await process_single_cluster(
            session, cluster, cortarNo, property_code, trade_code, existing_atcl_numbers
        )

        if (i + 1) % 5 == 0:  # 5개 클러스터마다 긴 슬립
            print(f"[클러스터 {i + 1}개] 대기 중...")
            await asyncio.sleep(random.uniform(10.0, 15.0))
        else:
            await asyncio.sleep(random.uniform(3.0, 5.0))

    await asyncio.gather(*tasks)


# 조합 처리
async def process_combinations(
    session, location_info, property_types, trade_types, existing_atcl_numbers
):
    combinations = list(product(property_types, trade_types))
    for property_type, trade_type in combinations:
        property_code = PROPERTY_TYPE_MAP.get(property_type, "OR")
        trade_code = TRADE_TYPE_MAP.get(trade_type, "B2")

        print(
            f"\n[조합] 부동산유형: {property_type} ({property_code}), 거래유형: {trade_type} ({trade_code})"
        )

        cluster_url = build_cluster_url(location_info, property_code, trade_code)
        cluster_json = await fetch_json(session, cluster_url)

        if (
            not cluster_json
            or "data" not in cluster_json
            or "ARTICLE" not in cluster_json["data"]
        ):
            print("클러스터 없음")
            continue

        clusters = cluster_json["data"]["ARTICLE"]
        #클러스터 갯수 제한
        if len(clusters) > 10:
            clusters = clusters[:10]
        
        print(f"총 클러스터 수: {len(clusters)}")
        print((f"클러스터 URL: {cluster_url}"))
        await process_clusters(
            session,
            clusters,
            location_info["cortarNo"],
            property_code,
            trade_code,
            existing_atcl_numbers,
        )
        await asyncio.sleep(random.uniform(10.0, 15.0))


# 기존 매물 번호 로드
def load_existing_atcl_numbers(filepath=PROGRESS_FILE):
    atcl_numbers = set()
    if not os.path.exists(filepath):
        return atcl_numbers

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            try:
                article = json.loads(line)
                atcl_no = article.get("property_number")
                if atcl_no:
                    atcl_numbers.add(atcl_no)
            except json.JSONDecodeError:
                continue

    print(f"이미 저장된 매물 수: {len(atcl_numbers)}")
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
        "https://m.land.naver.com/article/info/{}".format(
            random.randint(1000000000, 9999999999)
        ),
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
        "Cookie": "cookie",
    }


# 메인 함수
async def house_crawler(keyword):
    print(f"[검색어] {keyword}")
    existing_atcl_numbers = load_existing_atcl_numbers()
    cookie_jar = aiohttp.CookieJar()

    async with aiohttp.ClientSession(
        headers=get_random_headers(), cookie_jar=cookie_jar
    ) as session:
        encoded_keyword = encode_keyword(keyword)
        search_url = f"https://m.land.naver.com/search/result/{encoded_keyword}"
        search_response_text = await fetch(session, search_url)

        if not search_response_text:
            print("검색 결과 없음")
            return

        location_info = extract_location_info(search_response_text)

        property_types = ["원룸","오피스텔","빌라"]
        trade_types = ["월세","전세"]

        await process_combinations(
            session, location_info, property_types, trade_types, existing_atcl_numbers
        )

        print("모든 작업이 완료되었습니다.")

async def get_seoul_property():
    with open("data/seoul_dong_list.json", "r", encoding="utf-8") as f:
        seoul_dong_data = json.load(f)

    all_keywords = []
    for gu_info in seoul_dong_data:
        gu = gu_info["gu"]
        for dong in gu_info["dong_list"]:
            keyword = f"서울시 {gu} {dong}"
            all_keywords.append(keyword)

    for keyword in all_keywords:
        print(f"\n\n============================")
        print(f"[크롤링 시작] {keyword}")
        print(f"============================\n")
        try:
            await house_crawler(keyword)
            # 동별 크롤링 사이에 약간 텀을 줘서 봇 차단 방지
            await asyncio.sleep(60)
        except Exception as e:
            print(f"오류 발생 - {keyword}: {e}")
            continue

if __name__ == "__main__":
    asyncio.run(get_seoul_property())

# if __name__ == "__main__":
    # asyncio.run(house_crawler("서울시 관악구 신림동"))