import asyncio
from google.adk.runners import Runner
from sub_agents.accommodation_agent.agent import accommodation_agent
from core.session_service import SQLiteSessionService
from google.genai.types import Content, Part

APP_NAME = "Trip Planner"
USER_ID = "test_user"
SESSION_ID = "test_accom_session"

async def test_accommodation_agent():
    session_service = SQLiteSessionService("sessions.db")
    await session_service._init_db()

    await session_service.delete_session(APP_NAME, USER_ID, SESSION_ID)
    
    initial_state = {
        "trip_plan": {}
    }
    
    print("Creating session with initial state:", initial_state)
    await session_service.create_session(APP_NAME, USER_ID, initial_state, SESSION_ID)
    
    session = await session_service.get_session(APP_NAME, USER_ID, SESSION_ID)
    print("Session state after creation:", session.state if session else "Session not found")

    runner = Runner(agent=accommodation_agent, session_service=session_service, app_name=APP_NAME)

    user_message = """I want to book accommodation in Manali from August 10th to August 14th, 2025. 
    My budget is 2500 rupees per night and the total cost should be around 10000 rupees."""

    print(f"\n=== Accommodation Agent ===")
    print(f"User Input: {user_message}")
    print("Agent Response:")
    
    async for event in runner.run_async(
        user_id=USER_ID, 
        session_id=SESSION_ID, 
        new_message=Content(role="user", parts=[Part(text=user_message)])
    ):
        for part in event.content.parts:
            if part.text:
                print("Response:", part.text)

asyncio.run(test_accommodation_agent())