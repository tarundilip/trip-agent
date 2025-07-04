from datetime import datetime
from google.genai import types

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[36m"
    YELLOW = "\033[33m"
    BLACK = "\033[30m"
    WHITE = "\033[37m"
    BG_GREEN = "\033[42m"
    BG_BLUE = "\033[44m"
    BG_RED = "\033[41m"

async def add_user_query_to_history(session_service, app_name, user_id, session_id, query):
    session = await session_service.get_session(app_name, user_id, session_id)
    history = session.state.get("interaction_history", [])
    history.append({
        "action": "user_query",
        "query": query,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    updated_state = session.state.copy()
    updated_state["interaction_history"] = history
    await session_service.update_session_state(app_name, user_id, session_id, updated_state)

async def add_agent_response_to_history(session_service, app_name, user_id, session_id, agent_name, response):
    session = await session_service.get_session(app_name, user_id, session_id)
    history = session.state.get("interaction_history", [])
    history.append({
        "action": "agent_response",
        "agent": agent_name,
        "response": response,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    updated_state = session.state.copy()
    updated_state["interaction_history"] = history
    await session_service.update_session_state(app_name, user_id, session_id, updated_state)

def process_agent_response(event):
    if event.content and event.content.parts:
        combined_text = ""
        for part in event.content.parts:
            if hasattr(part, "text") and part.text and not part.text.isspace():
                combined_text += part.text.strip() + " "
        if combined_text:
            return event.author or "agent", combined_text.strip()
    return event.author or "agent", None

async def call_agent(runner, user_id, session_id, query):
    from core.response_formatter import format_booking_response  
    content = types.Content(role="user", parts=[types.Part(text=query)])
    full_response = ""
    agent_name = None

    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            agent_name, partial = process_agent_response(event)
            if partial:
                full_response += partial + "\n"
    except Exception as e:
        print(f"{Colors.BG_RED}{Colors.WHITE}ERROR: {e}{Colors.RESET}")
        return

    if full_response and agent_name:
        session = await runner.session_service.get_session(runner.app_name, user_id, session_id)
        state = session.state

        formatted = format_booking_response(state, full_response.strip())

        print(f"\n{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}╔══ FORMATTED AGENT RESPONSE ══════════════════════════════════{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}{formatted}{Colors.RESET}")
        print(f"{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}╚═════════════════════════════════════════════════════════════{Colors.RESET}")

        await add_agent_response_to_history(
            runner.session_service,
            runner.app_name,
            user_id,
            session_id,
            agent_name,
            formatted,
        )