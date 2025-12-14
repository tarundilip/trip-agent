"""
Simplified bridge - no ADK imports needed
"""
from typing import Dict, Any, Optional
from loguru import logger
from core.db import db_manager
from core.models import Booking
from datetime import datetime

class ADKDatabaseBridge:
    """Synchronizes ADK sessions with custom database"""
    
    def __init__(self):
        self.db = db_manager
        logger.info("✅ Simplified ADK Database Bridge initialized")
    
    async def sync_user_from_state(self, state: Dict[str, Any]) -> Optional[str]:
        """Extract user info from state and ensure user exists in DB"""
        user_name = state.get('user_name')
        user_email = state.get('user_email')
        adk_user_id = state.get('user_id')
        
        if not (user_name or user_email):
            return None
        
        try:
            if user_email:
                existing_user = await self.db.get_user_by_email(user_email)
                if existing_user:
                    if adk_user_id != existing_user.user_id:
                        state['user_id'] = existing_user.user_id
                    return existing_user.user_id
            
            if user_name:
                new_user = await self.db.create_user(
                    name=user_name,
                    email=user_email
                )
                state['user_id'] = new_user.user_id
                logger.info(f"✅ Created user: {new_user.user_id}")
                return new_user.user_id
            
        except Exception as e:
            logger.error(f"❌ Sync user failed: {e}")
            return None
    
    async def sync_session_from_adk(self, app_name: str, adk_user_id: str, 
                                   session_id: str, state: Dict[str, Any]) -> bool:
        """Sync session to custom DB"""
        try:
            db_user_id = await self.sync_user_from_state(state)
            if not db_user_id:
                return False
            
            existing_session = await self.db.get_session(session_id)
            
            if existing_session:
                existing_session.state = state
                existing_session.last_active = datetime.now()
                await self.db.update_session(existing_session)
            else:
                # Create better session name
                session_name = state.get('session_name')
                if not session_name:
                    trip_plan = state.get('trip_plan', {})
                    if trip_plan.get('travel'):
                        travel = trip_plan['travel']
                        session_name = f"Trip to {travel.get('to', 'destination')} on {travel.get('date', 'date')}"
                    else:
                        session_name = f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                
                await self.db.create_session(
                    user_id=db_user_id,
                    session_name=session_name,
                    initial_state=state
                )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Sync session failed: {e}")
            return False
    
    async def sync_bookings_from_state(self, state: Dict[str, Any], 
                                      session_id: str) -> None:
        """Extract bookings from trip_plan and save to DB"""
        user_id = state.get('user_id')
        if not user_id:
            return
        
        trip_plan = state.get('trip_plan', {})
        
        try:
            # Travel
            travel = trip_plan.get('travel')
            if travel and travel.get('ticket_id'):
                booking_id = travel['ticket_id']
                existing = await self.db.get_booking_by_id(booking_id)
                if not existing:
                    await self.db.save_booking(Booking(
                        booking_id=booking_id,
                        user_id=user_id,
                        session_id=session_id,
                        booking_type='travel',
                        details=travel,
                        created_at=datetime.now(),
                        status='confirmed'
                    ))
                    logger.info(f"✅ Saved travel: {booking_id}")
            
            # Accommodation
            accommodation = trip_plan.get('accommodation')
            if accommodation and accommodation.get('booking_id'):
                booking_id = accommodation['booking_id']
                existing = await self.db.get_booking_by_id(booking_id)
                if not existing:
                    await self.db.save_booking(Booking(
                        booking_id=booking_id,
                        user_id=user_id,
                        session_id=session_id,
                        booking_type='accommodation',
                        details=accommodation,
                        created_at=datetime.now(),
                        status='confirmed'
                    ))
                    logger.info(f"✅ Saved accommodation: {booking_id}")
            
            # Sightseeing
            sightseeing = trip_plan.get('sightseeing')
            if sightseeing and sightseeing.get('booking_id'):
                booking_id = sightseeing['booking_id']
                existing = await self.db.get_booking_by_id(booking_id)
                if not existing:
                    await self.db.save_booking(Booking(
                        booking_id=booking_id,
                        user_id=user_id,
                        session_id=session_id,
                        booking_type='sightseeing',
                        details=sightseeing,
                        created_at=datetime.now(),
                        status='confirmed'
                    ))
                    logger.info(f"✅ Saved sightseeing: {booking_id}")
                    
        except Exception as e:
            logger.error(f"❌ Sync bookings failed: {e}")

# Global instance
adk_db_bridge = ADKDatabaseBridge()