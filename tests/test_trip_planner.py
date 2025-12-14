import pytest
from datetime import datetime, timedelta
from core.trip_tool_context import TripToolContext
from core.session_service import session_manager
from trip_tools.accom_tools import parse_accommodation_details, check_accommodation_state, book_accommodation
from trip_tools.travel_tools import parse_travel_details, check_travel_state, book_travel
from trip_tools.sightseeing_tools import parse_sightseeing_details, check_sightseeing_state, plan_sightseeing

@pytest.mark.asyncio
async def test_full_trip_planning():
    """Test the complete trip planning workflow"""
    # Create a test session
    session_data = await session_manager.create_user_session(
        name="Test User",
        email="test@example.com"
    )
    
    # Initialize context
    context = TripToolContext(session_id=session_data["session_id"])
    await context.initialize()
    
    # Test accommodation booking
    accom_input = "Book hotel in Mumbai from 2024-01-01 to 2024-01-03 with budget 5000 per night"
    accom_parse = parse_accommodation_details(context, accom_input)
    assert accom_parse["status"] == "success"
    
    # Test travel booking
    travel_input = "Book travel from Delhi to Mumbai on 2024-01-01 by flight"
    travel_parse = parse_travel_details(context, travel_input)
    assert travel_parse["status"] == "success"
    
    # Test sightseeing planning
    sight_input = "Plan visit to Gateway of India on 2024-01-02"
    sight_parse = parse_sightseeing_details(context, sight_input)
    assert sight_parse["status"] == "success"