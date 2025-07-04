import asyncio
from google.adk.runners import Runner
from sub_agents.sightseeing_agent.agent import sightseeing_agent
from core.session_service import SQLiteSessionService
from google.genai.types import Content, Part

APP_NAME = "Trip Planner"
USER_ID = "test_user"
SESSION_ID = "test_sightseeing_session"

async def test_sightseeing_agent():
    session_service = SQLiteSessionService("sessions.db")
    await session_service._init_db()

    await session_service.delete_session(APP_NAME, USER_ID, SESSION_ID)
    await session_service.create_session(APP_NAME, USER_ID, {"trip_plan": {}}, SESSION_ID)

    runner = Runner(agent=sightseeing_agent, session_service=session_service, app_name=APP_NAME)

    user_message = """I want to visit City Palace on August 2nd, 2025. The entry fee is 300 rupees."""

    print("\n=== Sightseeing Agent ===")
    print("User Input:", user_message)

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=Content(role="user", parts=[Part(text=user_message)])
    ):
        for part in event.content.parts:
            if part.text:
                print("Response:", part.text)

asyncio.run(test_sightseeing_agent())