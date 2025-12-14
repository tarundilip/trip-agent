"""
UI tools for user identification and session management
"""
from typing import Optional
from loguru import logger
from google.adk.tools.tool_context import ToolContext
import uuid

async def identify_user(tool_context: ToolContext, user_input: str) -> str:
    """
    Identify or create user in session state with AUTO-RESUME functionality.
    """
    try:
        user_input = user_input.strip()
        logger.info(f"🔍 identify_user called with: {user_input}")
        
        existing_user_id = tool_context.state.get('user_id')
        if existing_user_id:
            user_name = tool_context.state.get('user_name', 'User')
            user_email = tool_context.state.get('user_email', 'Not provided')
            logger.info(f"✅ User already identified: {user_name}")
            return f"You are already identified as {user_name} (Email: {user_email})."
        
        if '@' in user_input and '.' in user_input:
            email = user_input.lower()
            tool_context.state['pending_user_email'] = email
            logger.info(f"✅ Email captured: {email}")
            
            # ✅ CHECK IF USER EXISTS IN CUSTOM DB
            from core.db import db_manager
            existing_user = await db_manager.get_user_by_email(email)
            
            if existing_user:
                # User exists - load their info
                user_id = existing_user.user_id
                tool_context.state['user_id'] = user_id
                tool_context.state['user_name'] = existing_user.name
                tool_context.state['user_email'] = existing_user.email
                
                logger.info(f"✅ Returning user: {existing_user.name} ({user_id})")
                
                # ✅ LOAD LAST ACTIVE SESSION
                sessions = await db_manager.list_user_sessions(user_id, active_only=True)
                
                if sessions:
                    last_session = sessions[0]  # Most recent
                    db_session = await db_manager.get_session(last_session['session_id'])
                    
                    if db_session and db_session.state:
                        # ✅ RESUME: Load trip plan into current context
                        trip_plan = db_session.state.get('trip_plan', {})
                        
                        # Merge the trip plan into current state
                        if trip_plan:
                            tool_context.state['trip_plan'] = trip_plan
                            
                            summary_parts = []
                            summary_parts.append(f"Welcome back, **{existing_user.name}**! 🎉\n")
                            summary_parts.append(f"I've loaded your last trip session from {last_session['last_active']}\n")
                            
                            # Show travel details
                            if trip_plan.get('travel'):
                                travel = trip_plan['travel']
                                summary_parts.append(f"\n🚆 **Travel Booking:**")
                                summary_parts.append(f"   • From: {travel.get('from')}")
                                summary_parts.append(f"   • To: {travel.get('to')}")
                                summary_parts.append(f"   • Date: {travel.get('date')}")
                                summary_parts.append(f"   • Mode: {travel.get('mode')}")
                                if travel.get('transport_name'):
                                    summary_parts.append(f"   • Transport: {travel.get('transport_name')}")
                                if travel.get('price'):
                                    summary_parts.append(f"   • Price: ₹{travel.get('price')}")
                                summary_parts.append(f"   • Ticket ID: {travel.get('ticket_id')}")
                            
                            # Show accommodation details
                            if trip_plan.get('accommodation'):
                                accom = trip_plan['accommodation']
                                summary_parts.append(f"\n🏨 **Accommodation Booking:**")
                                summary_parts.append(f"   • Location: {accom.get('location')}")
                                summary_parts.append(f"   • Check-in: {accom.get('check_in')}")
                                summary_parts.append(f"   • Check-out: {accom.get('check_out')}")
                                summary_parts.append(f"   • Nights: {accom.get('nights', 'N/A')}")
                                if accom.get('budget'):
                                    summary_parts.append(f"   • Budget: ₹{accom.get('budget')} per night")
                                if accom.get('total_price'):
                                    summary_parts.append(f"   • Total: ₹{accom.get('total_price')}")
                                if accom.get('booking_id'):
                                    summary_parts.append(f"   • Booking ID: {accom.get('booking_id')}")
                            
                            # Show sightseeing details
                            if trip_plan.get('sightseeing'):
                                sight = trip_plan['sightseeing']
                                summary_parts.append(f"\n🎫 **Sightseeing Plan:**")
                                summary_parts.append(f"   • Place: {sight.get('place')}")
                                summary_parts.append(f"   • Date: {sight.get('date')}")
                                if sight.get('entry_fee'):
                                    summary_parts.append(f"   • Entry Fee: ₹{sight.get('entry_fee')}")
                                if sight.get('booking_id'):
                                    summary_parts.append(f"   • Booking ID: {sight.get('booking_id')}")
                            
                            # ✅ ADD TOTAL COST
                            total_cost = 0
                            if trip_plan.get('travel'):
                                total_cost += trip_plan['travel'].get('price', 0)
                            if trip_plan.get('accommodation'):
                                total_cost += trip_plan['accommodation'].get('total_price', 0)
                            if trip_plan.get('sightseeing'):
                                total_cost += trip_plan['sightseeing'].get('entry_fee', 0)
                            
                            if total_cost > 0:
                                summary_parts.append(f"\n💰 **Total Trip Cost: ₹{total_cost}**")
                            
                            summary_parts.append(f"\n\n💡 Would you like to continue with this trip or start a new one?")
                            
                            logger.info(f"✅ Resumed session with trip plan for {existing_user.name}")
                            return "\n".join(summary_parts)
                        else:
                            return f"Welcome back, {existing_user.name}! You have a session but no bookings yet. Ready to plan your next trip?"
                    else:
                        return f"Welcome back, {existing_user.name}! Ready to start planning your next trip?"
                else:
                    return f"Welcome back, {existing_user.name}! You don't have any active trip plans yet. Where would you like to go?"
            
            # New user - ask for name
            return f"Thanks for providing your email ({email}). What's your full name?"
        
        else:
            # Treat as name
            name = user_input.title()
            email = tool_context.state.get('pending_user_email')
            
            # Check if user exists by email
            from core.db import db_manager
            
            if email:
                existing_user = await db_manager.get_user_by_email(email)
                if existing_user:
                    user_id = existing_user.user_id
                    # Update name if different
                    if existing_user.name != name:
                        logger.info(f"Updating user name from {existing_user.name} to {name}")
                else:
                    # Create new user in custom DB
                    new_user = await db_manager.create_user(name=name, email=email)
                    user_id = new_user.user_id
                    logger.info(f"✅ Created new user: {user_id}")
            else:
                # No email - create user with just name
                user_id = str(uuid.uuid4())
            
            tool_context.state['user_id'] = user_id
            tool_context.state['user_name'] = name
            tool_context.state['user_email'] = email
            
            if 'pending_user_email' in tool_context.state:
                del tool_context.state['pending_user_email']
            
            logger.info(f"✅ User identified: {user_id} | Name: {name} | Email: {email}")
            
            if email:
                return f"Great to meet you, {name}! Your account is set up with email {email}. Ready to plan your trip!"
            else:
                return f"Welcome, {name}! Ready to plan your trip?"
                
    except Exception as e:
        logger.error(f"❌ User identification failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"I encountered an error setting up your account. Please provide your email or name again."


async def list_user_sessions(tool_context: ToolContext) -> str:
    """List sessions for current user"""
    try:
        user_id = tool_context.state.get('user_id')
        
        if not user_id:
            return "I need to identify you first. Please provide your email address."
        
        user_name = tool_context.state.get('user_name', 'User')
        
        # Check if there's a trip plan
        trip_plan = tool_context.state.get('trip_plan', {})
        
        if trip_plan:
            return f"You have an active trip planning session. Would you like to continue or start fresh?"
        else:
            return f"Welcome back, {user_name}! You don't have any active trip plans yet. Where would you like to go?"
        
    except Exception as e:
        logger.error(f"❌ Failed to list sessions: {str(e)}")
        return f"I couldn't retrieve your sessions: {str(e)}"


async def get_current_user_info(tool_context: ToolContext) -> str:
    """Get current user info from session state"""
    try:
        user_id = tool_context.state.get('user_id')
        
        if not user_id:
            return "No user is currently identified. Please provide your email or name."
        
        user_name = tool_context.state.get('user_name', 'Unknown')
        user_email = tool_context.state.get('user_email', 'Not provided')
        
        info = f"Current user: {user_name}"
        if user_email and user_email != 'Not provided':
            info += f"\nEmail: {user_email}"
        info += f"\nUser ID: {user_id}"
        
        return info
        
    except Exception as e:
        logger.error(f"❌ Failed to get user info: {str(e)}")
        return f"Couldn't retrieve user information: {str(e)}"