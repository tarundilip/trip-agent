from typing import Optional, Dict
from loguru import logger
from .db import db_manager
from .models import User, Session

class SessionManager:
    """Manages user sessions and state persistence"""
    
    def __init__(self):
        self.db = db_manager

    async def create_user_session(
        self,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        session_name: Optional[str] = None
    ) -> Dict:
        """
        Create a new user and session
        
        Args:
            name: User's name
            email: User's email (optional)
            phone: User's phone (optional)
            session_name: Name for the session (optional)
            
        Returns:
            dict: Contains user_id and session_id
        """
        try:
            # Create user
            user = await self.db.create_user(name=name, email=email, phone=phone)
            
            # Create session for user
            session = await self.db.create_session(
                user_id=user.user_id,
                session_name=session_name
            )
            
            logger.info(f"Created session for user {user.user_id}")
            
            return {
                "user_id": user.user_id,
                "session_id": session.session_id,
                "user_name": user.name,
                "session_name": session_name
            }
            
        except Exception as e:
            logger.error(f"Failed to create user session: {str(e)}")
            raise

    async def get_or_create_user(
        self,
        email: Optional[str] = None,
        name: Optional[str] = None
    ) -> User:
        """
        Get existing user or create new one
        
        Args:
            email: User's email
            name: User's name
            
        Returns:
            User: User object
        """
        if email:
            user = await self.db.get_user_by_email(email)
            if user:
                await self.db.update_user_login(user.user_id)
                return user
        
        if not name:
            raise ValueError("Name is required for new users")
        
        return await self.db.create_user(name=name, email=email)

    async def get_session(self, session_id: str) -> Optional[Session]:
        """Retrieve session by ID"""
        return await self.db.get_session(session_id)

    async def list_user_sessions(self, user_id: str) -> list:
        """List all sessions for a user"""
        return await self.db.list_user_sessions(user_id)

    async def update_session_state(self, session_id: str, state: Dict) -> None:
        """Update session state"""
        await self.db.update_session_state(session_id, state)

    async def create_session(self, user_id: str, session_name: Optional[str] = None) -> Session:
        """Create a new session for existing user"""
        return await self.db.create_session(user_id, session_name)

# Global session manager instance
session_manager = SessionManager()