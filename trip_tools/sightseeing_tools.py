from google.adk.tools.tool_context import ToolContext

def collect_sightseeing_info(tool_context: ToolContext) -> dict:
    """
    Collects sightseeing plan input. Either suggest or take from user.
    """

    prefs = tool_context.state.get("user_preferences", {})

    required_fields = ["location", "start_date", "end_date"]
    missing = [field for field in required_fields if field not in prefs]

    if missing:
        return {
            "action": "collect_sightseeing_info",
            "status": "incomplete",
            "message": f"Missing fields for sightseeing: {', '.join(missing)}. Please provide them."
        }

    tool_context.state["trip_plan"] = tool_context.state.get("trip_plan", {})
    tool_context.state["trip_plan"]["sightseeing"] = []

    return {
        "action": "collect_sightseeing_info",
        "status": "success",
        "message": "Sightseeing section initialized. Waiting for user input or suggestions."
    }