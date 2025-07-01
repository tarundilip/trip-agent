from google.adk.agents import Agent
from trip_tools.accom_tools import collect_accommodation_info
from trip_tools.convo_tools import handle_convo

accommodation_agent = Agent(
    name="accommodation_agent",
    model="gemini-2.0-flash",
    description="Handles accommodation-related tasks.",
    instruction="""
        Only proceed if all required info is available:
        - location
        - check-in date
        - check-out date
        - budget

        Store only structured info in state['trip_plan']['accommodation']. Do NOT hardcode any hotel or simulate responses.

        If user query is general (e.g., 'best hotels in Delhi'), call "handle_convo" tool only to fetch via Google Search.
        """,
    tools=[collect_accommodation_info, handle_convo]
)