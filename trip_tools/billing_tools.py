"""
Billing tools for trip planner - Calculate total costs
"""
from google.adk.tools.tool_context import ToolContext
from loguru import logger
from typing import Dict, Any

def calculate_total_bill(tool_context: ToolContext) -> dict:
    """
    Calculate the complete bill for all bookings in the current session.
    Returns itemized breakdown and total cost.
    
    This is the main billing function used by the billing_agent.
    """
    try:
        trip_plan = tool_context.state.get("trip_plan", {})
        
        if not trip_plan:
            return {
                "action": "calculate_bill",
                "status": "no_bookings",
                "message": "No bookings found in this session. Please make some bookings first.",
                "total_amount": 0,
                "breakdown": {}
            }
        
        # Initialize bill components
        bill_breakdown = {
            "travel": {"items": [], "subtotal": 0},
            "accommodation": {"items": [], "subtotal": 0},
            "sightseeing": {"items": [], "subtotal": 0}
        }
        
        total_amount = 0
        
        # ✅ TRAVEL COSTS
        travel = trip_plan.get('travel')
        if travel:
            price = travel.get('price', 0)
            if price > 0:
                bill_breakdown["travel"]["items"].append({
                    "description": f"{travel.get('mode', 'Travel').title()} from {travel.get('from')} to {travel.get('to')}",
                    "date": travel.get('date'),
                    "ticket_id": travel.get('ticket_id'),
                    "amount": price
                })
                bill_breakdown["travel"]["subtotal"] = price
                total_amount += price
        
        # ✅ ACCOMMODATION COSTS
        accommodation = trip_plan.get('accommodation')
        if accommodation:
            total_price = accommodation.get('total_price', 0)
            if total_price > 0:
                nights = accommodation.get('nights', 0)
                rate = accommodation.get('budget', 0)
                bill_breakdown["accommodation"]["items"].append({
                    "description": f"Hotel in {accommodation.get('location')}",
                    "check_in": accommodation.get('check_in'),
                    "check_out": accommodation.get('check_out'),
                    "nights": nights,
                    "rate_per_night": rate,
                    "booking_id": accommodation.get('booking_id'),
                    "amount": total_price
                })
                bill_breakdown["accommodation"]["subtotal"] = total_price
                total_amount += total_price
        
        # ✅ SIGHTSEEING COSTS
        sightseeing = trip_plan.get('sightseeing')
        if sightseeing:
            budget = sightseeing.get('budget', 0)
            if budget > 0:
                bill_breakdown["sightseeing"]["items"].append({
                    "description": f"Sightseeing at {sightseeing.get('location')}",
                    "date": sightseeing.get('date'),
                    "booking_id": sightseeing.get('booking_id'),
                    "amount": budget
                })
                bill_breakdown["sightseeing"]["subtotal"] = budget
                total_amount += budget
        
        # Store bill in state
        tool_context.state["trip_bill"] = {
            "breakdown": bill_breakdown,
            "total": total_amount
        }
        
        # ✅ BUILD FORMATTED MESSAGE
        message_parts = ["# 🧾 **TRIP BILL SUMMARY**\n"]
        
        # Travel section
        if bill_breakdown["travel"]["subtotal"] > 0:
            message_parts.append("## 🚆 **Travel**")
            for item in bill_breakdown["travel"]["items"]:
                message_parts.append(f"- {item['description']}")
                message_parts.append(f"  - Date: {item['date']}")
                message_parts.append(f"  - Ticket ID: `{item['ticket_id']}`")
                message_parts.append(f"  - **Amount: ₹{item['amount']}**")
            message_parts.append(f"**Subtotal: ₹{bill_breakdown['travel']['subtotal']}**\n")
        
        # Accommodation section
        if bill_breakdown["accommodation"]["subtotal"] > 0:
            message_parts.append("## 🏨 **Accommodation**")
            for item in bill_breakdown["accommodation"]["items"]:
                message_parts.append(f"- {item['description']}")
                message_parts.append(f"  - Check-in: {item['check_in']}")
                message_parts.append(f"  - Check-out: {item['check_out']}")
                if item['nights'] > 0 and item['rate_per_night'] > 0:
                    message_parts.append(f"  - {item['nights']} night(s) × ₹{item['rate_per_night']} per night")
                message_parts.append(f"  - Booking ID: `{item['booking_id']}`")
                message_parts.append(f"  - **Amount: ₹{item['amount']}**")
            message_parts.append(f"**Subtotal: ₹{bill_breakdown['accommodation']['subtotal']}**\n")
        
        # Sightseeing section
        if bill_breakdown["sightseeing"]["subtotal"] > 0:
            message_parts.append("## 🎫 **Sightseeing**")
            for item in bill_breakdown["sightseeing"]["items"]:
                message_parts.append(f"- {item['description']}")
                message_parts.append(f"  - Date: {item['date']}")
                message_parts.append(f"  - Booking ID: `{item['booking_id']}`")
                message_parts.append(f"  - **Amount: ₹{item['amount']}**")
            message_parts.append(f"**Subtotal: ₹{bill_breakdown['sightseeing']['subtotal']}**\n")
        
        # Total
        message_parts.append("---")
        message_parts.append(f"## 💳 **TOTAL AMOUNT: ₹{total_amount}**")
        
        logger.info(f"✅ Bill calculated: ₹{total_amount}")
        
        return {
            "action": "calculate_bill",
            "status": "success",
            "message": "\n".join(message_parts),
            "total_amount": total_amount,
            "breakdown": bill_breakdown
        }
        
    except Exception as e:
        logger.error(f"❌ Bill calculation failed: {str(e)}", exc_info=True)
        return {
            "action": "calculate_bill",
            "status": "error",
            "message": f"Failed to calculate bill: {str(e)}",
            "total_amount": 0,
            "breakdown": {}
        }


def get_bill_breakdown(tool_context: ToolContext) -> dict:
    """
    Get detailed breakdown of all costs
    Same as calculate_total_bill but with more detailed view
    """
    return calculate_total_bill(tool_context)


def estimate_trip_cost(tool_context: ToolContext) -> dict:
    """
    Estimate trip cost based on current bookings
    Quick summary without full bill formatting
    """
    try:
        trip_plan = tool_context.state.get("trip_plan", {})
        
        if not trip_plan:
            return {
                "action": "estimate_cost",
                "status": "no_bookings",
                "message": "No bookings found. Total cost: ₹0",
                "estimated_cost": 0
            }
        
        total = 0
        components = []
        
        # Travel cost
        travel = trip_plan.get('travel')
        if travel and travel.get('price', 0) > 0:
            travel_cost = travel['price']
            total += travel_cost
            components.append(f"Travel: ₹{travel_cost}")
        
        # Accommodation cost
        accommodation = trip_plan.get('accommodation')
        if accommodation and accommodation.get('total_price', 0) > 0:
            accom_cost = accommodation['total_price']
            total += accom_cost
            components.append(f"Accommodation: ₹{accom_cost}")
        
        # Sightseeing cost
        sightseeing = trip_plan.get('sightseeing')
        if sightseeing and sightseeing.get('budget', 0) > 0:
            sight_cost = sightseeing['budget']
            total += sight_cost
            components.append(f"Sightseeing: ₹{sight_cost}")
        
        if components:
            breakdown = " + ".join(components)
            message = f"💰 **Estimated Trip Cost**\n\n{breakdown}\n\n**Total: ₹{total}**"
        else:
            message = "No costs to estimate yet. Prices will be added after bookings are confirmed."
        
        logger.info(f"📊 Estimated cost: ₹{total}")
        
        return {
            "action": "estimate_cost",
            "status": "success",
            "message": message,
            "estimated_cost": total,
            "breakdown": components
        }
        
    except Exception as e:
        logger.error(f"❌ Cost estimation failed: {str(e)}", exc_info=True)
        return {
            "action": "estimate_cost",
            "status": "error",
            "message": "Failed to estimate trip cost",
            "estimated_cost": 0
        }


# ✅ ALIAS FOR BACKWARD COMPATIBILITY
def calculate_trip_bill(tool_context: ToolContext) -> dict:
    """Alias for calculate_total_bill - for backward compatibility"""
    return calculate_total_bill(tool_context)


def get_trip_total(tool_context: ToolContext) -> dict:
    """Quick function to get just the total amount"""
    try:
        trip_plan = tool_context.state.get("trip_plan", {})
        
        total = 0
        
        # Add travel cost
        travel = trip_plan.get('travel')
        if travel:
            total += travel.get('price', 0)
        
        # Add accommodation cost
        accommodation = trip_plan.get('accommodation')
        if accommodation:
            total += accommodation.get('total_price', 0)
        
        # Add sightseeing cost
        sightseeing = trip_plan.get('sightseeing')
        if sightseeing:
            total += sightseeing.get('budget', 0)
        
        logger.info(f"💵 Total calculated: ₹{total}")
        
        return {
            "action": "get_total",
            "status": "success",
            "message": f"**Total trip cost: ₹{total}**",
            "total_amount": total
        }
        
    except Exception as e:
        logger.error(f"❌ Get total failed: {str(e)}", exc_info=True)
        return {
            "action": "get_total",
            "status": "error",
            "message": "Failed to calculate total",
            "total_amount": 0
        }