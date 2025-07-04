from google.adk.agents import Agent
from trip_tools.sightseeing_tools import (
    parse_sightseeing_details,
    check_sightseeing_state,
    plan_sightseeing
)
from trip_tools.convo_tools import search_and_store

sightseeing_agent = Agent(
    name="sightseeing_agent",
    model="gemini-2.0-flash",
    description="Handles sightseeing planning for users.",
    instruction="""
        You are responsible for planning sightseeing from user input.

        WORKFLOW:
        1. When user provides input like "I want to visit City Palace on August 2nd", call 'parse_sightseeing_details'.
        2. Then call 'check_sightseeing_state' to verify required info.
        3. If state is ready, call 'plan_sightseeing'.
        4. If details are missing, ask user specifically for missing fields.
        5. When user responds again, repeat parsing and checking.

        Use 'search_and_store' only for general queries like "top places to visit in Jaipur".
    """,
    tools=[
        parse_sightseeing_details,
        check_sightseeing_state,
        plan_sightseeing,
        search_and_store
    ]
)