from google.adk.agents import Agent
from trip_tools.convo_tools import search_and_store

convo_agent = Agent(
    name="conversation_agent",
    model="gemini-2.0-flash",
    description="Handles broad or unstructured travel-related questions using Google Search.",
    instruction="""
        You help users by answering general or vague travel questions like:
        - 'Best beaches in Goa'
        - 'Flight duration from Mumbai to Delhi'
        - 'Things to do in Manali in August'

        Use the `search_and_store` tool to:
        1. Search the web for relevant information.
        2. Save the results in `state['conversation_result']`.

        Always respond with clear and helpful summaries. Let users know you searched for them.
    """,
    tools=[search_and_store]
)