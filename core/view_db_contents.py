import os
import asyncio
import aiosqlite

DB_PATH = os.getenv("DB_PATH", "trip_planner.sqlite")

async def print_table(table_name):
    print(f"\n=== {table_name.upper()} ===")
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(f"SELECT * FROM {table_name}") as cursor:
                columns = [col[0] for col in cursor.description]
                rows = await cursor.fetchall()

                if not rows:
                    print("No records found.")
                    return

                print(" | ".join(columns))
                for row in rows:
                    print(" | ".join(str(val) for val in row))
    except Exception as e:
        print(f"Error reading `{table_name}`: {e}")

async def main():
    await print_table("sessions")
    await print_table("travel_bookings")
    await print_table("accommodation_bookings")
    await print_table("sightseeing_plans")

if __name__ == "__main__":
    asyncio.run(main())