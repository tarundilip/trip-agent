from google.adk.tools.tool_context import ToolContext

def collect_accommodation_info(tool_context: ToolContext) -> dict:
    """
    Collects necessary accommodation info from user preferences and stores structured data.

    Returns a prompt to user if any info is missing.
    """
    prefs = tool_context.state.get("user_preferences", {})

    required_fields = ["location", "start_date", "end_date", "budget"]
    missing = [field for field in required_fields if field not in prefs]

    if missing:
        return {
            "action": "collect_accommodation_info",
            "status": "incomplete",
            "message": f"Missing fields for accommodation: {', '.join(missing)}. Please provide them."
        }

    tool_context.state["trip_plan"] = tool_context.state.get("trip_plan", {})
    tool_context.state["trip_plan"]["accommodation"] = {
        "hotel_name": None,
        "location": prefs["location"],
        "price_per_night": None,
        "total_price": None,
        "check_in": prefs["start_date"],
        "check_out": prefs["end_date"]
    }

    return {
        "action": "collect_accommodation_info",
        "status": "success",
        "message": "Accommodation info placeholder created based on user preferences."
    }