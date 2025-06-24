from google.adk.agents import Agent

travel_agent = Agent(
    name="travel_agent",
    model="gemini-2.0-flash",
    description="Handles travel-related queries (transportation) for a trip.",
    instruction="""
    You are responsible for planning transportation to the trip destination.

    Use state['user_preferences'] to access:
    - 'from_location': string
    - 'to_location': string
    - 'travel_date': string
    - 'budget': float

    Save your result in state['trip_plan']['travel'] as:
    {
        "mode": str,
        "provider": str,
        "departure_time": str,
        "arrival_time": str,
        "price": float
    }

    Suggest bus/train/flight based on distance and preferences.
    If anything is ambiguous, ask the conversation agent for clarification.
    """,
    tools=[]
)