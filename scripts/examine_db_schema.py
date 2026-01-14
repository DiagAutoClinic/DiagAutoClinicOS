#!/usr/bin/env python3
"""
Script to examine the SQLite database schema
"""

import sqlite3
import sys

def examine_database_schema(db_path):
    """Examine the schema of the SQLite database"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"Examining database: {db_path}")
        print("=" * 50)
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in the database")
            return False
        
        print(f"\nFound {len(tables)} tables:")
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print(f"  Columns: {len(columns)}")
            for column in columns:
                print(f"    - {column[1]} ({column[2]})")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            print(f"  Rows: {row_count}")
            
            # Show sample data
            if row_count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                sample_data = cursor.fetchall()
                print(f"  Sample data:")
                for row in sample_data:
                    print(f"    {row}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error examining database: {e}")
        return False

if __name__ == "__main__":
    db_path = "can_bus_databases.sqlite"
    success = examine_database_schema(db_path)
    sys.exit(0 if success else 1)