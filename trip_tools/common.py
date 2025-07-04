def update_trip_plan(tool_context, domain: str, required_fields: list, defaults: dict = None) -> dict:
    """
    Moves validated data from user_preferences into trip_plan.[domain],
    if required fields are met. Returns a structured result.
    """
    prefs = tool_context.state.get("user_preferences", {})
    trip_plan = tool_context.state.get("trip_plan", {})
    domain_data = trip_plan.get(domain, {})
    defaults = defaults or {}

    missing = [field for field in required_fields if field not in prefs]

    if missing:
        return {
            "action": f"collect_{domain}_info",
            "status": "incomplete",
            "message": f"Missing fields for {domain}: {', '.join(missing)}. Please provide them."
        }

    new_data = {**defaults}
    for field in required_fields:
        new_data[field] = prefs[field]

    trip_plan[domain] = new_data
    tool_context.state["trip_plan"] = trip_plan

    return {
        "action": f"collect_{domain}_info",
        "status": "success",
        "message": f"{domain.capitalize()} info updated in trip plan."
    }