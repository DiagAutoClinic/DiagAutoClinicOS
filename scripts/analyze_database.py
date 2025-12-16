#!/usr/bin/env python3
"""
Analyze the parsed CAN database and identify patterns
"""

import sqlite3
import json
from collections import Counter

def analyze_database(db_path="can_database.db"):
    """Analyze the parsed database structure"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("="*60)
    print("CAN DATABASE ANALYSIS")
    print("="*60)
    
    # 1. Count vehicles by manufacturer
    cursor.execute("""
        SELECT make, COUNT(*) as count 
        FROM vehicles 
        GROUP BY make 
        ORDER BY count DESC
    """)
    
    print("\n📊 VEHICLES BY MANUFACTURER:")
    print("-"*40)
    for make, count in cursor.fetchall():
        print(f"  {make:15} : {count:3} vehicles")
    
    # 2. Get total statistics
    cursor.execute("SELECT COUNT(*) FROM vehicles")
    total_vehicles = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM messages")
    total_messages = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM signals")
    total_signals = cursor.fetchone()[0]
    
    print(f"\n📈 TOTAL STATISTICS:")
    print(f"  Vehicles: {total_vehicles}")
    print(f"  CAN Messages: {total_messages}")
    print(f"  Signals: {total_signals}")
    
    # 3. Find common signals across manufacturers
    print("\n🔍 TOP 10 MOST COMMON SIGNALS:")
    print("-"*40)
    cursor.execute("""
        SELECT name, COUNT(DISTINCT vehicle_id) as vehicle_count
        FROM signals 
        JOIN messages ON signals.message_id = messages.id
        GROUP BY name 
        ORDER BY vehicle_count DESC 
        LIMIT 10
    """)
    
    for signal_name, count in cursor.fetchall():
        print(f"  {signal_name:30} : {count:3} vehicles")
    
    # 4. Analyze BMW specifically (most complete dataset)
    print("\n🏎️  BMW-SPECIFIC ANALYSIS:")
    print("-"*40)
    cursor.execute("""
        SELECT v.model, v.years, COUNT(DISTINCT m.id) as msg_count
        FROM vehicles v
        JOIN messages m ON v.id = m.vehicle_id
        WHERE v.make = 'BMW'
        GROUP BY v.model, v.years
        ORDER BY msg_count DESC
        LIMIT 5
    """)
    
    for model, years, msg_count in cursor.fetchall():
        print(f"  {model:25} ({years}): {msg_count:3} messages")
    
    # 5. Find diagnostic messages (common DTC patterns)
    print("\n🔧 DIAGNOSTIC MESSAGE PATTERNS:")
    print("-"*40)
    cursor.execute("""
        SELECT DISTINCT name 
        FROM signals 
        WHERE name LIKE '%DTC%' 
           OR name LIKE '%fault%' 
           OR name LIKE '%error%'
           OR name LIKE '%diagnos%'
        ORDER BY name
    """)
    
    dtc_signals = cursor.fetchall()
    for signal, in dtc_signals[:10]:  # Show first 10
        print(f"  • {signal}")
    
    conn.close()
    
    # 6. Save manufacturer summary to JSON
    cursor.execute("SELECT DISTINCT make FROM vehicles ORDER BY make")
    manufacturers = [row[0] for row in cursor.fetchall()]
    
    with open("manufacturers_summary.json", "w") as f:
        json.dump({"manufacturers": manufacturers, "total_vehicles": total_vehicles}, f, indent=2)
    
    print(f"\n✅ Analysis complete. {len(manufacturers)} manufacturers found.")
    return manufacturers

if __name__ == "__main__":
    analyze_database()