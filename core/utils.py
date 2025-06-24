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

async def display_state(session_service, app_name, user_id, session_id, label="State"):
    try:
        session = await session_service.get_session(app_name, user_id, session_id)
        print(f"\n{'=' * 10} {label} {'=' * 10}")
        for key, value in session.state.items():
            print(f"{key}: {value}")
        print("=" * (22 + len(label)))
    except Exception as e:
        print(f"{Colors.BG_RED}{Colors.WHITE}Error displaying state: {e}{Colors.RESET}")

def process_agent_response(event):
    agent_name = event.author or "agent"
    final_response = None

    if event.content and event.content.parts:
        for part in event.content.parts:
            if hasattr(part, "text") and part.text and not part.text.isspace():
                final_response = part.text.strip()
                print(
                    f"{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}╔══ AGENT RESPONSE ══════════════════════════════════{Colors.RESET}"
                )
                print(f"{Colors.CYAN}{Colors.BOLD}{final_response}{Colors.RESET}")
                print(
                    f"{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}╚═════════════════════════════════════════════════════{Colors.RESET}"
                )
    return agent_name, final_response

async def call_agent(runner, user_id, session_id, query):
    content = types.Content(role="user", parts=[types.Part(text=query)])
    print(f"\n{Colors.BG_GREEN}{Colors.BLACK}Running agent query...{Colors.RESET}")
    await display_state(runner.session_service, runner.app_name, user_id, session_id, "Before")

    final_response = None
    agent_name = None

    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            agent_name, final_response = process_agent_response(event)

    except Exception as e:
        print(f"{Colors.BG_RED}{Colors.WHITE}ERROR: {e}{Colors.RESET}")

    if final_response and agent_name:
        await add_agent_response_to_history(
            runner.session_service,
            runner.app_name,
            user_id,
            session_id,
            agent_name,
            final_response,
        )

    await display_state(runner.session_service, runner.app_name, user_id, session_id, "After")
    print(f"{Colors.YELLOW}{'-' * 40}{Colors.RESET}")