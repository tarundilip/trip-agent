"""
Trip planning tools package
"""
from .common import (
    update_trip_plan,
    list_active_bookings,
    view_cancelled_bookings
)

# Travel tools
from .travel_tools import (
    parse_travel_details,
    check_travel_state,
    book_travel,
    cancel_travel_booking
)

# Accommodation tools
from .accom_tools import (
    parse_accommodation_details,
    check_accommodation_state,
    book_accommodation,
    cancel_accommodation_booking
)

# Sightseeing tools
from .sightseeing_tools import (
    parse_sightseeing_details,
    check_sightseeing_state,
    plan_sightseeing,
    book_sightseeing,
    cancel_sightseeing_booking
)

# Conversation tools
from .convo_tools import search_and_store

# Conflict checking tools
from .conflict_tools import (
    check_conflicts,           # ✅ MAIN FUNCTION
    check_trip_conflicts,      # ✅ ORIGINAL FUNCTION
    parse_trip_details,
    parse_and_check_conflicts
)

# Billing tools
from .billing_tools import (
    calculate_total_bill,
    get_bill_breakdown,
    estimate_trip_cost
)

# UI tools
from .ui_tools import (
    identify_user,
    list_user_sessions,
    get_current_user_info
)

__all__ = [
    # Common utilities
    'update_trip_plan',
    'list_active_bookings',
    'view_cancelled_bookings',
    
    # Travel
    'parse_travel_details',
    'check_travel_state',
    'book_travel',
    'cancel_travel_booking',
    
    # Accommodation
    'parse_accommodation_details',
    'check_accommodation_state',
    'book_accommodation',
    'cancel_accommodation_booking',
    
    # Sightseeing
    'parse_sightseeing_details',
    'check_sightseeing_state',
    'plan_sightseeing',
    'book_sightseeing',
    'cancel_sightseeing_booking',
    
    # Conflict checking
    'check_conflicts',           # ✅ MAIN FUNCTION
    'check_trip_conflicts',
    'parse_trip_details',
    'parse_and_check_conflicts',
    
    # Other
    'search_and_store',
    'calculate_total_bill',
    'get_bill_breakdown',
    'estimate_trip_cost',
    'identify_user',
    'list_user_sessions',
    'get_current_user_info'
]