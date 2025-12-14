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
        
        cursor.execute("SELECT * FROM sessions ORDER BY updated DESC")
        sessions = cursor.fetchall()
        
        print(f"\n📊 Total sessions to search: {len(sessions)}")
        print("\n🔍 Searching for 'Test User 2' or 'testuser2@gmail.com'...\n")
        
        found_sessions = []
        
        for idx, session in enumerate(sessions, 1):
            if session['state']:
                try:
                    state = json.loads(session['state'])
                    
                    user_name = state.get('user_name') or ''
                    user_email = state.get('user_email') or ''
                    
                    user_name = str(user_name).lower()
                    user_email = str(user_email).lower()
                    
                    if 'Test User 2' in user_name or 'testuser2@gmail.com' in user_email:
                        found_sessions.append({
                            'position': idx,
                            'session': session,
                            'state': state
                        })
                        
                except (json.JSONDecodeError, AttributeError):
                    pass
        
        if found_sessions:
            print(f"✅ FOUND {len(found_sessions)} SESSION(S) FOR TEST USER 2!\n")
            
            for item in found_sessions:
                idx = item['position']
                session = item['session']
                state = item['state']
                
                print("="*80)
                print(f"FOUND AT POSITION #{idx}")
                print("="*80)
                print(f"Session ID: {session['id']}")
                print(f"Updated: {session['updated']}")
                
                print(f"\n👤 USER IDENTIFICATION:")
                print(f"   user_id: {state.get('user_id') or '❌ NOT SET'}")
                print(f"   user_name: {state.get('user_name') or '❌ NOT SET'}")
                print(f"   user_email: {state.get('user_email') or '❌ NOT SET'}")
                
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
                        print(f"      Price: ₹{travel.get('price', 'N/A')}")
                        print(f"      Ticket ID: {travel.get('ticket_id', 'N/A')}")
                    
                    accommodation = trip_plan.get('accommodation')
                    if accommodation:
                        print(f"\n   ✅ ACCOMMODATION BOOKING:")
                        print(f"      Hotel: {accommodation.get('hotel_name', 'N/A')}")
                        print(f"      Location: {accommodation.get('location', 'N/A')}")
                        print(f"      Check-in: {accommodation.get('check_in', 'N/A')}")
                        print(f"      Check-out: {accommodation.get('check_out', 'N/A')}")
                
                print(f"\n📄 FULL STATE:")
                print(json.dumps(state, indent=2))
                print()
        
        else:
            print("❌ NO SESSIONS FOUND FOR TEST USER!")
            print("\n💡 Next steps:")
            print("   1. Run 'python main.py' to create test session")
            print("   2. Or use 'adk web' and send test messages")
            print("   3. Run this script again")
        
        print("\n" + "="*80)
        if found_sessions:
            print("✅ Phase 1 Milestone 1.1: USER IDENTIFICATION - COMPLETE")
        print("="*80)
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_test_user()