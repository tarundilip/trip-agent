from google.adk.agents import Agent
from trip_tools.travel_tools import collect_travel_info
from trip_tools.convo_tools import handle_convo

travel_agent = Agent(
    name="travel_agent",
    model="gemini-2.0-flash",
    description="Manages travel-related planning.",
    instruction="""
        Rely only on user input: from_location, to_location, date, travel class, mode, and budget.

        Do NOT hardcode or guess anything. If details are missing or if the query is general (e.g., 'train schedule from X to Y'), reroute to "handle_convo" tool only.
        """,
    tools=[collect_travel_info, handle_convo]
)