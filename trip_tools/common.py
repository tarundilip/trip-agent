"""
Common utility functions for trip planning and booking management
"""
from google.adk.tools.tool_context import ToolContext
from loguru import logger
from datetime import datetime


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


# ✅ NEW: VIEW ACTIVE BOOKINGS
def list_active_bookings(tool_context: ToolContext) -> dict:
    """
    List all active bookings in the current trip plan
    
    Returns a formatted message showing all active bookings across
    travel, accommodation, and sightseeing with booking IDs and prices.
    """
    try:
        trip_plan = tool_context.state.get("trip_plan", {})
        
        if not trip_plan:
            return {
                "action": "list_bookings",
                "status": "no_bookings",
                "message": "You don't have any active bookings to view or cancel.",
                "bookings": []
            }
        
        bookings = []
        
        # Travel booking
        travel = trip_plan.get('travel')
        if travel and travel.get('ticket_id'):
            travel_mode = travel.get('mode', 'travel').capitalize()
            bookings.append({
                "type": "travel",
                "id": travel['ticket_id'],
                "details": f"{travel_mode} from {travel.get('from', 'N/A')} to {travel.get('to', 'N/A')} on {travel.get('date', 'N/A')}",
                "price": travel.get('price', 0),
                "mode": travel.get('mode', 'N/A'),
                "transport_name": travel.get('transport_name', 'N/A')
            })
        
        # Accommodation booking
        accommodation = trip_plan.get('accommodation')
        if accommodation and accommodation.get('booking_id'):
            nights = accommodation.get('nights', 0)
            nights_text = f"({nights} night{'s' if nights != 1 else ''})" if nights > 0 else ""
            bookings.append({
                "type": "accommodation",
                "id": accommodation['booking_id'],
                "details": f"Hotel in {accommodation.get('location', 'N/A')} from {accommodation.get('check_in', 'N/A')} to {accommodation.get('check_out', 'N/A')} {nights_text}",
                "price": accommodation.get('total_price', 0),
                "location": accommodation.get('location', 'N/A'),
                "nights": nights
            })
        
        # Sightseeing booking
        sightseeing = trip_plan.get('sightseeing')
        if sightseeing and sightseeing.get('booking_id'):
            bookings.append({
                "type": "sightseeing",
                "id": sightseeing['booking_id'],
                "details": f"Sightseeing at {sightseeing.get('location', 'N/A')} on {sightseeing.get('date', 'N/A')}",
                "price": sightseeing.get('budget', 0),
                "location": sightseeing.get('location', 'N/A')
            })
        
        if not bookings:
            return {
                "action": "list_bookings",
                "status": "no_bookings",
                "message": "You don't have any active bookings to view or cancel.",
                "bookings": []
            }
        
        # Format message
        message_parts = ["# 📋 **YOUR ACTIVE BOOKINGS**\n"]
        
        total_cost = 0
        for idx, booking in enumerate(bookings, 1):
            message_parts.append(f"\n## {idx}. {booking['type'].upper()}")
            message_parts.append(f"**Booking ID:** `{booking['id']}`")
            message_parts.append(f"**Details:** {booking['details']}")
            
            if booking['price'] > 0:
                message_parts.append(f"**Price:** ₹{booking['price']}")
                total_cost += booking['price']
            else:
                message_parts.append(f"**Price:** To be confirmed")
            
            # Add extra details
            if booking['type'] == 'travel' and booking.get('transport_name') and booking['transport_name'] != 'N/A':
                message_parts.append(f"**Transport:** {booking['transport_name']}")
            
            message_parts.append("")
        
        # Show total if any prices are set
        if total_cost > 0:
            message_parts.append(f"\n💰 **TOTAL COST:** ₹{total_cost}")
        
        message_parts.append("\n💡 **To cancel a booking, say:**")
        message_parts.append("- 'Cancel my travel booking'")
        message_parts.append("- 'Cancel my accommodation booking'")
        message_parts.append("- 'Cancel my sightseeing booking'")
        
        logger.info(f"✅ Listed {len(bookings)} active booking(s)")
        
        return {
            "action": "list_bookings",
            "status": "success",
            "message": "\n".join(message_parts),
            "bookings": bookings,
            "total_bookings": len(bookings),
            "total_cost": total_cost
        }
        
    except Exception as e:
        logger.error(f"❌ List bookings failed: {str(e)}", exc_info=True)
        return {
            "action": "list_bookings",
            "status": "error",
            "message": f"Failed to list bookings: {str(e)}",
            "bookings": []
        }


# ✅ NEW: VIEW CANCELLED BOOKINGS
def view_cancelled_bookings(tool_context: ToolContext) -> dict:
    """
    View history of cancelled bookings
    
    Shows all bookings that were cancelled in the current session
    with cancellation timestamps and original details.
    """
    try:
        cancelled_bookings = tool_context.state.get("cancelled_bookings", [])
        
        if not cancelled_bookings:
            return {
                "action": "view_cancelled",
                "status": "empty",
                "message": "You don't have any cancelled bookings in this session.",
                "cancelled_bookings": []
            }
        
        # Format message
        message_parts = ["# 🗑️ **CANCELLED BOOKINGS HISTORY**\n"]
        
        total_refund = 0
        for idx, cancelled in enumerate(cancelled_bookings, 1):
            booking_type = cancelled['type'].upper()
            message_parts.append(f"\n## {idx}. {booking_type} (❌ Cancelled)")
            message_parts.append(f"**Booking ID:** `{cancelled['booking_id']}`")
            
            # Format cancellation timestamp
            try:
                cancelled_at = datetime.fromisoformat(cancelled['cancelled_at'])
                formatted_time = cancelled_at.strftime("%B %d, %Y at %I:%M %p")
                message_parts.append(f"**Cancelled On:** {formatted_time}")
            except:
                message_parts.append(f"**Cancelled On:** {cancelled['cancelled_at']}")
            
            details = cancelled['details']
            
            # Show specific details based on booking type
            if cancelled['type'] == 'travel':
                message_parts.append(f"**Route:** {details.get('from', 'N/A')} → {details.get('to', 'N/A')}")
                message_parts.append(f"**Date:** {details.get('date', 'N/A')}")
                message_parts.append(f"**Mode:** {details.get('mode', 'N/A').capitalize()}")
                if details.get('transport_name'):
                    message_parts.append(f"**Transport:** {details['transport_name']}")
                refund = details.get('price', 0)
                
            elif cancelled['type'] == 'accommodation':
                message_parts.append(f"**Location:** {details.get('location', 'N/A')}")
                message_parts.append(f"**Check-in:** {details.get('check_in', 'N/A')}")
                message_parts.append(f"**Check-out:** {details.get('check_out', 'N/A')}")
                nights = details.get('nights', 0)
                if nights > 0:
                    message_parts.append(f"**Nights:** {nights}")
                refund = details.get('total_price', 0)
                
            elif cancelled['type'] == 'sightseeing':
                message_parts.append(f"**Location:** {details.get('location', 'N/A')}")
                message_parts.append(f"**Date:** {details.get('date', 'N/A')}")
                refund = details.get('budget', 0)
            else:
                refund = 0
            
            # Show refund amount
            if refund > 0:
                message_parts.append(f"**Refund Amount:** ₹{refund}")
                total_refund += refund
            
            message_parts.append("")
        
        # Show total refund if applicable
        if total_refund > 0:
            message_parts.append(f"\n💰 **TOTAL REFUND:** ₹{total_refund}")
            message_parts.append("⏳ Refunds will be processed within 5-7 business days")
        
        logger.info(f"✅ Displayed {len(cancelled_bookings)} cancelled booking(s)")
        
        return {
            "action": "view_cancelled",
            "status": "success",
            "message": "\n".join(message_parts),
            "cancelled_bookings": cancelled_bookings,
            "total_cancelled": len(cancelled_bookings),
            "total_refund": total_refund
        }
        
    except Exception as e:
        logger.error(f"❌ View cancelled bookings failed: {str(e)}", exc_info=True)
        return {
            "action": "view_cancelled",
            "status": "error",
            "message": f"Failed to view cancelled bookings: {str(e)}",
            "cancelled_bookings": []
        }