from google.adk.agents import Agent
from trip_tools.conflict_tools import check_conflicts

conflict_agent = Agent(
    name="conflict_checker_agent",
    model="gemini-2.0-flash",
    description="Detects and flags trip conflicts.",
    instruction="""
        Compare trip_plan sections:
        - travel vs accommodation dates
        - sightseeing within accommodation period
        - total cost vs budget

        Set:
        - state['conflict'] = True/False
        - state['conflict_reason'] = <explanation> if True
        """,
    tools=[check_conflicts]
)