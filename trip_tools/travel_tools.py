from google.adk.tools.tool_context import ToolContext

def collect_travel_info(tool_context: ToolContext) -> dict:
    """
    Collects necessary travel info from user preferences and stores structured data.
    """

    prefs = tool_context.state.get("user_preferences", {})

    required_fields = ["from_location", "to_location", "travel_date", "budget", "mode"]
    missing = [field for field in required_fields if field not in prefs]

    if missing:
        return {
            "action": "collect_travel_info",
            "status": "incomplete",
            "message": f"Missing fields for travel: {', '.join(missing)}. Please provide them."
        }

    tool_context.state["trip_plan"] = tool_context.state.get("trip_plan", {})
    tool_context.state["trip_plan"]["travel"] = {
        "mode": prefs["mode"],
        "provider": None,
        "departure_time": None,
        "arrival_time": None,
        "price": None
    }

    return {
        "action": "collect_travel_info",
        "status": "success",
        "message": "Travel info placeholder saved based on user input."
    }