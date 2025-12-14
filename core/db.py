from datetime import datetime, UTC
import sqlite3
import json
import uuid
import os
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from loguru import logger
from .models import User, Session, Booking

class DatabaseManager:
    """Manages database operations for trip planner with multi-user support"""
    
    def __init__(self, db_path: str = "temp_backup/trip_planner.db"):
        """Initialize database connection and tables"""
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    @contextmanager
    def _get_connection(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self):
        """Initialize database tables with enhanced schema for multi-user support"""
        with self._get_connection() as conn:
            conn.executescript("""
                -- Users table with unique identification
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    phone TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    metadata JSON
                );

                -- Sessions table linked to users
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    state JSON,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                );

                -- Bookings table with user and session tracking
                CREATE TABLE IF NOT EXISTS bookings (
                    booking_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    booking_type TEXT NOT NULL CHECK(booking_type IN ('accommodation', 'travel', 'sightseeing')),
                    details JSON NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'confirmed' CHECK(status IN ('pending', 'confirmed', 'cancelled', 'completed')),
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
                );

                -- Create indexes for performance
                CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
                CREATE INDEX IF NOT EXISTS idx_sessions_active ON sessions(is_active);
                CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings(user_id);
                CREATE INDEX IF NOT EXISTS idx_bookings_session_id ON bookings(session_id);
                CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);
                
                -- Create view for active sessions with user details
                CREATE VIEW IF NOT EXISTS active_user_sessions AS
                SELECT 
                    s.session_id,
                    s.user_id,
                    u.name as user_name,
                    u.email as user_email,
                    s.session_name,
                    s.created_at,
                    s.last_active,
                    s.state
                FROM sessions s
                JOIN users u ON s.user_id = u.user_id
                WHERE s.is_active = 1 AND u.is_active = 1;
            """)
            logger.info("Database initialized with enhanced multi-user schema")

    # User Management Methods
    async def create_user(self, name: str, email: Optional[str] = None, phone: Optional[str] = None, metadata: Optional[Dict] = None) -> User:
        """Create a new user in the database"""
        user_id = str(uuid.uuid4())
        now = datetime.now(UTC)
        
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """INSERT INTO users (user_id, name, email, phone, created_at, last_login, metadata)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (user_id, name, email, phone, now.isoformat(), now.isoformat(), 
                     json.dumps(metadata or {}))
                )
            
            logger.info(f"Created user: {user_id} - {name}")
            return User(user_id=user_id, name=name, email=email, created_at=now)
        except sqlite3.IntegrityError as e:
            logger.error(f"User creation failed - duplicate email: {email}")
            raise ValueError(f"User with email {email} already exists")
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            raise

    async def get_user(self, user_id: str) -> Optional[User]:
        """Retrieve user by ID"""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM users WHERE user_id = ? AND is_active = 1",
                    (user_id,)
                )
                row = cursor.fetchone()
                
                if not row:
                    return None
                    
                return User(
                    user_id=row['user_id'],
                    name=row['name'],
                    email=row['email'],
                    created_at=datetime.fromisoformat(row['created_at'])
                )
        except Exception as e:
            logger.error(f"Failed to get user: {str(e)}")
            raise

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve user by email"""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM users WHERE email = ? AND is_active = 1",
                    (email,)
                )
                row = cursor.fetchone()
                
                if not row:
                    return None
                    
                return User(
                    user_id=row['user_id'],
                    name=row['name'],
                    email=row['email'],
                    created_at=datetime.fromisoformat(row['created_at'])
                )
        except Exception as e:
            logger.error(f"Failed to get user by email: {str(e)}")
            raise

    async def list_users(self) -> List[User]:
        """List all active users"""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM users WHERE is_active = 1 ORDER BY created_at DESC"
                )
                return [
                    User(
                        user_id=row['user_id'],
                        name=row['name'],
                        email=row['email'],
                        created_at=datetime.fromisoformat(row['created_at'])
                    )
                    for row in cursor.fetchall()
                ]
        except Exception as e:
            logger.error(f"Failed to list users: {str(e)}")
            raise

    async def update_user_login(self, user_id: str) -> None:
        """Update user's last login timestamp"""
        try:
            now = datetime.now(UTC)
            with self._get_connection() as conn:
                conn.execute(
                    "UPDATE users SET last_login = ? WHERE user_id = ?",
                    (now.isoformat(), user_id)
                )
        except Exception as e:
            logger.error(f"Failed to update user login: {str(e)}")
            raise

    # Session Management Methods
    async def create_session(self, user_id: str, session_name: Optional[str] = None, initial_state: Dict = None) -> Session:
        """Create a new session for a user"""
        session_id = str(uuid.uuid4())
        now = datetime.now(UTC)
        
        # Verify user exists
        user = await self.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        if not session_name:
            session_name = f"Session {now.strftime('%Y-%m-%d %H:%M')}"
        
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """INSERT INTO sessions (session_id, user_id, session_name, created_at, last_active, state, is_active)
                       VALUES (?, ?, ?, ?, ?, ?, 1)""",
                    (session_id, user_id, session_name, now.isoformat(), now.isoformat(), 
                     json.dumps(initial_state or {}))
                )
            
            logger.info(f"Created session: {session_id} for user: {user_id}")
            return Session(
                session_id=session_id,
                user_id=user_id,
                created_at=now,
                last_active=now,
                state=initial_state or {}
            )
        except Exception as e:
            logger.error(f"Failed to create session: {str(e)}")
            raise

    async def get_session(self, session_id: str) -> Optional[Session]:
        """Retrieve session by ID"""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM sessions WHERE session_id = ? AND is_active = 1",
                    (session_id,)
                )
                row = cursor.fetchone()
                
                if not row:
                    logger.warning(f"Session not found: {session_id}")
                    return None
                    
                return Session(
                    session_id=row['session_id'],
                    user_id=row['user_id'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    last_active=datetime.fromisoformat(row['last_active']),
                    state=json.loads(row['state'])
                )
        except Exception as e:
            logger.error(f"Failed to get session: {str(e)}")
            raise

    async def list_user_sessions(self, user_id: str, active_only: bool = True) -> List[Dict]:
        """List all sessions for a user"""
        try:
            with self._get_connection() as conn:
                query = """
                    SELECT session_id, session_name, created_at, last_active, is_active
                    FROM sessions
                    WHERE user_id = ?
                """
                params = [user_id]
                
                if active_only:
                    query += " AND is_active = 1"
                
                query += " ORDER BY last_active DESC"
                
                cursor = conn.execute(query, params)
                return [
                    {
                        'session_id': row['session_id'],
                        'session_name': row['session_name'],
                        'created_at': row['created_at'],
                        'last_active': row['last_active'],
                        'is_active': bool(row['is_active'])
                    }
                    for row in cursor.fetchall()
                ]
        except Exception as e:
            logger.error(f"Failed to list user sessions: {str(e)}")
            raise

    async def update_session(self, session: Session) -> None:
        """Update session state and last active time"""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """UPDATE sessions 
                       SET last_active = ?, state = ?
                       WHERE session_id = ? AND is_active = 1""",
                    (session.last_active.isoformat(), 
                     json.dumps(session.state), 
                     session.session_id)
                )
            logger.debug(f"Updated session: {session.session_id}")
        except Exception as e:
            logger.error(f"Failed to update session: {str(e)}")
            raise

    async def update_session_state(self, session_id: str, state: Dict) -> None:
        """Update session state"""
        try:
            now = datetime.now(UTC)
            with self._get_connection() as conn:
                conn.execute(
                    """UPDATE sessions 
                       SET last_active = ?, state = ?
                       WHERE session_id = ? AND is_active = 1""",
                    (now.isoformat(), json.dumps(state), session_id)
                )
            logger.debug(f"Updated session state: {session_id}")
        except Exception as e:
            logger.error(f"Failed to update session state: {str(e)}")
            raise

    async def delete_session(self, session_id: str) -> bool:
        """Soft delete a session"""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "UPDATE sessions SET is_active = 0 WHERE session_id = ?",
                    (session_id,)
                )
                deleted = cursor.rowcount > 0
                if deleted:
                    logger.info(f"Deleted session: {session_id}")
                return deleted
        except Exception as e:
            logger.error(f"Failed to delete session: {str(e)}")
            raise

    # Booking Management Methods
    async def save_booking(self, booking: Booking) -> Booking:
        """Save a new booking"""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """INSERT INTO bookings (
                        booking_id, user_id, session_id, booking_type,
                        details, created_at, updated_at, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        booking.booking_id,
                        booking.user_id,
                        booking.session_id,
                        booking.booking_type,
                        json.dumps(booking.details),
                        booking.created_at.isoformat(),
                        booking.created_at.isoformat(),
                        booking.status
                    )
                )
            logger.info(f"Saved booking: {booking.booking_id}")
            return booking
        except Exception as e:
            logger.error(f"Failed to save booking: {str(e)}")
            raise

    async def get_session_bookings(self, session_id: str) -> List[Booking]:
        """Get all bookings for a session"""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM bookings WHERE session_id = ? ORDER BY created_at DESC",
                    (session_id,)
                )
                return [
                    Booking(
                        booking_id=row['booking_id'],
                        user_id=row['user_id'],
                        session_id=row['session_id'],
                        booking_type=row['booking_type'],
                        details=json.loads(row['details']),
                        created_at=datetime.fromisoformat(row['created_at']),
                        status=row['status']
                    )
                    for row in cursor.fetchall()
                ]
        except Exception as e:
            logger.error(f"Failed to get bookings: {str(e)}")
            raise

    async def get_user_bookings(self, user_id: str) -> List[Booking]:
        """Get all bookings for a user across all sessions"""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM bookings WHERE user_id = ? ORDER BY created_at DESC",
                    (user_id,)
                )
                return [
                    Booking(
                        booking_id=row['booking_id'],
                        user_id=row['user_id'],
                        session_id=row['session_id'],
                        booking_type=row['booking_type'],
                        details=json.loads(row['details']),
                        created_at=datetime.fromisoformat(row['created_at']),
                        status=row['status']
                    )
                    for row in cursor.fetchall()
                ]
        except Exception as e:
            logger.error(f"Failed to get user bookings: {str(e)}")
            raise

    async def update_booking_status(self, booking_id: str, status: str) -> None:
        """Update booking status"""
        try:
            now = datetime.now(UTC)
            with self._get_connection() as conn:
                conn.execute(
                    """UPDATE bookings 
                       SET status = ?, updated_at = ?
                       WHERE booking_id = ?""",
                    (status, now.isoformat(), booking_id)
                )
            logger.info(f"Updated booking {booking_id} status to {status}")
        except Exception as e:
            logger.error(f"Failed to update booking status: {str(e)}")
            raise

        async def get_booking_by_id(self, booking_id: str) -> Optional[Booking]:
            """Get a single booking by ID"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM bookings WHERE booking_id = ?
                """, (booking_id,))
                
                row = cursor.fetchone()
                
                if row:
                    return Booking(
                        booking_id=row['booking_id'],
                        user_id=row['user_id'],
                        session_id=row['session_id'],
                        booking_type=row['booking_type'],
                        details=json.loads(row['details']) if row['details'] else {},
                        created_at=datetime.fromisoformat(row['created_at']),
                        status=row['status']
                    )
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get booking: {str(e)}")
            raise

    async def get_session_bill(self, session_id: str) -> int:
        """Calculate total bill for a session from bookings"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT SUM(
                        CASE 
                            WHEN booking_type = 'travel' THEN CAST(json_extract(details, '$.price') AS INTEGER)
                            WHEN booking_type = 'accommodation' THEN CAST(json_extract(details, '$.total_price') AS INTEGER)
                            WHEN booking_type = 'sightseeing' THEN CAST(json_extract(details, '$.entry_fee') AS INTEGER)
                            ELSE 0
                        END
                    ) as total
                    FROM bookings
                    WHERE session_id = ? AND status = 'confirmed'
                """, (session_id,))
                
                result = cursor.fetchone()
                return result['total'] if result['total'] else 0
                
        except Exception as e:
            logger.error(f"Failed to calculate session bill: {str(e)}")
            return 0

db_manager = DatabaseManager()