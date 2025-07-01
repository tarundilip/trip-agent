from google.adk.agents import Agent
from trip_tools.convo_tools import handle_convo

convo_agent = Agent(
    name="conversation_agent",
    model="gemini-2.0-flash",
    description="Handles general or vague queries using Google Search.",
    instruction="""
        You act as a fallback when a query is unstructured or general.

        Examples:
        - "Best beaches in Goa?"
        - "How long is a train ride to Jaipur?"

        Use "handle_convo" tool only to fetch real-time info via Google Search. Store result in state['conversation_result'].
        """,
    tools=[handle_convo]
)