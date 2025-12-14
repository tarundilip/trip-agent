from google.adk.agents import Agent
from trip_tools.travel_tools import (
    parse_travel_details, 
    check_travel_state, 
    book_travel,
    cancel_travel_booking  # ✅ NEW
)
from trip_tools.common import list_active_bookings, view_cancelled_bookings  # ✅ NEW
from trip_tools.convo_tools import search_and_store

travel_agent = Agent(
    name="travel_agent",
    model="gemini-2.0-flash",
    description="Handles travel bookings and cancellations based on user input.",
    instruction="""
You are responsible for booking and managing travel from natural language user input.

WORKFLOW:
1. When user gives travel info, call 'parse_travel_details' with user input.
2. Then call 'check_travel_state' to verify if all fields are captured.
3. If status is "ready_to_book", call 'book_travel'.
4. If "missing_data", ask the user for only the missing fields.
5. When the user replies again, call 'parse_travel_details' again with new input.

CANCELLATION:
- When user says "Cancel my travel booking" or "Cancel my ticket", call 'cancel_travel_booking'
- Confirm cancellation with booking ID and refund details (if price was set)
- Show email confirmation status

VIEW BOOKINGS:
- When user asks "What are my bookings?" or "Show my bookings", call 'list_active_bookings'
- When user asks "What did I cancel?" or "Show cancelled bookings", call 'view_cancelled_bookings'

IMPORTANT: 
- Price is OPTIONAL - the system will try to extract it from previous search results
- DO NOT ask user for price if they haven't provided it
- Use 'search_and_store' only for general travel queries like "best trains from Delhi to Mumbai"
- For cancellations, send email notification if user has provided email
    """,
    tools=[
        parse_travel_details, 
        check_travel_state, 
        book_travel,
        cancel_travel_booking,  # ✅ NEW
        list_active_bookings,  # ✅ NEW
        view_cancelled_bookings,  # ✅ NEW
        search_and_store
    ]
)