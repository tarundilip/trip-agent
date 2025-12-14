import sqlite3
import json

def check_test_user():
    """Check session data for Test User"""
    
    db_path = "sessions.db"
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("\n" + "="*80)
        print("📊 CHECKING TEST USER SESSION DATA")
        print("="*80)
        
        # Check if sessions table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'")
        if not cursor.fetchone():
            print("\n❌ 'sessions' table not found in sessions.db")
            conn.close()
            return
        
        # Get table structure
        cursor.execute("PRAGMA table_info(sessions)")
        columns = cursor.fetchall()
        print("\n📋 Table Structure:")
        for col in columns:
            print(f"   - {col['name']} ({col['type']})")
        
        # Get total count
        cursor.execute("SELECT COUNT(*) as count FROM sessions")
        total_count = cursor.fetchone()['count']
        print(f"\n📊 Total sessions in database: {total_count}")
        
        # Get the most recent 5 sessions (using 'updated' instead of 'last_active')
        cursor.execute("""
            SELECT * FROM sessions 
            ORDER BY updated DESC 
            LIMIT 5
        """)
        sessions = cursor.fetchall()
        
        print(f"\n📊 Showing {len(sessions)} most recent sessions:\n")
        
        test_user_found = False
        
        for idx, session in enumerate(sessions, 1):
            print("="*80)
            print(f"SESSION #{idx}")
            print("="*80)
            
            # Show basic info
            for key in session.keys():
                if key != 'state':  # Skip state for now
                    print(f"{key}: {session[key]}")
            
            # Parse state
            if session['state']:
                try:
                    state = json.loads(session['state'])
                    
                    print("\n📋 STATE CONTENTS:")
                    
                    # Check for user identification
                    user_id = state.get('user_id')
                    user_name = state.get('user_name')
                    user_email = state.get('user_email')
                    
                    if user_name or user_email:
                        print(f"\n👤 USER IDENTIFICATION:")
                        print(f"   user_id: {user_id or '❌ NOT SET'}")
                        print(f"   user_name: {user_name or '❌ NOT SET'}")
                        print(f"   user_email: {user_email or '❌ NOT SET'}")
                        
                        if user_name == "Test User" and user_email == "test@gmail.com":
                            print("\n   ✅ TEST USER FOUND!")
                            test_user_found = True
                    
                    # Check for trip plan
                    trip_plan = state.get('trip_plan')
                    if trip_plan:
                        print(f"\n🎫 TRIP PLAN:")
                        
                        # Travel booking
                        travel = trip_plan.get('travel')
                        if travel:
                            print(f"\n   ✅ TRAVEL BOOKING:")
                            print(f"      From: {travel.get('from', 'N/A')}")
                            print(f"      To: {travel.get('to', 'N/A')}")
                            print(f"      Mode: {travel.get('mode', 'N/A')}")
                            print(f"      Transport: {travel.get('transport_name', 'N/A')}")
                            print(f"      Date: {travel.get('date', 'N/A')}")
                            print(f"      Budget: ₹{travel.get('budget') or travel.get('price', 'N/A')}")
                            print(f"      Ticket ID: {travel.get('ticket_id', 'N/A')}")
                        
                        # Accommodation booking
                        accommodation = trip_plan.get('accommodation')
                        if accommodation:
                            print(f"\n   ✅ ACCOMMODATION BOOKING:")
                            print(f"      Hotel: {accommodation.get('hotel_name', 'N/A')}")
                            print(f"      Location: {accommodation.get('location', 'N/A')}")
                            print(f"      Check-in: {accommodation.get('check_in', 'N/A')}")
                            print(f"      Check-out: {accommodation.get('check_out', 'N/A')}")
                            print(f"      Budget/night: ₹{accommodation.get('budget_per_night', 'N/A')}")
                            print(f"      Total: ₹{accommodation.get('total_cost', 'N/A')}")
                    
                    # Show all state keys
                    print(f"\n📦 All state keys: {', '.join(state.keys())}")
                    
                    # If this is Test User, show full state
                    if user_name == "Test User":
                        print(f"\n📄 FULL STATE (JSON):")
                        print(json.dumps(state, indent=2))
                    
                except json.JSONDecodeError as e:
                    print(f"\n❌ Error parsing state: {e}")
                    print(f"Raw state (first 200 chars): {session['state'][:200]}")
            else:
                print("\n⚠️  State is empty")
            
            print()
        
        # Summary
        print("="*80)
        if test_user_found:
            print("✅ TEST USER SESSION FOUND WITH COMPLETE DATA!")
            print("✅ Phase 1 Milestone 1.1: USER IDENTIFICATION - COMPLETE")
        else:
            print("⚠️  Test User not found in recent sessions")
            print("💡 The session might be older, or user identification didn't work")
        print("="*80)
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"\n❌ Database error: {e}")
        import traceback
        traceback.print_exc()
    except FileNotFoundError:
        print(f"\n❌ Database file not found: {db_path}")
        print("💡 Make sure you're in the project root directory")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_test_user()