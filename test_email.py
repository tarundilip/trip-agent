"""
Test email notification after fix
"""
import asyncio
from core.notifications import notification_service

async def test_email():
    print("\n" + "="*80)
    print("🧪 TESTING EMAIL NOTIFICATION FIX")
    print("="*80)
    
    test_email = "4404fuchsia@goeschman.com"
    print(f"\n📧 Sending test email to: {test_email}")
    
    test_booking = {
        "from": "Mumbai",
        "to": "Howrah",
        "date": "2025-12-28",
        "mode": "train",
        "transport_name": "Shalimar LTT Express",
        "price": 750,
        "ticket_id": "PNR-2BU6QU"
    }
    
    results = await notification_service.send_booking_notification(
        user_email=test_email,
        user_name="John Doe",
        booking_type="Travel",
        booking_details=test_booking,
        booking_id="PNR-2BU6QU"
    )
    
    if results["email_sent"]:
        print("\n✅ SUCCESS! Email sent!")
        print(f"\n📬 Check your inbox at: {test_email}")
        print("\n💡 Look for email with subject: '✅ Booking Confirmed - PNR-2BU6QU'")
    else:
        print("\n❌ FAILED! Email was not sent.")
        print("\n🔍 Check:")
        print("1. SENDER_EMAIL in .env is correct")
        print("2. SENDER_PASSWORD is valid App Password")
        print("3. Internet connection is working")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(test_email())