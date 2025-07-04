import uuid
import datetime
import json
import aiosqlite
from google.adk.sessions import Session
from google.adk.sessions.base_session_service import BaseSessionService

class SQLiteSessionService(BaseSessionService):
    def __init__(self, db_path="sessions.db"):
        self.db_path = db_path

    async def _init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    app_name TEXT,
                    user_id TEXT,
                    created TEXT,
                    updated TEXT,
                    state TEXT
                )
            """)
            await db.commit()

    async def create_session(self, app_name, user_id, state, session_id=None):
        session_id = session_id or str(uuid.uuid4())
        now = datetime.datetime.now().isoformat()

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO sessions (id, app_name, user_id, created, updated, state)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session_id, app_name, user_id, now, now, json.dumps(state)))
            await db.commit()

        return Session(
            id=session_id,
            appName=app_name,
            userId=user_id,
            state=state
        )

    def _safe_load_state(self, state_str):
        try:
            return json.loads(state_str)
        except json.JSONDecodeError:
            try:
                return eval(state_str)
            except Exception:
                return {}

    async def get_session(self, app_name, user_id, session_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT state, created, updated FROM sessions
                WHERE app_name=? AND user_id=? AND id=?
            """, (app_name, user_id, session_id)) as cursor:
                row = await cursor.fetchone()
                if row:
                    state_str, created, updated = row
                    state = self._safe_load_state(state_str)
                    return Session(
                        id=session_id,
                        appName=app_name,
                        userId=user_id,
                        state=state
                    )
                raise ValueError("Session not found")

    async def update_session_state(self, app_name, user_id, session_id, state):
        now = datetime.datetime.now().isoformat()

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE sessions
                SET state = ?, updated = ?
                WHERE app_name = ? AND user_id = ? AND id = ?
            """, (json.dumps(state), now, app_name, user_id, session_id))
            await db.commit()

    async def delete_session(self, app_name: str, user_id: str, session_id: str) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM sessions WHERE app_name = ? AND user_id = ? AND id = ?",
                (app_name, user_id, session_id)
            )
            await db.commit()


    async def list_sessions(self, app_name, user_id):
        sessions = []

        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT id, created, updated, state FROM sessions
                WHERE app_name=? AND user_id=?
                ORDER BY updated DESC
            """, (app_name, user_id)) as cursor:
                async for row in cursor:
                    sid, created, updated, state_str = row
                    state = self._safe_load_state(state_str)
                    sessions.append(Session(
                        id=sid,
                        appName=app_name,
                        userId=user_id,
                        state=state
                    ))

        return sessions