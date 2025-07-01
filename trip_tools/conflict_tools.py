from google.adk.tools.tool_context import ToolContext

def check_conflicts(tool_context: ToolContext) -> dict:
    """
    Analyzes trip plan for conflicts across travel, accommodation, and sightseeing.
    """

    plan = tool_context.state.get("trip_plan", {})
    prefs = tool_context.state.get("user_preferences", {})
    conflict_reason = []

    travel = plan.get("travel")
    accommodation = plan.get("accommodation")
    sightseeing = plan.get("sightseeing", [])
    budget = prefs.get("budget", float('inf'))

    if travel and accommodation:
        if travel.get("departure_time") and accommodation.get("check_in"):
            if travel["departure_time"] > accommodation["check_in"]:
                conflict_reason.append("Travel arrives after hotel check-in.")

    if sightseeing and accommodation:
        for item in sightseeing:
            if item.get("scheduled_date"):
                if not (accommodation["check_in"] <= item["scheduled_date"] <= accommodation["check_out"]):
                    conflict_reason.append(f"Sightseeing '{item['place']}' is outside accommodation period.")

    total_cost = 0
    if travel and travel.get("price"): total_cost += travel["price"]
    if accommodation and accommodation.get("total_price"): total_cost += accommodation["total_price"]
    if sightseeing:
        total_cost += sum(item.get("entry_fee", 0) for item in sightseeing)

    if total_cost > budget:
        conflict_reason.append("Total trip cost exceeds budget.")

    if conflict_reason:
        tool_context.state["conflict"] = True
        tool_context.state["conflict_reason"] = "; ".join(conflict_reason)
        return {
            "action": "check_conflicts",
            "status": "conflict",
            "message": "Conflicts detected in trip plan.",
            "reasons": conflict_reason
        }

    tool_context.state["conflict"] = False
    return {
        "action": "check_conflicts",
        "status": "ok",
        "message": "No conflicts detected."
    }