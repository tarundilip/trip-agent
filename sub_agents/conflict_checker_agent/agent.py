from google.adk.agents import Agent
from trip_tools.conflict_tools import parse_and_check_conflicts

conflict_checker_agent = Agent(
    name="conflict_checker_agent",
    model="gemini-2.0-flash",
    description="Checks the trip plan for timing and budget conflicts.",
    instruction="""
        You are responsible for validating the trip plan to make sure everything fits well in terms of timing and budget.

        1. Always use the 'parse_and_check_conflicts' tool to detect issues.
        2. Conflicts can include:
            - Travel date after hotel check-in
            - Sightseeing outside hotel stay dates
            - Total cost exceeding the user's budget
        3. If conflicts are found, the tool will return `status: conflict_detected` and include reasons.
        4. If everything is okay, the tool will return `status: no_conflict`

        Respond clearly and politely, showing either the conflict list or confirming no issues.
    """,
    tools=[parse_and_check_conflicts]
)