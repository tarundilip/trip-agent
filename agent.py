from google.adk.agents import Agent
from google.adk.runners import Runner   

from sub_agents.accommodation_agent.agent import accommodation_agent
from sub_agents.travel_agent.agent import travel_agent
from sub_agents.sightseeing_agent.agent import sightseeing_agent
from sub_agents.conflict_checker_agent.agent import conflict_checker_agent
from sub_agents.conversation_agent.agent import conversation_agent

trip_planner_supervisor = Agent(
    name="trip_supervisor",
    model="gemini-2.0-flash",
    description="Supervisor agent that coordinates trip planning (accommodation, travel, sightseeing).",
    instruction="""
    You are the main trip planning assistant. Your task is to understand user queries about planning trips
    and delegate subtasks to the appropriate sub-agents.

    Trip Planning Components:
    1. Accommodation: hotels, stays, availability
    2. Travel: transportation options, schedules
    3. Sightseeing: local spots, activities, attractions
    4. Conflict Checking: validate compatibility (date, location, pricing)
    5. Conversation Management: ask clarifying questions or follow up

    Use user session state to store and access:
    - trip_plan (dict): overall plan with keys 'accommodation', 'travel', 'sightseeing'
    - user_preferences (dict): budget, location, dates
    - interaction_history (list): past messages

    Follow this logic:
    - Understand what aspect of trip the user is asking for
    - Check if all parts of the plan align (call conflict agent if needed)
    - Ask clarifying questions through conversation agent
    - Update session state after every step

    You must guide the user smoothly from initial query to a finalized trip plan.
    """,
    sub_agents=[
        accommodation_agent,
        travel_agent,
        sightseeing_agent,
        conflict_checker_agent,
        conversation_agent
    ],
    tools=[]
)

class TripPlannerRunner(Runner):
    def __init__(self, session_service):
        super().__init__(
            app_name="trip_planner",
        agent=trip_planner_supervisor,
        session_service=session_service
        )