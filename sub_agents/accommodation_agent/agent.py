from google.adk.agents import Agent

accommodation_agent = Agent(
    name="accommodation_agent",
    model="gemini-2.0-flash",
    description="Handles accommodation queries for a trip planning assistant.",
    instruction="""
    You are responsible for finding accommodation options based on:
    - Location
    - Budget
    - Travel dates

    Use state['user_preferences'] to access:
    - 'location': string
    - 'start_date': string
    - 'end_date': string
    - 'budget': float

    Save your chosen accommodation under state['trip_plan']['accommodation'] as a dictionary:
    {
        "hotel_name": str,
        "location": str,
        "price_per_night": float,
        "total_price": float,
        "check_in": str,
        "check_out": str
    }

    If information is missing or unclear, delegate to the conversation agent for clarification.
    Be descriptive and helpful. Suggest options if no data is fixed.
    """,
    tools=[]
)