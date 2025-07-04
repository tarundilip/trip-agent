import random
import string

def generate_id(prefix="", length=6):
    return prefix + ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_pnr(): return generate_id("PNR-", 6)
def generate_ticket_number(): return generate_id("TKT-", 8)
def generate_boarding_pass(): return generate_id("BRD-", 7)
def generate_ferry_ticket(): return generate_id("FRY-", 7)
def generate_metro_token(): return generate_id("MTR-", 5)
def generate_tram_pass(): return generate_id("TRM-", 6)
def generate_room_number(): return "Room-" + str(random.randint(100, 999))
def generate_entry_id(): return generate_id("ENT-", 5)