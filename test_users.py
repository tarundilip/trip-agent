import sqlite3
import json
from datetime import datetime
from tabulate import tabulate

def check_database():
    """Check all user-related data in the database"""
    
    db_path = "temp_backup/trip_planner.db"
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("\n" + "="*80)
        print("📊 TRIP PLANNER DATABASE - USER DATA")
        print("="*80)
        
        # Check if users table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='users'
        """)
        
        if not cursor.fetchone():
            print("\n❌ Users table does not exist yet!")
            print("💡 Run the application first to create the database schema.")
            return
        
        # 1. Check Users
        print("\n" + "-"*80)
        print("👥 USERS TABLE")
        print("-"*80)
        
        cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        
        if users:
            user_data = []
            for user in users:
                user_data.append([
                    user['user_id'][:8] + "...",
                    user['name'],
                    user['email'] or "N/A",
                    user['phone'] or "N/A",
                    user['created_at'],
                    user['last_login'] or "Never",
                    "✓" if user['is_active'] else "✗"
                ])
            
            print(tabulate(
                user_data,
                headers=['User ID', 'Name', 'Email', 'Phone', 'Created', 'Last Login', 'Active'],
                tablefmt='grid'
            ))
            print(f"\n📈 Total Users: {len(users)}")
        else:
            print("No users found.")
        
        # 2. Check Sessions
        print("\n" + "-"*80)
        print("📅 SESSIONS TABLE")
        print("-"*80)
        
        cursor.execute("""
            SELECT s.*, u.name as user_name, u.email as user_email
            FROM sessions s
            LEFT JOIN users u ON s.user_id = u.user_id
            ORDER BY s.last_active DESC
        """)
        sessions = cursor.fetchall()
        
        if sessions:
            session_data = []
            for session in sessions:
                session_data.append([
                    session['session_id'][:8] + "...",
                    session['user_name'] or "Unknown",
                    session['session_name'] or "Unnamed",
                    session['created_at'],
                    session['last_active'],
                    "✓" if session['is_active'] else "✗"
                ])
            
            print(tabulate(
                session_data,
                headers=['Session ID', 'User', 'Session Name', 'Created', 'Last Active', 'Active'],
                tablefmt='grid'
            ))
            print(f"\n📈 Total Sessions: {len(sessions)}")
        else:
            print("No sessions found.")
        
        # 3. Check Bookings
        print("\n" + "-"*80)
        print("🎫 BOOKINGS TABLE")
        print("-"*80)
        
        cursor.execute("""
            SELECT b.*, u.name as user_name, s.session_name
            FROM bookings b
            LEFT JOIN users u ON b.user_id = u.user_id
            LEFT JOIN sessions s ON b.session_id = s.session_id
            ORDER BY b.created_at DESC
        """)
        bookings = cursor.fetchall()
        
        if bookings:
            booking_data = []
            for booking in bookings:
                booking_data.append([
                    booking['booking_id'][:8] + "...",
                    booking['user_name'] or "Unknown",
                    booking['booking_type'],
                    booking['status'],
                    booking['created_at']
                ])
            
            print(tabulate(
                booking_data,
                headers=['Booking ID', 'User', 'Type', 'Status', 'Created'],
                tablefmt='grid'
            ))
            print(f"\n📈 Total Bookings: {len(bookings)}")
        else:
            print("No bookings found.")
        
        # 4. User-Session Summary
        print("\n" + "-"*80)
        print("📊 USER-SESSION SUMMARY")
        print("-"*80)
        
        cursor.execute("""
            SELECT 
                u.name,
                u.email,
                COUNT(DISTINCT s.session_id) as total_sessions,
                COUNT(DISTINCT CASE WHEN s.is_active = 1 THEN s.session_id END) as active_sessions,
                COUNT(b.booking_id) as total_bookings
            FROM users u
            LEFT JOIN sessions s ON u.user_id = s.user_id
            LEFT JOIN bookings b ON u.user_id = b.user_id
            WHERE u.is_active = 1
            GROUP BY u.user_id
            ORDER BY total_sessions DESC
        """)
        
        summary = cursor.fetchall()
        
        if summary:
            summary_data = []
            for row in summary:
                summary_data.append([
                    row['name'],
                    row['email'] or "N/A",
                    row['total_sessions'],
                    row['active_sessions'],
                    row['total_bookings']
                ])
            
            print(tabulate(
                summary_data,
                headers=['User Name', 'Email', 'Total Sessions', 'Active Sessions', 'Bookings'],
                tablefmt='grid'
            ))
        else:
            print("No user data available.")
        
        # 5. Check specific user by email (if provided)
        print("\n" + "-"*80)
        print("🔍 SEARCH USER BY EMAIL")
        print("-"*80)
        
        search_email = input("\nEnter email to search (or press Enter to skip): ").strip()
        
        if search_email:
            cursor.execute("""
                SELECT u.*, 
                       COUNT(DISTINCT s.session_id) as sessions,
                       COUNT(b.booking_id) as bookings
                FROM users u
                LEFT JOIN sessions s ON u.user_id = s.user_id
                LEFT JOIN bookings b ON u.user_id = b.user_id
                WHERE u.email = ?
                GROUP BY u.user_id
            """, (search_email,))
            
            user_result = cursor.fetchone()
            
            if user_result:
                print(f"\n✅ User Found!")
                print(f"   Name: {user_result['name']}")
                print(f"   Email: {user_result['email']}")
                print(f"   User ID: {user_result['user_id']}")
                print(f"   Created: {user_result['created_at']}")
                print(f"   Last Login: {user_result['last_login'] or 'Never'}")
                print(f"   Sessions: {user_result['sessions']}")
                print(f"   Bookings: {user_result['bookings']}")
                print(f"   Active: {'Yes' if user_result['is_active'] else 'No'}")
                
                # Show user's sessions
                cursor.execute("""
                    SELECT session_id, session_name, created_at, last_active, is_active
                    FROM sessions
                    WHERE user_id = ?
                    ORDER BY last_active DESC
                """, (user_result['user_id'],))
                
                user_sessions = cursor.fetchall()
                
                if user_sessions:
                    print(f"\n   📅 User's Sessions:")
                    for idx, sess in enumerate(user_sessions, 1):
                        print(f"   {idx}. {sess['session_name']} (ID: {sess['session_id'][:8]}...)")
                        print(f"      Created: {sess['created_at']}")
                        print(f"      Last Active: {sess['last_active']}")
                        print(f"      Status: {'Active' if sess['is_active'] else 'Inactive'}")
            else:
                print(f"\n❌ No user found with email: {search_email}")
        
        print("\n" + "="*80)
        
    except sqlite3.OperationalError as e:
        print(f"\n❌ Database Error: {e}")
        print("💡 Make sure the database file exists at: temp_backup/trip_planner.db")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_database()