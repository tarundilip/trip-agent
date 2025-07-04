import asyncio
from google.adk.runners import Runner
from sub_agents.conflict_checker_agent.agent import conflict_checker_agent
from core.session_service import SQLiteSessionService
from google.genai.types import Content, Part

APP_NAME = "Trip Planner"
USER_ID = "test_user"
SESSION_ID = "test_conflict_session"

async def test_conflict_agent():
    session_service = SQLiteSessionService("sessions.db")
    await session_service._init_db()

    await session_service.delete_session(APP_NAME, USER_ID, SESSION_ID)
    await session_service.create_session(APP_NAME, USER_ID, {"trip_plan": {}}, SESSION_ID)

    runner = Runner(agent=conflict_checker_agent, session_service=session_service, app_name=APP_NAME)

    user_message = """I'm planning a trip from Delhi to Goa. I'll be flying there on July 12th, 2025, which costed ₹5000.
    I've booked a hotel in Goa from July 10th to July 14th for ₹5000.
    I also want to visit Baga Beach on July 15th, and the entry fee is ₹500.
    My total budget for this entire trip is ₹10000.
    Can you check if there are any conflicts in my itinerary?"""

    print("\n=== Conflict Checker Agent ===")
    print("User Input:", user_message)

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=Content(role="user", parts=[Part(text=user_message)])
    ):
        for part in event.content.parts:
            if part.text:
                print("Response:", part.text)

asyncio.run(test_conflict_agent())