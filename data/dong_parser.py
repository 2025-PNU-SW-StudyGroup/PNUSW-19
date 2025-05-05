import asyncio
import aiohttp
import json

BASE_URL = "https://m.land.naver.com/map/getRegionList"

HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "ko,en;q=0.9,en-US;q=0.8",
    "referer": "https://m.land.naver.com/",
    "sec-ch-ua": '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0",
    "x-requested-with": "XMLHttpRequest",
    "cookie": "NNB=your_real_cookie_here; NID_SES=your_real_cookie_here;"
}

SEOUL_CORTAR_NO = "1100000000"

async def fetch_json(session, cortar_no):
    params = {
        "cortarNo": cortar_no,
        "mycortarNo": cortar_no
    }
    async with session.get(BASE_URL, headers=HEADERS, params=params) as response:
        if response.status == 200:
            return await response.json()
        else:
            print(f"❌ 실패: {cortar_no}, 상태코드: {response.status}")
            return None

async def get_seoul_gu_list(session):
    data = await fetch_json(session, SEOUL_CORTAR_NO)
    if data:
        return data["result"]["list"]
    return []

async def get_dong_list(session, gu):
    data = await fetch_json(session, gu["CortarNo"])
    if data:
        return {
            "gu": gu["CortarNm"],
            "gu_code": gu["CortarNo"],
            "dong_list": [
                {"dong": dong["CortarNm"], "dong_code": dong["CortarNo"]}
                for dong in data["result"]["list"]
            ]
        }
    return {
        "gu": gu["CortarNm"],
        "gu_code": gu["CortarNo"],
        "dong_list": []
    }

async def main():
    async with aiohttp.ClientSession() as session:
        gu_list = await get_seoul_gu_list(session)
        print(f"서울시 구 수: {len(gu_list)}")

        tasks = [get_dong_list(session, gu) for gu in gu_list]
        results = await asyncio.gather(*tasks)

        with open("seoul_dong_list_with_code.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print("✅ 저장 완료: seoul_dong_list_with_code.json")

if __name__ == "__main__":
    asyncio.run(main())