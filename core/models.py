from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class User:
    """User model representing trip planner users"""
    user_id: str
    name: str
    email: Optional[str]
    created_at: datetime

@dataclass
class Session:
    """Session model for maintaining user state"""
    session_id: str
    user_id: str
    created_at: datetime
    last_active: datetime
    state: Dict[str, Any]

@dataclass
class Booking:
    """Booking model for all types of reservations"""
    booking_id: str
    user_id: str
    session_id: str
    booking_type: str  # 'accommodation', 'travel', 'sightseeing'
    details: Dict[str, Any]
    created_at: datetime
    status: str