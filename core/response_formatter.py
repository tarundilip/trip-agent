import re
from core.ticket_utils import (
    generate_pnr, generate_ticket_number, generate_boarding_pass,
    generate_ferry_ticket, generate_metro_token, generate_tram_pass,
    generate_room_number, generate_entry_id
)

def safe_line(label, value):
    return f"• {label}: {value}" if value else ""

def extract_from_raw(raw_response):
    match = re.search(r'from\s+(.+?)\s+to\s+(.+?)\s+on\s+(.+?)(?:\.|$)', raw_response, re.IGNORECASE)
    if match:
        return match.groups()
    return None, None, None

def format_booking_response(state: dict, raw_response: str) -> str:
    plan = state.get("trip_plan", {})
    travel = plan.get("travel", {})
    accommodation = plan.get("accommodation", {})
    sightseeing = plan.get("sightseeing", {})

    mode = travel.get("mode", "").lower()
    from_city = travel.get("from")
    to_city = travel.get("to")
    date = travel.get("date")

    if not (from_city and to_city and date):
        r_from, r_to, r_date = extract_from_raw(raw_response)
        from_city = from_city or r_from
        to_city = to_city or r_to
        date = date or r_date

    if "train" in raw_response.lower() or mode == "train":
        if from_city and to_city and date:
            return "\n".join(filter(None, [
                f" Train booked from {from_city} to {to_city} on {date}.",
                "",
                " Booking Details:",
                safe_line("Transport Mode", "Train"),
                safe_line("From", from_city),
                safe_line("To", to_city),
                safe_line("Date", date),
                safe_line("Departure Time", travel.get("departure_time")),
                safe_line("Arrival Time", travel.get("arrival_time")),
                safe_line("Seat Type", travel.get("seat_type")),
                safe_line("Price", f"₹{travel.get('price')}") if travel.get("price") else "",
                safe_line("PNR Number", generate_pnr()),
            ]))

    elif "flight" in raw_response.lower() or mode == "flight":
        if from_city and to_city and date:
            return "\n".join(filter(None, [
                f" Flight booked from {from_city} to {to_city} on {date}.",
                "",
                " Booking Details:",
                safe_line("Transport Mode", "Flight"),
                safe_line("Airline", travel.get("airline")),
                safe_line("From", from_city),
                safe_line("To", to_city),
                safe_line("Date", date),
                safe_line("Departure", travel.get("departure_time")),
                safe_line("Arrival", travel.get("arrival_time")),
                safe_line("Price", f"₹{travel.get('price')}") if travel.get("price") else "",
                safe_line("Boarding Pass No.", generate_boarding_pass()),
            ]))

    elif "bus" in raw_response.lower() or mode == "bus":
        if from_city and to_city and date:
            return "\n".join(filter(None, [
                f" Bus ticket confirmed from {from_city} to {to_city} on {date}.",
                "",
                " Booking Details:",
                safe_line("Transport Mode", "Bus"),
                safe_line("Bus Provider", travel.get("provider")),
                safe_line("From", from_city),
                safe_line("To", to_city),
                safe_line("Departure", travel.get("departure_time")),
                safe_line("Seat", travel.get("seat_type")),
                safe_line("Price", f"₹{travel.get('price')}") if travel.get("price") else "",
                safe_line("Ticket Number", generate_ticket_number()),
            ]))

    elif "ferry" in raw_response.lower() or mode == "ferry":
        if from_city and to_city and date:
            return "\n".join(filter(None, [
                f" Ferry booking confirmed from {from_city} to {to_city} on {date}.",
                "",
                " Booking Details:",
                safe_line("Transport Mode", "Ferry"),
                safe_line("Ferry Operator", travel.get("provider")),
                safe_line("From", from_city),
                safe_line("To", to_city),
                safe_line("Departure", travel.get("departure_time")),
                safe_line("Duration", travel.get("duration")),
                safe_line("Seat Type", travel.get("seat_type")),
                safe_line("Price", f"₹{travel.get('price')}") if travel.get("price") else "",
                safe_line("Ferry Ticket", generate_ferry_ticket()),
            ]))

    elif "metro" in raw_response.lower() or mode == "metro":
        if from_city and to_city and date:
            return "\n".join(filter(None, [
                f" Metro journey confirmed on {date} from {from_city} to {to_city}.",
                "",
                " Booking Details:",
                safe_line("Transport Mode", "Metro"),
                safe_line("Line", travel.get("line")),
                safe_line("From", from_city),
                safe_line("To", to_city),
                safe_line("Departure", travel.get("departure_time")),
                safe_line("Seat Type", travel.get("seat_type")),
                safe_line("Price", f"₹{travel.get('price')}") if travel.get("price") else "",
                safe_line("Metro Token", generate_metro_token()),
            ]))

    elif "tram" in raw_response.lower() or mode == "tram":
        if from_city and to_city and date:
            return "\n".join(filter(None, [
                f" Tram ride confirmed on {date} from {from_city} to {to_city}.",
                "",
                " Booking Details:",
                safe_line("Transport Mode", "Tram"),
                safe_line("Tram Line", travel.get("line")),
                safe_line("From", from_city),
                safe_line("To", to_city),
                safe_line("Departure", travel.get("departure_time")),
                safe_line("Seat Type", travel.get("seat_type")),
                safe_line("Price", f"₹{travel.get('price')}") if travel.get("price") else "",
                safe_line("Tram Pass", generate_tram_pass()),
            ]))

    elif "hotel" in raw_response.lower() and accommodation.get("hotel_name"):
        return "\n".join(filter(None, [
            f" Hotel booking confirmed at {accommodation.get('hotel_name')} in {accommodation.get('city')}.",
            "",
            " Booking Details:",
            safe_line("Hotel", accommodation.get("hotel_name")),
            safe_line("City", accommodation.get("city")),
            safe_line("Check-in", accommodation.get("check_in")),
            safe_line("Check-out", accommodation.get("check_out")),
            safe_line("Guests", accommodation.get("guests")),
            safe_line("Room Type", accommodation.get("room_type")),
            safe_line("Room Number", generate_room_number()),
            safe_line("Price", f"₹{accommodation.get('price')}") if accommodation.get("price") else "",
        ]))

    elif "sightseeing" in raw_response.lower() and sightseeing.get("place"):
        return "\n".join(filter(None, [
            f" Sightseeing entry confirmed for {sightseeing.get('place')} on {sightseeing.get('date')}.",
            "",
            " Entry Details:",
            safe_line("Place", sightseeing.get("place")),
            safe_line("Date", sightseeing.get("date")),
            safe_line("Entry Slot", sightseeing.get("time")),
            safe_line("Price", f"₹{sightseeing.get('price')}") if sightseeing.get("price") else "",
            safe_line("Entry ID", generate_entry_id()),
        ]))

    return raw_response.strip()