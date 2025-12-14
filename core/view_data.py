import sqlite3
import json
from datetime import datetime
from typing import Dict, Any
from loguru import logger

def format_db_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """Format database row for display"""
    formatted = dict(row)
    
    # Format JSON fields
    if 'state' in formatted and formatted['state']:
        try:
            formatted['state'] = json.loads(formatted['state'])
        except json.JSONDecodeError:
            formatted['state'] = None
            
    if 'details' in formatted and formatted['details']:
        try:
            formatted['details'] = json.loads(formatted['details'])
        except json.JSONDecodeError:
            formatted['details'] = None
    
    return formatted

def view_db_contents(db_path: str = "temp_backup/trip_planner.db") -> None:
    """Display contents of all tables in the trip planner database"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        print("\n=== Trip Planner Database Contents ===\n")
        
        print("=== Users ===")
        for row in conn.execute("SELECT * FROM users ORDER BY created_at DESC"):
            user = format_db_row(row)
            print(f"\nUser ID: {user['user_id']}")
            print(f"Name: {user['name']}")
            print(f"Email: {user['email']}")
            print(f"Created: {user['created_at']}")
        
        print("\n=== Sessions ===")
        for row in conn.execute("SELECT * FROM sessions ORDER BY last_active DESC"):
            session = format_db_row(row)
            print(f"\nSession ID: {session['session_id']}")
            print(f"User ID: {session['user_id']}")
            print(f"Created: {session['created_at']}")
            print(f"Last Active: {session['last_active']}")
            print(f"State: {json.dumps(session['state'], indent=2)}")
        
        print("\n=== Bookings ===")
        for row in conn.execute("SELECT * FROM bookings ORDER BY created_at DESC"):
            booking = format_db_row(row)
            print(f"\nBooking ID: {booking['booking_id']}")
            print(f"Type: {booking['booking_type']}")
            print(f"User ID: {booking['user_id']}")
            print(f"Session ID: {booking['session_id']}")
            print(f"Created: {booking['created_at']}")
            print(f"Status: {booking['status']}")
            print(f"Details: {json.dumps(booking['details'], indent=2)}")
            
    except sqlite3.Error as e:
        logger.error(f"Database error: {str(e)}")
        print(f"Error accessing database: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"Unexpected error: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    view_db_contents()