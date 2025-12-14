from google.adk.tools.tool_context import ToolContext
import re
from datetime import datetime
from loguru import logger

def normalize_date(date_str):
    try:
        cleaned = re.sub(r"(st|nd|rd|th)", "", date_str)
        dt = datetime.strptime(cleaned.strip(), "%B %d, %Y")
        return dt.strftime("%Y-%m-%d")
    except:
        return date_str

def parse_trip_details(tool_context: ToolContext, user_input: str) -> dict:
    trip_plan = tool_context.state.get("trip_plan", {})
    if not isinstance(trip_plan, dict):
        trip_plan = {}

    travel_match = re.search(
        r"trip from (\w+) to (\w+).*?via (\w+).*?on (\w+ \d{1,2}(?:st|nd|rd|th)?,? \d{4}).*?₹?(\d+)", user_input, re.IGNORECASE)
    if travel_match:
        trip_plan["travel"] = {
            "from_location": travel_match.group(1),
            "to_location": travel_match.group(2),
            "mode": travel_match.group(3).lower(),
            "date": normalize_date(travel_match.group(4)),
            "price": int(travel_match.group(5))
        }

    accom_match = re.search(
        r"hotel in ([\w\s]+).*?from (\w+ \d{1,2}(?:st|nd|rd|th)?).*?to (\w+ \d{1,2}(?:st|nd|rd|th)?).*?₹?(\d+)",
        user_input, re.IGNORECASE)
    if accom_match:
        trip_plan["accommodation"] = {
            "location": accom_match.group(1).strip(),
            "check_in": normalize_date(accom_match.group(2)),
            "check_out": normalize_date(accom_match.group(3)),
            "total_price": int(accom_match.group(4))
        }

    sight_matches = re.findall(
        r"visit ([\w\s]+) in ([\w\s]+)? on (\w+ \d{1,2}(?:st|nd|rd|th)?).*?₹?(\d+)", user_input, re.IGNORECASE)
    if sight_matches:
        sightseeing = trip_plan.get("sightseeing", [])
        if not isinstance(sightseeing, list):
            sightseeing = []

        for place, loc, date_str, fee in sight_matches:
            location = loc.strip() if loc else trip_plan.get("accommodation", {}).get("location", "Unknown")
            sightseeing.append({
                "location": location,
                "date": normalize_date(date_str),
                "activity": f"Visit {place.strip()}",
                "entry_fee": int(fee)
            })
        trip_plan["sightseeing"] = sightseeing

    budget_match = re.search(r"budget.*?₹?(\d{4,6})", user_input)
    if budget_match:
        tool_context.state["total_budget"] = int(budget_match.group(1))

    tool_context.state["trip_plan"] = trip_plan

    return {
        "action": "parse_trip_details",
        "status": "success",
        "message": "Parsed trip details from user input.",
        "parsed_state": tool_context.state
    }


def check_trip_conflicts(tool_context: ToolContext) -> dict:
    state = tool_context.state
    trip_plan = state.get("trip_plan", {})
    if not isinstance(trip_plan, dict):
        trip_plan = {}

    conflict_reasons = []

    travel = trip_plan.get("travel", {})
    accommodation = trip_plan.get("accommodation", {})
    sightseeing = trip_plan.get("sightseeing", [])
    budget = state.get("total_budget", float("inf"))

    if travel and accommodation:
        travel_date = travel.get("date")
        check_in = accommodation.get("check_in")
        if travel_date and check_in and travel_date > check_in:
            conflict_reasons.append("Your travel date is after your hotel check-in date.")

    if sightseeing and accommodation:
        check_in = accommodation.get("check_in")
        check_out = accommodation.get("check_out")
        for activity in sightseeing:
            date = activity.get("date")
            location = activity.get("location")
            if date and (date < check_in or date > check_out):
                conflict_reasons.append(
                    f"Sightseeing activity in {location} on {date} is outside your hotel stay period."
                )

    total_cost = 0
    if travel.get("price"):
        total_cost += travel["price"]
    if accommodation.get("total_price"):
        total_cost += accommodation["total_price"]
    if isinstance(sightseeing, list):
        total_cost += sum(item.get("entry_fee", 0) for item in sightseeing)

    if total_cost > budget:
        conflict_reasons.append(f"Total cost of ₹{total_cost} exceeds your budget of ₹{budget}.")

    if conflict_reasons:
        state["conflict"] = True
        state["conflict_reason"] = "; ".join(conflict_reasons)
        return {
            "action": "check_trip_conflicts",
            "status": "conflict_detected",
            "message": "There are some conflicts in your current trip plan.",
            "conflict_reasons": conflict_reasons
        }

    state["conflict"] = False
    return {
        "action": "check_trip_conflicts",
        "status": "no_conflict",
        "message": "Everything looks good! No conflicts were found in your trip plan."
    }


def parse_and_check_conflicts(tool_context: ToolContext, user_input: str) -> dict:
    parse_trip_details(tool_context, user_input)
    return check_trip_conflicts(tool_context)


# ✅ ADD THIS FUNCTION (ALIAS FOR COMPATIBILITY)
def check_conflicts(tool_context: ToolContext) -> dict:
    """
    Alias for check_trip_conflicts - checks for conflicts in the current trip plan
    
    This function is used by the conflict_checker_agent to validate trip bookings.
    It checks for:
    - Date conflicts between travel and accommodation
    - Sightseeing dates outside accommodation period
    - Budget overruns
    """
    logger.info("🔍 Checking trip conflicts...")
    result = check_trip_conflicts(tool_context)
    
    if result["status"] == "conflict_detected":
        logger.warning(f"⚠️ Conflicts found: {'; '.join(result.get('conflict_reasons', []))}")
    else:
        logger.info("✅ No conflicts detected")
    
    return result