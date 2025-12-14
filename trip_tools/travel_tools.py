"""
Travel tools with email notifications, optional pricing, and cancellation
"""
from google.adk.tools.tool_context import ToolContext
import re
from datetime import datetime
from loguru import logger

# ✅ IMPORT NOTIFICATION SERVICE
from core.notifications import notification_service

from core.ticket_utils import (
    generate_pnr, generate_ticket_number, generate_boarding_pass,
    generate_ferry_ticket, generate_metro_token, generate_tram_pass
)

def parse_travel_details(tool_context: ToolContext, user_input: str) -> dict:
    """Parse travel details from user's natural language input."""
    details = {}

    # From/To extraction
    from_to_pattern = r"from\s+([A-Za-z\s]+?)\s+to\s+([A-Za-z\s]+?)(?:\s|,|\.|$)"
    match = re.search(from_to_pattern, user_input, re.IGNORECASE)
    if match:
        details['travel_from'] = match.group(1).strip()
        details['travel_to'] = match.group(2).strip()

    # Date extraction
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

    # Mode extraction
    mode_match = re.search(r"(train|flight|bus|car|cab|plane|metro|tram|ferry)", user_input, re.IGNORECASE)
    if mode_match:
        mode = mode_match.group(1).lower()
        if mode == "plane":
            mode = "flight"
        details['travel_mode'] = mode

    # Extract transport name/number
    transport_patterns = [
        r"(?:train|flight|bus|ferry|metro|tram)\s+(?:name|number|no\.?|#)?\s*[:–-]?\s*([A-Za-z0-9\s]+?)(?:\s+on|\s+from|\s+to|,|\.|$)",
        r"(?:by|via)\s+(?:the\s+)?([A-Za-z0-9\s]+?)\s+(?:train|flight|bus|ferry|metro|tram)",
        r"([A-Za-z0-9\s]+?)\s+(?:Express|Superfast|Rajdhani|Shatabdi|Airways|Airlines|Travels|Mail)",
    ]
    
    for pattern in transport_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            transport_name = match.group(1).strip()
            transport_name = re.sub(r'^(the|a|an)\s+', '', transport_name, flags=re.IGNORECASE)
            details['transport_name'] = transport_name
            break

    # Price extraction
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
    """Normalize dates to YYYY-MM-DD format."""
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
    """Check if required travel information is available."""
    required_fields = {
        'travel_from': 'Origin',
        'travel_to': 'Destination',
        'travel_date': 'Date',
        'travel_mode': 'Mode of travel'
    }
    
    optional_fields = {
        'transport_name': 'Transport name/number',
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
    
    for key in optional_fields:
        if tool_context.state.get(key):
            available[key] = tool_context.state.get(key)

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
            "message": "All required travel details are available. Ready to proceed with booking.",
            "available_data": available,
            "missing_fields": []
        }


async def book_travel(tool_context: ToolContext) -> dict:
    """Book travel with email notification."""
    trip_plan = tool_context.state.get("trip_plan", {})
    mode = tool_context.state.get("travel_mode")
    
    price = tool_context.state.get("travel_price")
    
    if not price:
        conversation_result = tool_context.state.get("conversation_result", "")
        price_match = re.search(r'₹\s*(\d+)\s*-\s*₹\s*(\d+)', conversation_result)
        if price_match:
            price = int(price_match.group(1))
        else:
            price_match = re.search(r'₹\s*(\d+)', conversation_result)
            if price_match:
                price = int(price_match.group(1))
            else:
                price = 0

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
        "transport_name": tool_context.state.get("transport_name"),
        "price": price,
        "ticket_id": travel_id
    }

    trip_plan["travel"] = travel
    tool_context.state["trip_plan"] = trip_plan

    user_email = tool_context.state.get("user_email")
    user_name = tool_context.state.get("user_name", "Traveler")
    
    notification_msg = ""
    
    if user_email:
        try:
            logger.info(f"📧 Attempting to send travel booking email to {user_email}")
            
            results = await notification_service.send_booking_notification(
                user_email=user_email,
                user_name=user_name,
                booking_type="Travel",
                booking_details=travel,
                booking_id=travel_id
            )
            
            if results["email_sent"]:
                notification_msg = f"\n\n📧 **Confirmation email sent to {user_email}**"
                logger.info(f"✅ Travel booking email sent successfully to {user_email}")
            else:
                notification_msg = f"\n\n⚠️ **Email notification failed**"
                logger.warning(f"❌ Travel booking email failed for {user_email}")
                
        except Exception as e:
            logger.error(f"❌ Travel notification error: {e}", exc_info=True)
            notification_msg = f"\n\n⚠️ **Could not send email notification**"
    else:
        logger.warning("ℹ️ No user_email in state - skipping email notification")
        notification_msg = "\n\n⚠️ **No email address provided**"

    transport_info = f" via {travel['transport_name']}" if travel.get('transport_name') else ""
    price_info = f"Estimated cost: ₹{price}." if price > 0 else "Price to be confirmed."
    
    return {
        "action": "book_travel",
        "status": "success",
        "message": (
            f"✅ **Travel booking confirmed!**\n\n"
            f"📍 From: {travel['from']} → To: {travel['to']}\n"
            f"📅 Date: {travel['date']}\n"
            f"🚆 Mode: {mode}{transport_info}\n"
            f"{price_info}\n\n"
            f"🎫 **Ticket ID:** `{travel_id}`"
            f"{notification_msg}"
        ),
        "travel_details": travel
    }


# ✅ NEW: CANCEL TRAVEL BOOKING
async def cancel_travel_booking(tool_context: ToolContext) -> dict:
    """Cancel travel booking with email notification"""
    try:
        trip_plan = tool_context.state.get("trip_plan", {})
        
        if not trip_plan or 'travel' not in trip_plan:
            return {
                "action": "cancel_travel",
                "status": "not_found",
                "message": "❌ No active travel booking found to cancel."
            }
        
        travel = trip_plan['travel']
        travel_id = travel.get('ticket_id', 'N/A')
        price = travel.get('price', 0)
        
        # Store in cancelled history
        cancelled_bookings = tool_context.state.get("cancelled_bookings", [])
        cancelled_bookings.append({
            "type": "travel",
            "booking_id": travel_id,
            "details": travel,
            "cancelled_at": datetime.now().isoformat()
        })
        tool_context.state["cancelled_bookings"] = cancelled_bookings
        
        del trip_plan['travel']
        tool_context.state["trip_plan"] = trip_plan
        
        user_email = tool_context.state.get("user_email")
        user_name = tool_context.state.get("user_name", "Traveler")
        
        notification_msg = ""
        
        if user_email:
            try:
                logger.info(f"📧 Sending travel cancellation email to {user_email}")
                
                cancellation_details = {
                    **travel,
                    "status": "CANCELLED",
                    "cancellation_reason": "User requested cancellation"
                }
                
                results = await notification_service.send_booking_notification(
                    user_email=user_email,
                    user_name=user_name,
                    booking_type="TRAVEL - CANCELLED",
                    booking_details=cancellation_details,
                    booking_id=travel_id
                )
                
                if results["email_sent"]:
                    notification_msg = f"\n\n📧 **Cancellation confirmation sent to {user_email}**"
                else:
                    notification_msg = f"\n\n⚠️ **Email notification failed**"
                    
            except Exception as e:
                logger.error(f"❌ Cancellation email error: {e}", exc_info=True)
                notification_msg = f"\n\n⚠️ **Could not send email notification**"
        
        refund_msg = ""
        if price > 0:
            refund_msg = f"\n💰 **Refund Amount:** ₹{price} (processed within 5-7 business days)"
        
        logger.info(f"✅ Travel booking cancelled: {travel_id}")
        
        return {
            "action": "cancel_travel",
            "status": "success",
            "message": (
                f"✅ **TRAVEL BOOKING CANCELLED**\n\n"
                f"🎫 **Ticket ID:** `{travel_id}`\n"
                f"📍 Route: {travel.get('from')} → {travel.get('to')}\n"
                f"📅 Date: {travel.get('date')}"
                f"{refund_msg}"
                f"{notification_msg}\n\n"
                f"💡 You can make a new booking anytime!"
            ),
            "cancelled_booking": travel
        }
        
    except Exception as e:
        logger.error(f"❌ Cancel travel failed: {str(e)}", exc_info=True)
        return {
            "action": "cancel_travel",
            "status": "error",
            "message": f"Failed to cancel travel booking: {str(e)}"
        }