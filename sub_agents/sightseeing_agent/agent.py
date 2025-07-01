from google.adk.agents import Agent
from trip_tools.sightseeing_tools import collect_sightseeing_info
from trip_tools.convo_tools import handle_convo

sightseeing_agent = Agent(
    name="sightseeing_agent",
    model="gemini-2.0-flash",
    description="Plans sightseeing options for the trip.",
    instruction="""
        Gather sightseeing preferences from user (location, date range).

        Do not hardcode or suggest default attractions. If query is general like 'places to visit in Mumbai', call "handle_convo" tool only to use Google Search.

        Store structured list under state['trip_plan']['sightseeing'].
        """,
    tools=[collect_sightseeing_info, handle_convo]
)