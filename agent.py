from google.adk.agents import Agent
from google.adk.runners import Runner
from sub_agents.accommodation_agent.agent import accommodation_agent
from sub_agents.travel_agent.agent import travel_agent
from sub_agents.sightseeing_agent.agent import sightseeing_agent
from sub_agents.conflict_checker_agent.agent import conflict_agent
from sub_agents.conversation_agent.agent import convo_agent
from tools.search_tool import perform_search

trip_planner_supervisor = Agent(
    name="trip_supervisor",
    model="gemini-2.0-flash",
    description="Supervisor agent coordinating all trip planning sub-agents.",
    instruction="""
        You are the trip planning supervisor.

        Responsibilities:
        - Understand user's intent: booking travel, accommodation, sightseeing, or general queries.
        - Route subtasks to appropriate sub-agents.
        - Ensure all required data is collected from the user.
        - Use conversation agent when queries are vague or generic.
        - Validate completed plans using conflict checker.

        Session state structure:
        - user_preferences: user's input for travel details
        - trip_plan: dict with accommodation, travel, sightseeing entries
        - conversation_result: if rerouted through search
        - conflict: True/False
        """,
    sub_agents=[
        accommodation_agent,
        travel_agent,
        sightseeing_agent,
        conflict_agent,
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