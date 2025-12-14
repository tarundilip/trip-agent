import os
import sqlite3

def find_and_check_databases():
    """Find all SQLite databases in the project"""
    
    print("\n" + "="*80)
    print("🔍 SEARCHING FOR DATABASES")
    print("="*80)
    
    # Check common locations
    db_locations = [
        "sessions.db",
        "trip_planner.sqlite",
        "temp_backup/trip_planner.db",
        "trip_planner.db"
    ]
    
    found_dbs = []
    
    for db_path in db_locations:
        if os.path.exists(db_path):
            found_dbs.append(db_path)
            size = os.path.getsize(db_path)
            print(f"\n✅ Found: {db_path}")
            print(f"   Size: {size:,} bytes")
            
            # Check tables
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                print(f"   Tables: {', '.join(tables) if tables else 'No tables'}")
                
                # Check row counts
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"     - {table}: {count} rows")
                
                conn.close()
            except Exception as e:
                print(f"   Error reading: {e}")
        else:
            print(f"\n❌ Not found: {db_path}")
    
    if not found_dbs:
        print("\n⚠️  No databases found!")
        print("💡 Run 'adk web' first to create the database.")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    find_and_check_databases()