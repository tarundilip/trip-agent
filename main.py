import asyncio
from loguru import logger
from agent import trip_planner_supervisor
from core.session_service import session_manager
from core.db import db_manager
from core.trip_tool_context import TripToolContext

async def display_user_menu():
    """Display main user menu"""
    print("\n" + "="*60)
    print("🌍 TRIP PLANNER AGENT")
    print("="*60)
    print("\n1. New User - Create Account")
    print("2. Existing User - Login")
    print("3. List All Users (Debug)")
    print("4. Exit")
    print("\n" + "="*60)

async def display_session_menu(user_name: str):
    """Display session management menu"""
    print("\n" + "="*60)
    print(f"👤 Welcome, {user_name}!")
    print("="*60)
    print("\n1. Start New Trip Planning Session")
    print("2. Resume Existing Session")
    print("3. View All My Sessions")
    print("4. Logout")
    print("\n" + "="*60)

async def handle_user_login():
    """Handle user login/identification"""
    print("\n📧 Enter your email or name:")
    user_input = input("> ").strip()
    
    if not user_input:
        print("❌ Invalid input. Please try again.")
        return None
    
    # Check if email
    if '@' in user_input:
        user = await db_manager.get_user_by_email(user_input)
        if user:
            logger.info(f"User logged in: {user.user_id}")
            return user
        else:
            print(f"\n❌ No account found with email: {user_input}")
            print("Would you like to create a new account? (yes/no)")
            create = input("> ").strip().lower()
            
            if create in ['yes', 'y']:
                print("\n📝 What's your name?")
                name = input("> ").strip()
                if name:
                    user = await db_manager.create_user(name=name, email=user_input)
                    print(f"\n✅ Account created successfully!")
                    logger.info(f"New user created: {user.user_id}")
                    return user
            return None
    else:
        # Treat as name for new user
        print("\n📧 Enter your email (optional - press Enter to skip):")
        email = input("> ").strip()
        email = email if email else None
        
        # Check if email exists
        if email:
            existing = await db_manager.get_user_by_email(email)
            if existing:
                print(f"\n✅ Found existing account for {existing.name}")
                return existing
        
        user = await db_manager.create_user(name=user_input, email=email)
        print(f"\n✅ Account created successfully!")
        logger.info(f"New user created: {user.user_id}")
        return user

async def display_sessions(user_id: str):
    """Display all sessions for a user"""
    sessions = await db_manager.list_user_sessions(user_id, active_only=True)
    
    if not sessions:
        print("\n📋 You don't have any active sessions.")
        return None
    
    print("\n" + "="*60)
    print("📋 YOUR ACTIVE SESSIONS")
    print("="*60)
    
    for idx, session in enumerate(sessions, 1):
        print(f"\n{idx}. {session['session_name']}")
        print(f"   Session ID: {session['session_id'][:8]}...")
        print(f"   Created: {session['created_at']}")
        print(f"   Last Active: {session['last_active']}")
    
    print("\n" + "="*60)
    return sessions

async def select_session(user_id: str):
    """Allow user to select or create a session"""
    sessions = await display_sessions(user_id)
    
    if not sessions:
        print("\nWould you like to start a new session? (yes/no)")
        choice = input("> ").strip().lower()
        if choice in ['yes', 'y']:
            return await create_session_interactive(user_id)
        return None
    
    print("\nEnter session number to resume, or 'new' for a new session:")
    choice = input("> ").strip().lower()
    
    if choice == 'new':
        return await create_session_interactive(user_id)
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(sessions):
            return sessions[idx]['session_id']
        else:
            print("❌ Invalid session number")
            return None
    except ValueError:
        print("❌ Invalid input")
        return None

async def create_session_interactive(user_id: str):
    """Create a new session interactively"""
    print("\n✨ Creating new trip planning session...")
    print("\nGive your trip a name (optional - press Enter to skip):")
    session_name = input("> ").strip()
    
    if not session_name:
        from datetime import datetime
        session_name = f"Trip {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    session = await db_manager.create_session(user_id, session_name=session_name)
    print(f"\n✅ Session created: {session_name}")
    logger.info(f"New session created: {session.session_id}")
    
    return session.session_id

async def run_conversation(user_id: str, session_id: str):
    """Run the conversation loop with the Google ADK agent"""
    print("\n" + "="*60)
    print("🤖 TRIP PLANNING ASSISTANT")
    print("="*60)
    print("\nType 'exit' to end the session")
    print("Type 'status' to see your current bookings")
    print("Type 'sessions' to switch sessions")
    print("\n" + "="*60 + "\n")
    
    # Initialize context with user_id
    context = TripToolContext(session_id=session_id)
    await context.initialize()
    context.set_state_value('user_id', user_id)
    await context.save_state()
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'exit':
                print("\n👋 Thank you for using Trip Planner! Your session has been saved.")
                break
            
            if user_input.lower() == 'status':
                await display_booking_status(session_id)
                continue
            
            if user_input.lower() == 'sessions':
                print("\n🔄 Returning to session menu...")
                break
            
            # Call Google ADK agent
            print("\nAssistant: ", end="", flush=True)
            
            # Google ADK agent execution
            response = trip_planner_supervisor(user_input, session_id=session_id)
            
            # Display response
            if hasattr(response, 'content'):
                print(response.content)
            elif isinstance(response, dict):
                print(response.get('response', str(response)))
            else:
                print(str(response))
            
            # Save session state after each interaction
            await context.save_state()
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Session interrupted. Your progress has been saved.")
            break
        except Exception as e:
            logger.error(f"Error in conversation: {str(e)}")
            print(f"\n❌ Error: {str(e)}")
            print("Please try again or type 'exit' to quit.\n")

async def display_booking_status(session_id: str):
    """Display current booking status"""
    try:
        bookings = await db_manager.get_session_bookings(session_id)
        
        if not bookings:
            print("\n📋 No bookings found for this session.")
            return
        
        print("\n" + "="*60)
        print("📋 YOUR BOOKINGS")
        print("="*60)
        
        for booking in bookings:
            print(f"\n🎫 {booking.booking_type.upper()}")
            print(f"   ID: {booking.booking_id[:8]}...")
            print(f"   Status: {booking.status}")
            print(f"   Details: {booking.details}")
            print(f"   Created: {booking.created_at}")
        
        print("\n" + "="*60)
        
    except Exception as e:
        logger.error(f"Failed to display bookings: {str(e)}")
        print(f"\n❌ Error retrieving bookings: {str(e)}")

async def main():
    """Main application entry point"""
    logger.info("Trip Planner Agent started")
    
    while True:
        try:
            await display_user_menu()
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                # New user
                print("\n📝 CREATE NEW ACCOUNT")
                print("="*60)
                print("\nEnter your name:")
                name = input("> ").strip()
                
                if not name:
                    print("❌ Name is required")
                    continue
                
                print("\nEnter your email (optional - press Enter to skip):")
                email = input("> ").strip()
                email = email if email else None
                
                if email:
                    existing = await db_manager.get_user_by_email(email)
                    if existing:
                        print(f"\n❌ Email already registered to: {existing.name}")
                        continue
                
                user = await db_manager.create_user(name=name, email=email)
                print(f"\n✅ Account created successfully!")
                logger.info(f"New user created: {user.user_id}")
                
                # Create first session
                session_id = await create_session_interactive(user.user_id)
                await run_conversation(user.user_id, session_id)
                
            elif choice == '2':
                # Existing user
                user = await handle_user_login()
                
                if not user:
                    continue
                
                # Session management loop
                while True:
                    await display_session_menu(user.name)
                    session_choice = input("\nSelect option: ").strip()
                    
                    if session_choice == '1':
                        # New session
                        session_id = await create_session_interactive(user.user_id)
                        await run_conversation(user.user_id, session_id)
                        
                    elif session_choice == '2':
                        # Resume session
                        session_id = await select_session(user.user_id)
                        if session_id:
                            await run_conversation(user.user_id, session_id)
                        
                    elif session_choice == '3':
                        # View sessions
                        await display_sessions(user.user_id)
                        input("\nPress Enter to continue...")
                        
                    elif session_choice == '4':
                        # Logout
                        print(f"\n👋 Goodbye, {user.name}!")
                        break
                    
                    else:
                        print("❌ Invalid option")
                
            elif choice == '3':
                # Debug - List all users
                users = await db_manager.list_users()
                print("\n" + "="*60)
                print("👥 ALL USERS (DEBUG)")
                print("="*60)
                for user in users:
                    print(f"\n• {user.name}")
                    print(f"  Email: {user.email or 'N/A'}")
                    print(f"  ID: {user.user_id[:8]}...")
                    print(f"  Created: {user.created_at}")
                print("\n" + "="*60)
                input("\nPress Enter to continue...")
                
            elif choice == '4':
                # Exit
                print("\n👋 Thank you for using Trip Planner Agent!")
                logger.info("Trip Planner Agent stopped")
                break
            
            else:
                print("❌ Invalid option. Please try again.")
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Application interrupted")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            print(f"\n❌ Error: {str(e)}")
            print("Please try again.\n")

if __name__ == "__main__":
    asyncio.run(main())