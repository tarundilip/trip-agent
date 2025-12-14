"""
Sightseeing tools with email notifications, optional pricing, and cancellation
"""
from google.adk.tools.tool_context import ToolContext
import re
import uuid
from datetime import datetime
from loguru import logger

# ✅ IMPORT NOTIFICATION SERVICE
from core.notifications import notification_service


def parse_sightseeing_details(tool_context: ToolContext, user_input: str) -> dict:
    """Parse sightseeing details from user's natural language input."""
    details = {}
    
    # Location extraction
    location_patterns = [
        r"(?:in|at|visit)\s+([A-Za-z\s]+?)(?:\s+on|\s+for|,|\.|$)",
        r"sightseeing\s+(?:in|at)\s+([A-Za-z\s]+?)(?:\s|,|\.|$)",
        r"tour\s+(?:of|in)\s+([A-Za-z\s]+?)(?:\s|,|\.|$)",
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            details['sightseeing_location'] = match.group(1).strip()
            break
    
    # Date extraction
    date_patterns = [
        r"on\s+([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)",
        r"(\d{4}-\d{2}-\d{2})",
        r"(\d{1,2}[-/]\d{1,2}[-/]\d{4})"
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            details['sightseeing_date'] = normalize_date(match.group(1).strip())
            break
    
    # Budget/Price extraction
    budget_patterns = [
        r"budget\s+(?:of\s+)?(?:rs\.?\s*|₹\s*)?(\d+)",
        r"(?:rs\.?\s*|₹\s*)(\d+)",
        r"price\s+(?:of\s+)?(?:rs\.?\s*|₹\s*)?(\d+)",
    ]
    
    for pattern in budget_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            details['sightseeing_budget'] = int(match.group(1))
            break
    
    if details:
        tool_context.state.update(details)
    
    return {
        "action": "parse_sightseeing_details",
        "status": "success",
        "message": f"Extracted sightseeing details: {details}",
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
            return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
    except Exception as e:
        logger.warning(f"Date parsing failed for '{date_str}': {e}")
    
    return date_str


def check_sightseeing_state(tool_context: ToolContext) -> dict:
    """Check if required sightseeing information is available."""
    required_fields = {
        'sightseeing_location': 'Location',
        'sightseeing_date': 'Date'
    }
    
    optional_fields = {
        'sightseeing_budget': 'Budget'
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
            "message": f"Missing sightseeing details: {', '.join(missing)}",
            "available_data": available,
            "missing_fields": missing
        }
    else:
        return {
            "action": "check_state",
            "status": "ready_to_book",
            "message": "All required sightseeing details are available. Ready to proceed with booking.",
            "available_data": available,
            "missing_fields": []
        }


def plan_sightseeing(tool_context: ToolContext) -> dict:
    """Plan sightseeing activities (legacy function)"""
    logger.info("📍 plan_sightseeing called (redirecting to parse)")
    
    user_input = tool_context.state.get("last_user_message", "")
    
    if not user_input:
        return {
            "action": "plan_sightseeing",
            "status": "info",
            "message": "Please provide sightseeing details (location, date, budget)"
        }
    
    result = parse_sightseeing_details(tool_context, user_input)
    state_check = check_sightseeing_state(tool_context)
    
    if state_check["status"] == "ready_to_book":
        return {
            "action": "plan_sightseeing",
            "status": "ready",
            "message": "Sightseeing details captured. Ready to book!",
            "details": state_check["available_data"]
        }
    else:
        return {
            "action": "plan_sightseeing",
            "status": "incomplete",
            "message": state_check["message"],
            "missing": state_check["missing_fields"]
        }


async def book_sightseeing(tool_context: ToolContext) -> dict:
    """Book sightseeing with email notification and optional pricing."""
    trip_plan = tool_context.state.get("trip_plan", {})

    location = tool_context.state.get("sightseeing_location", "your selected location")
    date = tool_context.state.get("sightseeing_date")
    budget = tool_context.state.get("sightseeing_budget", 0)

    if budget == 0:
        conversation_result = tool_context.state.get("conversation_result", "")
        price_match = re.search(r'₹\s*(\d+)', conversation_result)
        if price_match:
            budget = int(price_match.group(1))

    location_code = location[:3].upper() if location else "SSG"
    date_code = date.replace("-", "") if date else datetime.now().strftime("%Y%m%d")
    booking_id = f"SSG-{location_code}-{date_code}-{str(uuid.uuid4())[:8].upper()}"

    sightseeing = {
        "location": location,
        "date": date,
        "budget": budget,
        "booking_id": booking_id
    }

    trip_plan["sightseeing"] = sightseeing
    tool_context.state.update({"trip_plan": trip_plan})
    
    user_email = tool_context.state.get("user_email")
    user_name = tool_context.state.get("user_name", "Traveler")
    
    notification_msg = ""
    
    if user_email:
        try:
            logger.info(f"📧 Sending sightseeing booking email to {user_email}")
            
            results = await notification_service.send_booking_notification(
                user_email=user_email,
                user_name=user_name,
                booking_type="Sightseeing",
                booking_details=sightseeing,
                booking_id=booking_id
            )
            
            if results["email_sent"]:
                notification_msg = f"\n\n📧 **Confirmation email sent to {user_email}**"
                logger.info(f"✅ Sightseeing email sent to {user_email}")
            else:
                notification_msg = f"\n\n⚠️ **Email notification failed**"
                logger.warning(f"❌ Sightseeing email failed for {user_email}")
                
        except Exception as e:
            logger.error(f"❌ Sightseeing notification error: {e}", exc_info=True)
            notification_msg = f"\n\n⚠️ **Could not send email notification**"
    else:
        logger.warning("ℹ️ No email address - skipping notification")
        notification_msg = "\n\n⚠️ **No email address provided**"
    
    if budget > 0:
        price_info = f"💰 Budget: ₹{budget}"
    else:
        price_info = "💰 Price to be confirmed"

    return {
        "action": "book_sightseeing",
        "status": "success",
        "message": (
            f"✅ **Sightseeing tour booked!**\n\n"
            f"📍 Location: {location}\n"
            f"📅 Date: {date}\n"
            f"{price_info}\n\n"
            f"🎫 **Booking ID:** `{booking_id}`"
            f"{notification_msg}"
        ),
        "sightseeing_details": sightseeing
    }


# ✅ NEW: CANCEL SIGHTSEEING BOOKING
async def cancel_sightseeing_booking(tool_context: ToolContext) -> dict:
    """Cancel sightseeing booking with email notification"""
    try:
        trip_plan = tool_context.state.get("trip_plan", {})
        
        if not trip_plan or 'sightseeing' not in trip_plan:
            return {
                "action": "cancel_sightseeing",
                "status": "not_found",
                "message": "❌ No active sightseeing booking found to cancel."
            }
        
        sightseeing = trip_plan['sightseeing']
        booking_id = sightseeing.get('booking_id', 'N/A')
        budget = sightseeing.get('budget', 0)
        
        cancelled_bookings = tool_context.state.get("cancelled_bookings", [])
        cancelled_bookings.append({
            "type": "sightseeing",
            "booking_id": booking_id,
            "details": sightseeing,
            "cancelled_at": datetime.now().isoformat()
        })
        tool_context.state["cancelled_bookings"] = cancelled_bookings
        
        del trip_plan['sightseeing']
        tool_context.state["trip_plan"] = trip_plan
        
        user_email = tool_context.state.get("user_email")
        user_name = tool_context.state.get("user_name", "Traveler")
        
        notification_msg = ""
        
        if user_email:
            try:
                logger.info(f"📧 Sending sightseeing cancellation email to {user_email}")
                
                cancellation_details = {
                    **sightseeing,
                    "status": "CANCELLED",
                    "cancellation_reason": "User requested cancellation"
                }
                
                results = await notification_service.send_booking_notification(
                    user_email=user_email,
                    user_name=user_name,
                    booking_type="SIGHTSEEING - CANCELLED",
                    booking_details=cancellation_details,
                    booking_id=booking_id
                )
                
                if results["email_sent"]:
                    notification_msg = f"\n\n📧 **Cancellation confirmation sent to {user_email}**"
                else:
                    notification_msg = f"\n\n⚠️ **Email notification failed**"
                    
            except Exception as e:
                logger.error(f"❌ Cancellation email error: {e}", exc_info=True)
                notification_msg = f"\n\n⚠️ **Could not send email notification**"
        
        refund_msg = ""
        if budget > 0:
            refund_msg = f"\n💰 **Refund Amount:** ₹{budget} (processed within 5-7 business days)"
        
        logger.info(f"✅ Sightseeing booking cancelled: {booking_id}")
        
        return {
            "action": "cancel_sightseeing",
            "status": "success",
            "message": (
                f"✅ **SIGHTSEEING BOOKING CANCELLED**\n\n"
                f"🎫 **Booking ID:** `{booking_id}`\n"
                f"📍 Location: {sightseeing.get('location')}\n"
                f"📅 Date: {sightseeing.get('date')}"
                f"{refund_msg}"
                f"{notification_msg}\n\n"
                f"💡 You can make a new booking anytime!"
            ),
            "cancelled_booking": sightseeing
        }
        
    except Exception as e:
        logger.error(f"❌ Cancel sightseeing failed: {str(e)}", exc_info=True)
        return {
            "action": "cancel_sightseeing",
            "status": "error",
            "message": f"Failed to cancel sightseeing booking: {str(e)}"
        }