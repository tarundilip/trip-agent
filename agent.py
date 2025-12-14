from google.adk.agents import Agent
from google.adk.runners import Runner
from sub_agents.accommodation_agent.agent import accommodation_agent
from sub_agents.travel_agent.agent import travel_agent
from sub_agents.sightseeing_agent.agent import sightseeing_agent
from sub_agents.conflict_checker_agent.agent import conflict_checker_agent
from sub_agents.conversation_agent.agent import convo_agent
from sub_agents.billing_agent.agent import billing_agent  # ✅ ADD THIS
from tools.search_tool import perform_search
from trip_tools.ui_tools import identify_user, list_user_sessions, get_current_user_info
from core.rate_limiter import gemini_rate_limiter
from loguru import logger
import time

trip_planner_supervisor = Agent(
    name="trip_supervisor",
    model="gemini-2.0-flash-exp",
    description="Supervisor agent coordinating all trip planning sub-agents with user management.",
    instruction="""
You are the trip planning supervisor. USER IDENTIFICATION IS MANDATORY BEFORE ANY TRIP PLANNING.

**CRITICAL: ALWAYS USE THE identify_user TOOL - DO NOT JUST RESPOND WITH TEXT!**

**STEP 1 - CHECK USER STATUS:**
- FIRST, call get_current_user_info() to check if user is identified
- If it returns "No user is currently identified", proceed to Step 2
- If user is identified, skip to Step 3

**STEP 2 - IDENTIFY USER (USE THE TOOL!):**
When user is NOT identified:
1. If they provide email (contains @ symbol):
   - IMMEDIATELY call: identify_user(user_input="their_email")
   - DO NOT just say "thank you" - CALL THE TOOL!
   
2. After email is captured, ask for name:
   - Wait for their response
   - When they provide name, IMMEDIATELY call: identify_user(user_input="their_name")
   - DO NOT just say "welcome" - CALL THE TOOL!

**STEP 3 - TRIP PLANNING:**
Only after user_id exists in state:
- Route to travel_agent for travel bookings
- Route to accommodation_agent for hotel bookings
- Route to sightseeing_agent for attractions
- Route to conflict_checker_agent for validation
- Route to billing_agent for bill/cost calculations  ← ADD THIS
- Route to convo_agent for general questions

**BILLING QUERIES:**
When user asks about costs, bills, or totals:
- Route to billing_agent
- Examples: "What's my total?", "Calculate bill", "Show costs"

Remember: ALWAYS call the tool, don't just respond with text!
""",
    sub_agents=[
        convo_agent,
        accommodation_agent,
        travel_agent,
        sightseeing_agent,
        conflict_checker_agent,
        billing_agent  # ✅ ADD THIS
    ],
    tools=[
        perform_search, 
        identify_user,
        list_user_sessions,
        get_current_user_info
    ]
)

class TripPlannerRunner(Runner):
    def __init__(self, session_service):
        super().__init__(
            app_name="trip_planner",
            agent=trip_planner_supervisor,
            session_service=session_service
        )
        logger.info("✅ TripPlannerRunner initialized with per-session rate limiting")
    
    async def run(self, user_input: str, session_id: str):
        """Override run to add per-session rate limiting"""
        
        # Apply rate limiting BEFORE making API call (per session)
        gemini_rate_limiter.wait_if_needed(session_id=session_id)
        
        logger.info(f"🔄 [Session: {session_id[:8]}...] Processing: {user_input[:50]}...")
        
        try:
            response = await super().run(user_input, session_id=session_id)
            logger.info(f"✅ [Session: {session_id[:8]}...] Response generated")
            return response
            
        except Exception as e:
            error_msg = str(e).lower()
            
            if '503' in error_msg or 'overload' in error_msg:
                logger.error(f"❌ [Session: {session_id[:8]}...] API overloaded - 503 error")
                logger.info("⏳ Waiting 3 seconds before retry...")
                time.sleep(3)
                
                try:
                    response = await super().run(user_input, session_id=session_id)
                    logger.info("✅ Retry successful")
                    return response
                except:
                    return "I apologize, but the AI service is currently experiencing high traffic. Please wait a moment and try your request again."
            else:
                logger.error(f"❌ Error: {error_msg}")
                raise