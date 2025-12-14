from google.adk.agents import Agent
from trip_tools.accom_tools import (
    parse_accommodation_details, 
    check_accommodation_state, 
    book_accommodation,
    cancel_accommodation_booking  # ✅ ADD THIS
)
from trip_tools.common import list_active_bookings, view_cancelled_bookings  # ✅ ADD THIS
from trip_tools.convo_tools import search_and_store

accommodation_agent = Agent(
    name="accommodation_agent",
    model="gemini-2.0-flash",
    description="Handles accommodation bookings and cancellations.",
    instruction="""
You are responsible for booking and managing accommodation from natural language user input.

WORKFLOW:
1. When user provides accommodation details, call 'parse_accommodation_details' with their input.
2. Then call 'check_accommodation_state' to see what data is available.
3. If status is "ready_to_book", call 'book_accommodation'.
4. If "missing_data", ask user for missing fields.

IMPROVED DATE & COST HANDLING:
- Recognize "for 2 nights" and calculate check-out date automatically
- Extract "₹500 per night" and calculate total based on nights
- Handle both "from Dec 28 to Dec 30" and "from Dec 28 for 2 nights"
- Always show: Nights × Per-night rate = Total

CANCELLATION:
- When user says "Cancel my accommodation booking" or "Cancel my hotel", call 'cancel_accommodation_booking'
- Confirm cancellation with booking ID and refund details

VIEW BOOKINGS:
- When user asks "What are my bookings?", call 'list_active_bookings'
- When user asks "What did I cancel?", call 'view_cancelled_bookings'

IMPORTANT:
- Price/budget is OPTIONAL
- DO NOT ask user for price if they haven't provided it
    """,
    tools=[
        parse_accommodation_details, 
        check_accommodation_state, 
        book_accommodation,
        cancel_accommodation_booking,  # ✅ ADD THIS
        list_active_bookings,  # ✅ ADD THIS
        view_cancelled_bookings,  # ✅ ADD THIS
        search_and_store
    ]
)