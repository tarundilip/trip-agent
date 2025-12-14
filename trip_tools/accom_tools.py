"""
Accommodation tools with email notifications, cancellation, and improved date/cost handling
"""
from google.adk.tools.tool_context import ToolContext
import re
import uuid
from datetime import datetime, timedelta
from loguru import logger

# ✅ IMPORT NOTIFICATION SERVICE
from core.notifications import notification_service


def parse_accommodation_details(tool_context: ToolContext, user_input: str) -> dict:
    """Parse accommodation details from user's natural language input."""
    details = {}
    
    # Location extraction
    location_patterns = [
        r"(?:in|at|near)\s+([A-Za-z\s]+?)(?:\s+from|\s+on|\s+for|,|\.|$)",
        r"accommodation\s+(?:in|at|near)\s+([A-Za-z\s]+?)(?:\s|,|\.|$)",
        r"hotel\s+(?:in|at|near)\s+([A-Za-z\s]+?)(?:\s|,|\.|$)",
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            details['accommodation_location'] = match.group(1).strip()
            break
    
    # ✅ IMPROVED: Check-in date extraction
    checkin_patterns = [
        r"check.?in\s+(?:on\s+)?([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)",
        r"from\s+([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)",
        r"starting\s+([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)",
        r"book.*?from\s+([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)",
    ]
    
    for pattern in checkin_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            details['accommodation_check_in'] = normalize_date(match.group(1).strip())
            break
    
    # ✅ IMPROVED: Check-out date extraction
    checkout_patterns = [
        r"check.?out\s+(?:on\s+)?([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)",
        r"to\s+([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)",
        r"until\s+([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)",
        r"till\s+([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)",
    ]
    
    for pattern in checkout_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            details['accommodation_check_out'] = normalize_date(match.group(1).strip())
            break
    
    # ✅ NEW: Extract number of nights directly
    nights_pattern = r"(?:for\s+)?(\d+)\s+night(?:s)?"
    nights_match = re.search(nights_pattern, user_input, re.IGNORECASE)
    if nights_match:
        nights = int(nights_match.group(1))
        details['accommodation_nights'] = nights
        
        # If check-in is known but check-out isn't, calculate it
        if 'accommodation_check_in' in details and 'accommodation_check_out' not in details:
            try:
                check_in_date = datetime.strptime(details['accommodation_check_in'], '%Y-%m-%d')
                check_out_date = check_in_date + timedelta(days=nights)
                details['accommodation_check_out'] = check_out_date.strftime('%Y-%m-%d')
                logger.info(f"✅ Calculated check-out from {nights} nights: {details['accommodation_check_out']}")
            except Exception as e:
                logger.warning(f"Could not calculate check-out date: {e}")
    
    # Budget/Price extraction (per night)
    budget_patterns = [
        r"budget\s+(?:of\s+)?(?:rs\.?\s*|₹\s*)?(\d+)\s+per\s+night",
        r"(?:rs\.?\s*|₹\s*)(\d+)\s+per\s+night",
        r"(?:rs\.?\s*|₹\s*)(\d+)\s*/\s*night",
        r"price\s+(?:of\s+)?(?:rs\.?\s*|₹\s*)?(\d+)\s+per\s+night",
    ]
    
    for pattern in budget_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            details['accommodation_budget'] = int(match.group(1))
            logger.info(f"✅ Extracted per-night rate: ₹{details['accommodation_budget']}")
            break
    
    # ✅ NEW: Extract total cost if mentioned
    total_patterns = [
        r"total\s+(?:cost|price)?\s*(?:of\s+)?(?:rs\.?\s*|₹\s*)?(\d+)",
        r"(?:rs\.?\s*|₹\s*)(\d+)\s+total",
    ]
    
    for pattern in total_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            details['accommodation_total_price'] = int(match.group(1))
            logger.info(f"✅ Extracted total price: ₹{details['accommodation_total_price']}")
            break
    
    # Update state
    if details:
        tool_context.state.update(details)
    
    return {
        "action": "parse_accommodation_details",
        "status": "success",
        "message": f"Extracted accommodation details: {details}",
        "extracted_details": details
    }


def normalize_date(date_str: str) -> str:
    """Normalize dates to YYYY-MM-DD format."""
    try:
        # Remove ordinal suffixes (1st, 2nd, 3rd, 4th)
        date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
        
        # Handle "Month Day, Year" or "Month Day"
        if re.match(r'[A-Za-z]+\s+\d{1,2}(?:,\s*\d{4})?', date_str):
            if not re.search(r'\d{4}', date_str):
                date_str += ", 2025"
            return datetime.strptime(date_str.strip(), '%B %d, %Y').strftime('%Y-%m-%d')
        
        # Already in YYYY-MM-DD format
        elif re.match(r'\d{4}-\d{2}-\d{2}', date_str):
            return date_str
        
        # Handle DD/MM/YYYY or DD-MM-YYYY
        elif re.match(r'\d{1,2}[-/]\d{1,2}[-/]\d{4}', date_str):
            parts = re.split(r'[-/]', date_str)
            return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
    except Exception as e:
        logger.warning(f"Date parsing failed for '{date_str}': {e}")
    
    return date_str


def check_accommodation_state(tool_context: ToolContext) -> dict:
    """Check if required accommodation information is available."""
    required_fields = {
        'accommodation_location': 'Location',
        'accommodation_check_in': 'Check-in date',
        'accommodation_check_out': 'Check-out date'
    }
    
    optional_fields = {
        'accommodation_budget': 'Budget per night',
        'accommodation_nights': 'Number of nights',
        'accommodation_total_price': 'Total price'
    }
    
    available = {}
    missing = []
    
    for key, label in required_fields.items():
        val = tool_context.state.get(key)
        if val:
            available[key] = val
        else:
            missing.append(label)
    
    # Include optional fields if present
    for key in optional_fields:
        if tool_context.state.get(key):
            available[key] = tool_context.state.get(key)
    
    if missing:
        return {
            "action": "check_state",
            "status": "missing_data",
            "message": f"Missing accommodation details: {', '.join(missing)}",
            "available_data": available,
            "missing_fields": missing
        }
    else:
        return {
            "action": "check_state",
            "status": "ready_to_book",
            "message": "All required accommodation details are available. Ready to proceed with booking.",
            "available_data": available,
            "missing_fields": []
        }


async def book_accommodation(tool_context: ToolContext) -> dict:
    """Book accommodation with email notification and improved cost calculation."""
    trip_plan = tool_context.state.get("trip_plan", {})

    check_in = tool_context.state.get("accommodation_check_in")
    check_out = tool_context.state.get("accommodation_check_out")
    location = tool_context.state.get("accommodation_location", "your selected location")
    price_per_night = tool_context.state.get("accommodation_budget", 0)
    total_price = tool_context.state.get("accommodation_total_price")
    nights_from_user = tool_context.state.get("accommodation_nights")

    # ✅ IMPROVED: Calculate nights accurately
    if check_in and check_out:
        try:
            check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
            check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
            nights = (check_out_date - check_in_date).days
            
            if nights <= 0:
                nights = 1
                logger.warning(f"Check-out is same/before check-in. Setting nights to 1.")
            
            logger.info(f"✅ Calculated nights: {nights} (from {check_in} to {check_out})")
        except Exception as e:
            logger.error(f"Date calculation error: {e}")
            nights = nights_from_user or 1
    else:
        nights = nights_from_user or 1
    
    # ✅ IMPROVED: Calculate total price intelligently
    if total_price is None:
        if price_per_night > 0:
            total_price = price_per_night * nights
            logger.info(f"✅ Calculated total: ₹{price_per_night} × {nights} nights = ₹{total_price}")
        else:
            # Try to extract from conversation
            conversation_result = tool_context.state.get("conversation_result", "")
            price_match = re.search(r'₹\s*(\d+)', conversation_result)
            if price_match:
                price_per_night = int(price_match.group(1))
                total_price = price_per_night * nights
            else:
                price_per_night = 0
                total_price = 0
    else:
        # If total is given, calculate per-night rate
        if price_per_night == 0 and nights > 0:
            price_per_night = total_price // nights
            logger.info(f"✅ Calculated per-night rate: ₹{total_price} ÷ {nights} = ₹{price_per_night}/night")

    # Generate booking ID
    location_code = location[:3].upper() if location else "HTL"
    date_code = check_in.replace("-", "") if check_in else datetime.now().strftime("%Y%m%d")
    booking_id = f"HTL-{location_code}-{date_code}-{str(uuid.uuid4())[:8].upper()}"

    accommodation = {
        "location": location,
        "check_in": check_in,
        "check_out": check_out,
        "nights": nights,
        "budget": price_per_night,
        "total_price": total_price,
        "booking_id": booking_id
    }

    trip_plan["accommodation"] = accommodation
    tool_context.state.update({"trip_plan": trip_plan})
    
    # ✅ SEND EMAIL NOTIFICATION
    user_email = tool_context.state.get("user_email")
    user_name = tool_context.state.get("user_name", "Guest")
    
    notification_msg = ""
    
    if user_email:
        try:
            logger.info(f"📧 Sending accommodation booking email to {user_email}")
            
            results = await notification_service.send_booking_notification(
                user_email=user_email,
                user_name=user_name,
                booking_type="Accommodation",
                booking_details=accommodation,
                booking_id=booking_id
            )
            
            if results["email_sent"]:
                notification_msg = f"\n\n📧 **Confirmation email sent to {user_email}**"
                logger.info(f"✅ Accommodation email sent to {user_email}")
            else:
                notification_msg = f"\n\n⚠️ **Email notification failed**"
                logger.warning(f"❌ Accommodation email failed for {user_email}")
                
        except Exception as e:
            logger.error(f"❌ Accommodation notification error: {e}", exc_info=True)
            notification_msg = f"\n\n⚠️ **Could not send email notification**"
    else:
        logger.warning("ℹ️ No email address - skipping notification")
        notification_msg = "\n\n⚠️ **No email address provided**"
    
    # Build message
    if price_per_night > 0:
        price_info = f"💰 Rate: ₹{price_per_night}/night × {nights} nights = **₹{total_price}**"
    else:
        price_info = "💰 Price to be confirmed"

    return {
        "action": "book_accommodation",
        "status": "success",
        "message": (
            f"✅ **Hotel booking confirmed!**\n\n"
            f"🏨 Location: {location}\n"
            f"📅 Check-in: {check_in} | Check-out: {check_out}\n"
            f"🌙 Nights: {nights}\n"
            f"{price_info}\n\n"
            f"🎫 **Booking ID:** `{booking_id}`"
            f"{notification_msg}"
        ),
        "accommodation_details": accommodation
    }


# ✅ NEW: CANCEL ACCOMMODATION BOOKING
async def cancel_accommodation_booking(tool_context: ToolContext) -> dict:
    """Cancel accommodation booking with email notification"""
    try:
        trip_plan = tool_context.state.get("trip_plan", {})
        
        if not trip_plan or 'accommodation' not in trip_plan:
            return {
                "action": "cancel_accommodation",
                "status": "not_found",
                "message": "❌ No active accommodation booking found to cancel."
            }
        
        accommodation = trip_plan['accommodation']
        booking_id = accommodation.get('booking_id', 'N/A')
        total_price = accommodation.get('total_price', 0)
        
        # Store in cancelled history
        cancelled_bookings = tool_context.state.get("cancelled_bookings", [])
        cancelled_bookings.append({
            "type": "accommodation",
            "booking_id": booking_id,
            "details": accommodation,
            "cancelled_at": datetime.now().isoformat()
        })
        tool_context.state["cancelled_bookings"] = cancelled_bookings
        
        del trip_plan['accommodation']
        tool_context.state["trip_plan"] = trip_plan
        
        user_email = tool_context.state.get("user_email")
        user_name = tool_context.state.get("user_name", "Guest")
        
        notification_msg = ""
        
        if user_email:
            try:
                logger.info(f"📧 Sending accommodation cancellation email to {user_email}")
                
                cancellation_details = {
                    **accommodation,
                    "status": "CANCELLED",
                    "cancellation_reason": "User requested cancellation"
                }
                
                results = await notification_service.send_booking_notification(
                    user_email=user_email,
                    user_name=user_name,
                    booking_type="ACCOMMODATION - CANCELLED",
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
        if total_price > 0:
            refund_msg = f"\n💰 **Refund Amount:** ₹{total_price} (processed within 5-7 business days)"
        
        logger.info(f"✅ Accommodation booking cancelled: {booking_id}")
        
        return {
            "action": "cancel_accommodation",
            "status": "success",
            "message": (
                f"✅ **ACCOMMODATION BOOKING CANCELLED**\n\n"
                f"🎫 **Booking ID:** `{booking_id}`\n"
                f"🏨 Location: {accommodation.get('location')}\n"
                f"📅 Dates: {accommodation.get('check_in')} to {accommodation.get('check_out')}\n"
                f"🌙 Nights: {accommodation.get('nights')}"
                f"{refund_msg}"
                f"{notification_msg}\n\n"
                f"💡 You can make a new booking anytime!"
            ),
            "cancelled_booking": accommodation
        }
        
    except Exception as e:
        logger.error(f"❌ Cancel accommodation failed: {str(e)}", exc_info=True)
        return {
            "action": "cancel_accommodation",
            "status": "error",
            "message": f"Failed to cancel accommodation booking: {str(e)}"
        }