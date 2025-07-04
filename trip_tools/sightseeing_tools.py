from google.adk.tools.tool_context import ToolContext
import re
from datetime import datetime

def parse_sightseeing_details(tool_context: ToolContext, user_input: str) -> dict:
    """Extract sightseeing details from user input."""
    details = {}

    place_pattern = r"(?:visit|see|explore|go to|check out)\s+([A-Za-z\s]+?)(?:\s+on|\s+at|\s+with|\s+for|\s+entry|\s+which|\.|$)"
    date_patterns = [
        r"on\s+([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)",
        r"on\s+(\d{4}-\d{2}-\d{2})",
        r"on\s+(\d{1,2}[-/]\d{1,2}[-/]\d{4})"
    ]
    fee_patterns = [
        r"(?:entry\s+fee|ticket\s+price|cost)\s+(?:is\s+)?₹?\s*(\d+)",
        r"₹\s*(\d+)\s*(?:entry|ticket)?",
        r"(\d+)\s*rupees\s*(?:entry|ticket)?"
    ]

    match = re.search(place_pattern, user_input, re.IGNORECASE)
    if match:
        details['sightseeing_place'] = match.group(1).strip()

    for pattern in date_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            date = normalize_date(match.group(1).strip())
            details['sightseeing_date'] = date
            break

    for pattern in fee_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            details['sightseeing_fee'] = int(match.group(1))
            break

    if details:
        tool_context.state.update(details)

    return {
        "action": "parse_sightseeing_details",
        "status": "success",
        "message": f"Extracted sightseeing details: {details}",
        "extracted_details": details
    }

def check_sightseeing_state(tool_context: ToolContext) -> dict:
    """Check if all sightseeing fields are available in state."""
    required_fields = {
        'sightseeing_place': 'Sightseeing place',
        'sightseeing_date': 'Date',
        'sightseeing_fee': 'Entry fee'
    }

    available = {}
    missing = []

    for key, label in required_fields.items():
        val = tool_context.state.get(key)
        if val:
            available[key] = val
        else:
            missing.append(label)

    if missing:
        return {
            "action": "check_state",
            "status": "missing_data",
            "message": f"Missing sightseeing details: {', '.join(missing)}",
            "available_data": available,
            "missing_fields": missing
        }
    else:
        return {
            "action": "check_state",
            "status": "ready_to_plan",
            "message": "All sightseeing details are available. Ready to proceed.",
            "available_data": available,
            "missing_fields": []
        }

def plan_sightseeing(tool_context: ToolContext) -> dict:
    """Plan sightseeing using details in state."""

    trip_plan = tool_context.state.get("trip_plan", {})

    sightseeing = {
        "place": tool_context.state.get("sightseeing_place"),
        "date": tool_context.state.get("sightseeing_date"),
        "entry_fee": tool_context.state.get("sightseeing_fee")
    }

    trip_plan["sightseeing"] = sightseeing
    tool_context.state["trip_plan"] = trip_plan

    return {
        "action": "plan_sightseeing",
        "status": "success",
        "message": (
            f"Sightseeing confirmed at {sightseeing['place']} on {sightseeing['date']} "
            f"with an entry fee of ₹{sightseeing['entry_fee']}."
        ),
        "sightseeing_details": sightseeing
    }

def normalize_date(date_str: str) -> str:
    """Normalize dates to YYYY-MM-DD."""
    try:
        date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
        if re.match(r'[A-Za-z]+\s+\d{1,2}(?:,\s*\d{4})?', date_str):
            if not re.search(r'\d{4}', date_str):
                date_str += ", 2025"
            return datetime.strptime(date_str.strip(), '%B %d, %Y').strftime('%Y-%m-%d')
        elif re.match(r'\d{4}-\d{2}-\d{2}', date_str):
            return date_str
        elif re.match(r'\d{1,2}[-/]\d{1,2}[-/]\d{4}', date_str):
            parts = re.split(r'[-/]', date_str)
            return f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
    except Exception as e:
        print(f"Date normalization error: {e}")
    return date_str