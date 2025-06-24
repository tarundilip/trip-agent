from google.adk.agents import Agent

sightseeing_agent = Agent(
    name="sightseeing_agent",
    model="gemini-2.0-flash",
    description="Suggests sightseeing options based on user preferences.",
    instruction="""
    You handle sightseeing planning for the trip.

    Use state['user_preferences'] to access:
    - 'location': str
    - 'start_date': str
    - 'end_date': str

    Populate state['trip_plan']['sightseeing'] as a list of dictionaries:
    [
        {
            "place": str,
            "description": str,
            "entry_fee": float,
            "scheduled_date": str
        },
        ...
    ]

    Aim for popular or unique experiences. Mention cost and timing.
    Cross-check dates with accommodation and travel plans.
    If necessary, call the conflict_checker_agent.
    """,
    tools=[]
)