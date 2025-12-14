from google.adk.agents import Agent
from trip_tools.sightseeing_tools import (
    parse_sightseeing_details,
    check_sightseeing_state,
    plan_sightseeing,
    book_sightseeing,
    cancel_sightseeing_booking  # ✅ NEW
)
from trip_tools.common import list_active_bookings, view_cancelled_bookings  # ✅ NEW
from trip_tools.convo_tools import search_and_store

sightseeing_agent = Agent(
    name="sightseeing_agent",
    model="gemini-2.0-flash",
    description="Handles sightseeing planning, booking, and cancellations for users.",
    instruction="""
You are responsible for planning and managing sightseeing from user input.

WORKFLOW:
1. When user provides input like "I want to visit City Palace on August 2nd", call 'parse_sightseeing_details'.
2. Then call 'check_sightseeing_state' to verify required info.
3. If state is ready, call 'book_sightseeing'.
4. If details are missing, ask user specifically for missing fields.
5. When user responds again, repeat parsing and checking.

CANCELLATION:
- When user says "Cancel my sightseeing booking" or "Cancel my tour", call 'cancel_sightseeing_booking'
- Confirm cancellation with booking ID and refund details (if price was set)
- Show email confirmation status

VIEW BOOKINGS:
- When user asks "What are my bookings?" or "Show my bookings", call 'list_active_bookings'
- When user asks "What did I cancel?" or "Show cancelled bookings", call 'view_cancelled_bookings'

IMPORTANT:
- Entry fee/budget is OPTIONAL - the system will try to extract it from previous search results
- DO NOT ask user for entry fee if they haven't provided it
- Use 'search_and_store' only for general queries like "top places to visit in Jaipur"
- For cancellations, send email notification if user has provided email
    """,
    tools=[
        parse_sightseeing_details,
        check_sightseeing_state,
        plan_sightseeing,
        book_sightseeing,
        cancel_sightseeing_booking,  # ✅ NEW
        list_active_bookings,  # ✅ NEW
        view_cancelled_bookings,  # ✅ NEW
        search_and_store
    ]
)