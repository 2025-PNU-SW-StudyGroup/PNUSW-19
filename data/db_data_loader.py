import psycopg2
import json
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

def safe_get(d, key, default=None):
    return d.get(key) if d.get(key) not in [None, ""] else default

def safe_date(date_str):
    try:
        return datetime.fromisoformat(date_str).date()
    except:
        return None

def insert_property_row(cur, prop):
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
        %(monthly_rent_cost)s, %(deposit)s, %(area)s, %(floor)s, %(total_floors)s, %(room_type)s,
        %(property_type)s, %(features)s, %(direction)s,
        ST_GeomFromText(%(location)s, 4326), %(description)s,
        %(agent_name)s, %(agent_office)s, %(agent_phone)s, %(agent_address)s, %(agent_registration_no)s,
        %(property_number)s, %(administrative_code)s, %(property_name)s, %(transaction_type)s,
        %(confirmation_type)s, %(supply_area)s, %(property_confirmation_date)s,
        %(main_image_url)s, %(maintenance_cost)s, %(rooms_bathrooms)s, %(duplex)s,
        %(available_move_in_date)s
    ) 
    ON CONFLICT (property_number) DO NOTHING
    RETURNING id;
    """
    values = {
        "monthly_rent_cost": safe_get(prop, "monthly_rent_cost", 0),
        "deposit": safe_get(prop, "deposit", 0),
        "area": safe_get(prop, "area"),
        "floor": safe_get(prop, "floor"),
        "total_floors": safe_get(prop, "total_floors"),
        "room_type": safe_get(prop, "room_type"),
        "property_type": safe_get(prop, "property_type"),
        "features": safe_get(prop, "features"),
        "direction": safe_get(prop, "direction"),
        "location": f"POINT({prop['location'].split('(')[1]}" if prop.get("location") else "POINT(0 0)",
        "description": safe_get(prop, "description"),
        "agent_name": safe_get(prop, "agent_name", "미상"),
        "agent_office": safe_get(prop, "agent_office", "미상"),
        "agent_phone": safe_get(prop, "agent_phone", ""),
        "agent_address": safe_get(prop, "agent_address", ""),
        "agent_registration_no": safe_get(prop, "agent_registration_no", ""),
        "property_number": safe_get(prop, "property_number"),
        "administrative_code": safe_get(prop, "administrative_code"),
        "property_name": safe_get(prop, "property_name"),
        "transaction_type": safe_get(prop, "transaction_type"),
        "confirmation_type": safe_get(prop, "confirmation_type"),
        "supply_area": safe_get(prop, "supply_area"),
        "property_confirmation_date": safe_date(prop.get("property_confirmation_date", "")),
        "main_image_url": safe_get(prop, "main_image_url"),
        "maintenance_cost": safe_get(prop, "maintenance_cost", 0),
        "rooms_bathrooms": safe_get(prop, "rooms_bathrooms"),
        "duplex": prop.get("duplex", False),
        "available_move_in_date": safe_get(prop, "available_move_in_date")
    }

    cur.execute(query, values)
    return cur.fetchone()[0]

def insert_tags_and_photos(cur, property_id, tags, photos):
    # 태그 삽입
    if tags:
        for tag in [t.strip() for t in tags.split(",") if t.strip()]:
            cur.execute("INSERT INTO property_tag (property_id, name) VALUES (%s, %s);", (property_id, tag))

    # 사진 삽입
    if photos:
        for idx, photo_url in enumerate(photos):
            if not photo_url:
                continue
            image_type = "main" if idx == 0 else "sub"
            order = idx + 1
            cur.execute("""
                INSERT INTO property_photo (property_id, image_url, image_type, "order")
                VALUES (%s, %s, %s, %s);
            """, (property_id, photo_url, image_type, order))

def load_jsonl_to_postgres(file_path, batch_size=100):
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    cur = conn.cursor()

    with open(file_path, "r", encoding="utf-8") as f:
        batch = []
        for line in f:
            row = json.loads(line.strip())
            batch.append(row)

            if len(batch) >= batch_size:
                process_batch(batch, cur, conn)
                batch = []

        if batch:
            process_batch(batch, cur, conn)

    cur.close()
    conn.close()
    print("✅ 전체 데이터 적재 완료.")

def process_batch(batch, cur, conn):
    for prop in batch:
        try:
            property_number = insert_property_row(cur, prop)
            if property_number:
                insert_tags_and_photos(
                    cur,
                    property_number,
                    prop.get("tags", ""),
                    prop.get("photo", [])
                )
            conn.commit()  # 👉 여기서 커밋!
        except Exception as e:
            conn.rollback()  # 이 row만 롤백
            print(f"⚠️ [삽입 실패] property_number={prop.get('property_number')} → {e}")

# 실행 예시
load_jsonl_to_postgres("data/progress.jsonl")