from google.adk.tools.tool_context import ToolContext
import re
from datetime import datetime
from core.ticket_utils import (
    generate_pnr, generate_ticket_number, generate_boarding_pass,
    generate_ferry_ticket, generate_metro_token, generate_tram_pass
)

def parse_travel_details(tool_context: ToolContext, user_input: str) -> dict:
    details = {}

    from_to_pattern = r"from\s+([A-Za-z\s]+?)\s+to\s+([A-Za-z\s]+?)(?:\s|,|\.|$)"
    match = re.search(from_to_pattern, user_input, re.IGNORECASE)
    if match:
        details['travel_from'] = match.group(1).strip()
        details['travel_to'] = match.group(2).strip()

    date_patterns = [
        r"on\s+([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)",
        r"(\d{4}-\d{2}-\d{2})",
        r"(\d{1,2}[-/]\d{1,2}[-/]\d{4})"
    ]
    for pattern in date_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            details['travel_date'] = normalize_date(match.group(1).strip())
            break

    mode_match = re.search(r"(train|flight|bus|car|cab|plane|metro|tram|ferry)", user_input, re.IGNORECASE)
    if mode_match:
        mode = mode_match.group(1).lower()
        if mode == "plane":
            mode = "flight"
        details['travel_mode'] = mode

    price_match = re.search(r"(?:price|fare|cost|budget).{0,10}?(\d{3,6})", user_input, re.IGNORECASE)
    if price_match:
        details['travel_price'] = int(price_match.group(1))

    if details:
        tool_context.state.update(details)

    return {
        "action": "parse_travel_details",
        "status": "success",
        "message": f"Extracted travel details: {details}",
        "extracted_details": details
    }

def normalize_date(date_str: str) -> str:
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
    except:
        pass
    return date_str

def check_travel_state(tool_context: ToolContext) -> dict:
    required_fields = {
        'travel_from': 'Origin',
        'travel_to': 'Destination',
        'travel_date': 'Date',
        'travel_mode': 'Mode of travel',
        'travel_price': 'Price'
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
            "message": f"Missing travel details: {', '.join(missing)}",
            "available_data": available,
            "missing_fields": missing
        }
    else:
        return {
            "action": "check_state",
            "status": "ready_to_book",
            "message": "All travel details are available. Ready to proceed with booking.",
            "available_data": available,
            "missing_fields": []
        }

def book_travel(tool_context: ToolContext) -> dict:
    trip_plan = tool_context.state.get("trip_plan", {})
    mode = tool_context.state.get("travel_mode")

    id_map = {
        "train": generate_pnr,
        "flight": generate_boarding_pass,
        "bus": generate_ticket_number,
        "ferry": generate_ferry_ticket,
        "metro": generate_metro_token,
        "tram": generate_tram_pass,
        "cab": lambda: "CAB-" + tool_context.state.get("travel_from", "")[:2].upper() + "-" + tool_context.state.get("travel_to", "")[:2].upper(),
        "car": lambda: "CAR-" + tool_context.state.get("travel_date", "").replace("-", "")
    }

    travel_id = id_map.get(mode, lambda: "TKT-UNKNOWN")()

    travel = {
        "from": tool_context.state.get("travel_from"),
        "to": tool_context.state.get("travel_to"),
        "date": tool_context.state.get("travel_date"),
        "mode": mode,
        "price": tool_context.state.get("travel_price"),
        "ticket_id": travel_id
    }

    trip_plan["travel"] = travel
    tool_context.state["trip_plan"] = trip_plan

    return {
        "action": "book_travel",
        "status": "success",
        "message": (
            f"Travel confirmed from {travel['from']} to {travel['to']} on {travel['date']} via {mode}. "
            f"Estimated cost: ₹{travel['price']}. Ticket ID: {travel_id}"
        ),
        "travel_details": travel
    }