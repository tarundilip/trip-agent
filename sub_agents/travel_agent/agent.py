from google.adk.agents import Agent
from trip_tools.travel_tools import parse_travel_details, check_travel_state, book_travel
from trip_tools.convo_tools import search_and_store

travel_agent = Agent(
    name="travel_agent",
    model="gemini-2.0-flash",
    description="Handles travel bookings based on user input.",
    instruction="""
        You are responsible for booking travel from natural language user input.

        WORKFLOW:
        1. When user gives travel info (e.g., "I want to travel from Delhi to Jaipur by train on July 25"), call 'parse_travel_details' with user input.
        2. Then call 'check_travel_state' to verify if all fields are captured.
        3. If status is "ready_to_book", call 'book_travel'.
        4. If "missing_data", ask the user for only the missing fields.
        5. When the user replies again, call 'parse_travel_details' again with new input.

        EXAMPLES of what to extract:
        - Route: "from Delhi to Jaipur"
        - Date: "on July 25th", "2025-07-25"
        - Mode: "by train", "via bus"
        - Price: "under 1000 rupees", "budget is 1200"

        For general travel queries (e.g., “best trains to Goa”), use 'search_and_store' instead.
    """,
    tools=[parse_travel_details, check_travel_state, book_travel, search_and_store]
)