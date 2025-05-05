import asyncio
import asyncpg
import json
from datetime import datetime
from dotenv import load_dotenv
import os
from tqdm.asyncio import tqdm

load_dotenv()

def safe_get(d, key, default=None):
    return d.get(key) if d.get(key) not in [None, ""] else default

def safe_date(date_str):
    try:
        return datetime.fromisoformat(date_str).date()
    except:
        return None

async def insert_property_row(conn, prop):
    query = """
    INSERT INTO property (
        monthly_rent_cost, deposit, area, floor, total_floor, room_type,
        property_type, features, direction, location, description,
        agent_name, agent_office, agent_phone, agent_address, agent_registration_no,
        property_number, administrative_code, property_name, transaction_type,
        confirmation_type, supply_area, property_confirmation_date,
        main_image_url, maintenance_cost, rooms_bathrooms, duplex,
        available_move_in_date
    ) VALUES (
        $1, $2, $3, $4, $5, $6,
        $7, $8, $9, ST_GeomFromText($10, 4326), $11,
        $12, $13, $14, $15, $16,
        $17, $18, $19, $20,
        $21, $22, $23,
        $24, $25, $26, $27,
        $28
    ) ON CONFLICT (property_number) DO NOTHING
    RETURNING id;
    """

    values = (
        safe_get(prop, "monthly_rent_cost", 0),
        safe_get(prop, "deposit", 0),
        safe_get(prop, "area"),
        safe_get(prop, "floor"),
        safe_get(prop, "total_floors"),
        safe_get(prop, "room_type"),
        safe_get(prop, "property_type"),
        safe_get(prop, "features"),
        safe_get(prop, "direction"),
        f"POINT({prop['location'].split('(')[1]}" if prop.get("location") else "POINT(0 0)",
        safe_get(prop, "description"),
        safe_get(prop, "agent_name", "미상"),
        safe_get(prop, "agent_office", "미상"),
        safe_get(prop, "agent_phone", ""),
        safe_get(prop, "agent_address", ""),
        safe_get(prop, "agent_registration_no", ""),
        safe_get(prop, "property_number"),
        safe_get(prop, "administrative_code"),
        safe_get(prop, "property_name"),
        safe_get(prop, "transaction_type"),
        safe_get(prop, "confirmation_type"),
        safe_get(prop, "supply_area"),
        safe_date(prop.get("property_confirmation_date", "")),
        safe_get(prop, "main_image_url"),
        safe_get(prop, "maintenance_cost", 0),
        safe_get(prop, "rooms_bathrooms"),
        prop.get("duplex", False),
        safe_get(prop, "available_move_in_date")
    )

    row = await conn.fetchrow(query, *values)
    return row["id"] if row else None

async def insert_tags_and_photos(conn, property_id, tags, photos):
    if tags:
        for tag in [t.strip() for t in tags.split(",") if t.strip()]:
            await conn.execute(
                "INSERT INTO property_tag (property_id, name) VALUES ($1, $2);", property_id, tag
            )
    if photos:
        for idx, photo_url in enumerate(photos):
            if not photo_url:
                continue
            image_type = "main" if idx == 0 else "sub"
            order = idx + 1
            await conn.execute(
                """
                INSERT INTO property_photo (property_id, image_url, image_type, "order")
                VALUES ($1, $2, $3, $4);
                """, property_id, photo_url, image_type, order
            )

async def process_single_property(pool, prop, sem, progress):
    async with sem:
        async with pool.acquire() as conn:
            try:
                property_id = await insert_property_row(conn, prop)
                if property_id:
                    await insert_tags_and_photos(conn, property_id, prop.get("tags", ""), prop.get("photo", []))
                    status = "success"
                else:
                    status = "skipped"
            except Exception as e:
                print(f"⚠️ [삽입 실패] property_number={prop.get('property_number')} → {e}")
                status = "fail"
            progress.update(1)
            return status

async def load_jsonl_to_postgres(file_path, max_lines=None, concurrency=10):
    pool = await asyncpg.create_pool(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        min_size=5,
        max_size=concurrency
    )

    with open(file_path, "r", encoding="utf-8") as f:
        lines = list(f)
        if max_lines is not None:
            lines = lines[:max_lines]
        props = [json.loads(line.strip()) for line in lines]

    sem = asyncio.Semaphore(concurrency)
    progress = tqdm(total=len(props), desc="📦 비동기 매물 적재 중", unit="건")
    tasks = [process_single_property(pool, prop, sem, progress) for prop in props]
    results = await asyncio.gather(*tasks)

    await pool.close()
    progress.close()

    success_count = results.count("success")
    fail_count = results.count("fail")
    skipped_count = results.count("skipped")
    print(f"\n✅ 전체 데이터 적재 완료.")
    print(f"   - 총 성공: {success_count}건")
    print(f"   - 총 실패: {fail_count}건")
    print(f"   - 중복 스킵: {skipped_count}건")

# 실행
if __name__ == "__main__":
    asyncio.run(load_jsonl_to_postgres("data/property_crawler/progress.jsonl"))
