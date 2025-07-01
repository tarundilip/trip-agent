import asyncio
from dotenv import load_dotenv
from agent import trip_planner_supervisor
from google.adk.runners import Runner
from core.session_service import SQLiteSessionService
from core.utils import (
    add_user_query_to_history,
    add_agent_response_to_history,
    call_agent
)

load_dotenv()

APP_NAME = "Trip Planner"
session_service = SQLiteSessionService("sessions.db")
runner = Runner(agent=trip_planner_supervisor, session_service=session_service, app_name=APP_NAME)

initial_state = {
    "user_name": None,
    "destination": None,
    "preferences": [],
    "interaction_history": [],
}

async def main_async():
    await session_service._init_db()  

    user_id = input("Enter your user ID: ").strip()

    sessions = await session_service.list_sessions(app_name=APP_NAME, user_id=user_id)
    if sessions:
        print("\nFound existing session(s):")
        for idx, s in enumerate(sessions, 1):
            print(f"{idx}. {s.id}")
        print(f"{len(sessions) + 1}. Start a new session")
        choice = input("\nChoose a session to resume or start new: ").strip()

        if choice.isdigit() and 1 <= int(choice) <= len(sessions):
            session_id = sessions[int(choice) - 1].id
            print(f"\nResuming session: {session_id}")
        else:
            new_session = await session_service.create_session(APP_NAME, user_id, initial_state)
            session_id = new_session.id
            print(f"\nStarted new session: {session_id}")
    else:
        new_session = await session_service.create_session(APP_NAME, user_id, initial_state)
        session_id = new_session.id
        print(f"\nStarted new session: {session_id}")

    while True:
        user_query = input("\nAsk your travel planning question (or type 'exit'): ").strip()
        if user_query.lower() in ["exit", "quit"]:
            print("Exiting session. Goodbye!")
            break

        try:
            await add_user_query_to_history(session_service, APP_NAME, user_id, session_id, user_query)
            await call_agent(runner, user_id, session_id, user_query)
        except Exception as e:
            print(f"Error during interaction: {e}")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()