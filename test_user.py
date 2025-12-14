import sqlite3
import json

def find_test_user():
    """Search ALL sessions for Test User"""
    
    db_path = "sessions.db"
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("\n" + "="*80)
        print("🔍 SEARCHING ALL SESSIONS FOR TEST USER")
        print("="*80)
        
        # Get ALL sessions ordered by most recent
        cursor.execute("""
            SELECT * FROM sessions 
            ORDER BY updated DESC
        """)
        sessions = cursor.fetchall()
        
        print(f"\n📊 Total sessions to search: {len(sessions)}")
        print("\n🔍 Searching for 'Test User' or 'test@gmail.com'...\n")
        
        found_sessions = []
        
        for idx, session in enumerate(sessions, 1):
            if session['state']:
                try:
                    state = json.loads(session['state'])
                    
                    # Safe retrieval with None handling
                    user_name = state.get('user_name') or ''
                    user_email = state.get('user_email') or ''
                    
                    user_name = str(user_name).lower()
                    user_email = str(user_email).lower()
                    
                    # Check if this is Test User
                    if 'test user' in user_name or 'test@gmail.com' in user_email:
                        found_sessions.append({
                            'position': idx,
                            'session': session,
                            'state': state
                        })
                        
                except (json.JSONDecodeError, AttributeError) as e:
                    pass
        
        if found_sessions:
            print(f"✅ FOUND {len(found_sessions)} SESSION(S) FOR TEST USER!\n")
            
            for item in found_sessions:
                idx = item['position']
                session = item['session']
                state = item['state']
                
                print("="*80)
                print(f"FOUND AT POSITION #{idx}")
                print("="*80)
                print(f"Session ID: {session['id']}")
                print(f"App Name: {session['app_name']}")
                print(f"User ID: {session['user_id']}")
                print(f"Created: {session['created']}")
                print(f"Updated: {session['updated']}")
                
                # User info
                print(f"\n👤 USER IDENTIFICATION:")
                print(f"   user_id: {state.get('user_id') or '❌ NOT SET'}")
                print(f"   user_name: {state.get('user_name') or '❌ NOT SET'}")
                print(f"   user_email: {state.get('user_email') or '❌ NOT SET'}")
                
                # Trip plan
                trip_plan = state.get('trip_plan')
                if trip_plan:
                    print(f"\n🎫 TRIP PLAN:")
                    
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
                    
                    accommodation = trip_plan.get('accommodation')
                    if accommodation:
                        print(f"\n   ✅ ACCOMMODATION BOOKING:")
                        print(f"      Hotel: {accommodation.get('hotel_name', 'N/A')}")
                        print(f"      Location: {accommodation.get('location', 'N/A')}")
                        print(f"      Check-in: {accommodation.get('check_in', 'N/A')}")
                        print(f"      Check-out: {accommodation.get('check_out', 'N/A')}")
                        print(f"      Budget/night: ₹{accommodation.get('budget_per_night', 'N/A')}")
                        print(f"      Total: ₹{accommodation.get('total_cost', 'N/A')}")
                else:
                    print(f"\n⚠️  No trip plan found")
                
                # Show all state keys
                print(f"\n📦 All state keys: {', '.join(state.keys())}")
                
                # Full state
                print(f"\n📄 FULL STATE:")
                print(json.dumps(state, indent=2))
                print()
        
        else:
            print("❌ NO SESSIONS FOUND FOR TEST USER!")
            print("\n💡 This means one of the following:")
            print("   1. The identify_user tool was not called during your conversation")
            print("   2. The tool didn't save user_name/user_email to state")
            print("   3. You used a different session_id than expected")
            print("\n🔍 Let's check what the most recent session contains:")
            
            # Show the most recent session in detail
            cursor.execute("SELECT * FROM sessions ORDER BY updated DESC LIMIT 1")
            latest = cursor.fetchone()
            
            if latest:
                print("\n" + "="*80)
                print("MOST RECENT SESSION")
                print("="*80)
                print(f"Session ID: {latest['id']}")
                print(f"App Name: {latest['app_name']}")
                print(f"User ID: {latest['user_id']}")
                print(f"Created: {latest['created']}")
                print(f"Updated: {latest['updated']}")
                
                if latest['state']:
                    try:
                        state = json.loads(latest['state'])
                        print("\n📋 STATE CONTENTS:")
                        print(json.dumps(state, indent=2))
                        
                        # Check if it has trip_plan but no user info
                        if state.get('trip_plan') and not state.get('user_name'):
                            print("\n⚠️  ISSUE FOUND:")
                            print("   This session has trip bookings but NO user identification!")
                            print("   The identify_user tool was not called or failed.")
                        
                    except:
                        print(f"\nRaw state: {latest['state'][:500]}")
        
        print("\n" + "="*80)
        print("💡 NEXT STEPS:")
        print("="*80)
        
        if not found_sessions:
            print("\n1. Run 'adk web' and start a NEW conversation")
            print("2. First message: 'Hi my email is test@gmail.com'")
            print("3. Second message: 'My name is Test User'")
            print("4. Then make a trip booking")
            print("5. Run this script again to verify")
        else:
            print("\n✅ Test User found! Phase 1 Milestone 1.1 is working!")
        
        print("="*80)
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_test_user()