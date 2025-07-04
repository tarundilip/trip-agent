import aiosqlite
import os
import json
from datetime import datetime

DB_PATH = os.environ.get("DB_PATH", "trip_planner.sqlite")

async def initialize_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                app_name TEXT NOT NULL,
                state TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (user_id, session_id)
            )
        """)
        await db.commit()

async def get_user_sessions(user_id: str) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT session_id, state, created_at, updated_at FROM sessions WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
    return {
        row["session_id"]: {
            **json.loads(row["state"]),
            "_created_at": row["created_at"],
            "_updated_at": row["updated_at"]
        }
        for row in rows
    }

async def update_user_session(user_id: str, session_id: str, app_name: str, state: dict):
    now = datetime.utcnow().isoformat()
    state["_updated_at"] = now
    if "_created_at" not in state:
        state["_created_at"] = now
    state_json = json.dumps(state)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO sessions (user_id, session_id, app_name, state, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, session_id) DO UPDATE SET
                state=excluded.state,
                updated_at=excluded.updated_at
        """, (user_id, session_id, app_name, state_json, state["_created_at"], state["_updated_at"]))
        await db.commit()

async def delete_user_session(user_id: str, session_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM sessions WHERE user_id = ? AND session_id = ?",
            (user_id, session_id)
        )
        await db.commit()

async def save_accommodation_booking(user_id, session_id, booking_data):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS accommodation_bookings (
                user_id TEXT,
                session_id TEXT,
                location TEXT,
                check_in TEXT,
                check_out TEXT,
                hotel_name TEXT,
                price_per_night REAL,
                total_price REAL,
                created_at TEXT
            )
        """)
        await db.execute("""
            INSERT INTO accommodation_bookings (
                user_id, session_id, location, check_in, check_out, hotel_name,
                price_per_night, total_price, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, session_id,
            booking_data.get("location"),
            booking_data.get("check_in"),
            booking_data.get("check_out"),
            booking_data.get("hotel_name"),
            booking_data.get("price_per_night"),
            booking_data.get("total_price"),
            datetime.utcnow().isoformat()
        ))
        await db.commit()

async def save_travel_booking(user_id, session_id, booking_data):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS travel_bookings (
                user_id TEXT,
                session_id TEXT,
                mode TEXT,
                provider TEXT,
                departure_time TEXT,
                arrival_time TEXT,
                price REAL,
                created_at TEXT
            )
        """)
        await db.execute("""
            INSERT INTO travel_bookings (
                user_id, session_id, mode, provider, departure_time,
                arrival_time, price, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, session_id,
            booking_data.get("mode"),
            booking_data.get("provider"),
            booking_data.get("departure_time"),
            booking_data.get("arrival_time"),
            booking_data.get("price"),
            datetime.utcnow().isoformat()
        ))
        await db.commit()

async def save_sightseeing_plan(user_id, session_id, location, start_date, end_date):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sightseeing_plans (
                user_id TEXT,
                session_id TEXT,
                location TEXT,
                start_date TEXT,
                end_date TEXT,
                created_at TEXT
            )
        """)
        await db.execute("""
            INSERT INTO sightseeing_plans (
                user_id, session_id, location, start_date, end_date, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id, session_id,
            location,
            start_date,
            end_date,
            datetime.utcnow().isoformat()
        ))
        await db.commit()