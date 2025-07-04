from google.adk.agents import Agent
from google.adk.runners import Runner

from sub_agents.accommodation_agent.agent import accommodation_agent
from sub_agents.travel_agent.agent import travel_agent
from sub_agents.sightseeing_agent.agent import sightseeing_agent
from sub_agents.conflict_checker_agent.agent import conflict_checker_agent
from sub_agents.conversation_agent.agent import convo_agent
from tools.search_tool import perform_search

trip_planner_supervisor = Agent(
    name="trip_supervisor",
    model="gemini-2.0-flash",
    description="Supervisor agent coordinating all trip planning sub-agents.",
    instruction="""
        You are the trip planning supervisor. Your goal is to orchestrate travel planning by routing to the correct sub-agents.

        Responsibilities:
        - Understand the user’s request (travel, hotel, sightseeing, or general info).
        - Route to the appropriate sub-agent (do not process the task yourself).
        - Never ask for information if it already exists in state.
        - Ensure sub-agents only act when all required state values are available.
        - For vague queries or research requests, use the conversation_agent.
        - Once all components are added, call the conflict_checker_agent to validate the plan.

        State keys used:
        - state['user_preferences']: e.g., total budget, preferred travel mode
        - state['trip_plan']['travel']
        - state['trip_plan']['accommodation']
        - state['trip_plan']['sightseeing']
        - state['conversation_result']
        - state['conflict'] (boolean)
        - state['conflict_reason'] (if any)

        Do not call tools directly here unless it's the `perform_search` fallback.
    """,
    sub_agents=[
        accommodation_agent,
        travel_agent,
        sightseeing_agent,
        conflict_checker_agent,
        convo_agent
    ],
    tools=[perform_search]  
)

class TripPlannerRunner(Runner):
    def __init__(self, session_service):
        super().__init__(
            app_name="trip_planner",
            agent=trip_planner_supervisor,
            session_service=session_service
        )