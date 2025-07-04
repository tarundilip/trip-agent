from google.adk.tools.tool_context import ToolContext
import re
from datetime import datetime

def parse_accommodation_details(tool_context: ToolContext, user_input: str) -> dict:
    """Parse accommodation details from user's natural language input."""
    details = {}
    
    location_patterns = [
        r"(?:in|at|to)\s+([A-Za-z\s]+?)(?:\s+from|\s+for|\s+,|\s+\.|$)",
        r"accommodation\s+in\s+([A-Za-z\s]+?)(?:\s+from|\s+for|\s+,|\s+\.|$)"
    ]
    for pattern in location_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            details['accommodation_location'] = match.group(1).strip()
            break

    date_patterns = [
        r"from\s+([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)\s+to\s+([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)",
        r"(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})",
        r"(\d{1,2}[-/]\d{1,2}[-/]\d{4})\s+to\s+(\d{1,2}[-/]\d{1,2}[-/]\d{4})"
    ]
    for pattern in date_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            check_in = normalize_date(match.group(1).strip())
            check_out = normalize_date(match.group(2).strip())
            details['accommodation_check_in'] = check_in
            details['accommodation_check_out'] = check_out
            break

    budget_patterns = [
        r"budget\s+(?:is|of)?\s*(\d+)\s*rupees?\s*per\s*night",
        r"(\d+)\s*rupees?\s*per\s*night",
        r"budget\s+(?:is|of)?\s*₹?\s*(\d+)\s*per\s*night"
    ]
    for pattern in budget_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            details['accommodation_budget'] = int(match.group(1))
            break

    total_patterns = [
        r"(?:total\s+(?:cost|budget|price)?\s*(?:should\s+be\s+)?(?:around\s+)?₹?\s*(\d+))",
        r"(?:₹?\s*(\d+)\s*(?:rupees)?\s*(?:total|overall|in\s+total|for\s+the\s+stay))",
        r"my\s+total\s+(?:budget|cost|price)\s+(?:is|should\s+be)?\s*₹?\s*(\d+)"
    ]
    for pattern in total_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            details['accommodation_total_price'] = int(match.group(1))
            break

    if details:
        tool_context.state.update(details)

    return {
        "action": "parse_accommodation_details",
        "status": "success",
        "message": f"Extracted accommodation details: {details}",
        "extracted_details": details
    }

def normalize_date(date_str: str) -> str:
    try:
        if re.match(r'[A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?', date_str):
            cleaned = re.sub(r'(\d+)(?:st|nd|rd|th)', r'\1', date_str)
            if not re.search(r'\d{4}', cleaned):
                cleaned += ', 2025'
            try:
                return datetime.strptime(cleaned, '%B %d, %Y').strftime('%Y-%m-%d')
            except ValueError:
                return datetime.strptime(cleaned, '%b %d, %Y').strftime('%Y-%m-%d')
        elif re.match(r'\d{4}-\d{2}-\d{2}', date_str):
            return date_str
        elif re.match(r'\d{1,2}[-/]\d{1,2}[-/]\d{4}', date_str):
            parts = re.split(r'[-/]', date_str)
            return f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
    except Exception as e:
        print(f"Error normalizing date {date_str}: {e}")
    return date_str

def check_accommodation_state(tool_context: ToolContext) -> dict:
    required_fields = {
        'accommodation_location': 'Location',
        'accommodation_check_in': 'Check-in date',
        'accommodation_check_out': 'Check-out date',
        'accommodation_budget': 'Budget per night',
        'accommodation_total_price': 'Total price'
    }

    available_data = {}
    missing_fields = []

    for field, label in required_fields.items():
        value = tool_context.state.get(field)
        if value:
            available_data[field] = value
        else:
            missing_fields.append(label)

    if missing_fields:
        return {
            "action": "check_state",
            "status": "missing_data",
            "message": f"Missing accommodation details: {', '.join(missing_fields)}",
            "available_data": available_data,
            "missing_fields": missing_fields
        }
    else:
        return {
            "action": "check_state",
            "status": "ready_to_book",
            "message": "All accommodation details are available. Ready to proceed with booking.",
            "available_data": available_data,
            "missing_fields": []
        }

def book_accommodation(tool_context: ToolContext) -> dict:
    trip_plan = tool_context.state.get("trip_plan", {})

    check_in = tool_context.state.get("accommodation_check_in")
    check_out = tool_context.state.get("accommodation_check_out")
    price_per_night = tool_context.state.get("accommodation_budget", 0)
    total_price = tool_context.state.get("accommodation_total_price")

    if total_price is None and check_in and check_out:
        try:
            nights = (datetime.strptime(check_out, "%Y-%m-%d") - datetime.strptime(check_in, "%Y-%m-%d")).days
            total_price = price_per_night * nights
        except Exception:
            total_price = "not specified"

    accommodation = {
        "location": tool_context.state.get("accommodation_location"),
        "check_in": check_in,
        "check_out": check_out,
        "budget": price_per_night,
        "total_price": total_price
    }

    trip_plan["accommodation"] = accommodation
    tool_context.state.update({"trip_plan": trip_plan})

    return {
        "action": "book_accommodation",
        "status": "success",
        "message": (
            f"Hotel booking confirmed in {accommodation['location']} from {check_in} to {check_out} "
            f"within your budget of ₹{price_per_night} per night. Total cost: ₹{total_price}"
        )
    }