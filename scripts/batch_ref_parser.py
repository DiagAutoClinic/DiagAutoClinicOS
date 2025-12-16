#!/usr/bin/env python3
"""
Batch processor for multiple Racelogic .REF files
Processes all .REF files in a directory and exports to SQLite database
"""

from ref_parser import RacelogicREFParser
import os
import glob
from pathlib import Path
import sqlite3

def batch_process_ref_files(input_dir: str, output_db: str):
    """
    Process all .REF files in input_dir and export to SQLite database
    
    Args:
        input_dir: Directory containing .REF files
        output_db: Output SQLite database path
    """
    parser = RacelogicREFParser()
    
    # Find all .REF files
    ref_files = glob.glob(os.path.join(input_dir, "*.REF"))
    
    if not ref_files:
        print(f"No .REF files found in {input_dir}")
        return
    
    print(f"Found {len(ref_files)} .REF files to process")
    
    databases = {}
    processed = 0
    errors = 0
    
    for ref_file in ref_files:
        try:
            filename = Path(ref_file).name
            print(f"Processing {filename}...")
            
            db = parser.parse_file(ref_file)
            # Use filename without extension as key
            databases[filename.replace('.REF', '')] = db
            processed += 1
            
            print(f"  -> {db.manufacturer} {db.model} ({db.year_range}) - {len(db.messages)} messages")
            
        except Exception as e:
            print(f"  -> ERROR processing {filename}: {e}")
            errors += 1
    
    if processed > 0:
        # Export to SQLite
        print(f"\nExporting {processed} databases to {output_db}...")
        parser.save_to_sqlite(databases, output_db)
        
        # Verify database
        if os.path.exists(output_db):
            conn = sqlite3.connect(output_db)
            c = conn.cursor()
            
            # Get summary stats
            c.execute("SELECT COUNT(*) FROM vehicles")
            vehicle_count = c.fetchone()[0]
            
            c.execute("SELECT COUNT(*) FROM messages")
            message_count = c.fetchone()[0]
            
            c.execute("SELECT COUNT(*) FROM signals")
            signal_count = c.fetchone()[0]
            
            print(f"SQLite database created successfully!")
            print(f"  - Vehicles: {vehicle_count}")
            print(f"  - Messages: {message_count}")
            print(f"  - Signals: {signal_count}")
            
            # Show sample data
            print("\nSample vehicle data:")
            c.execute("""
                SELECT v.make, v.model, v.years, COUNT(m.id) as msg_count 
                FROM vehicles v 
                LEFT JOIN messages m ON v.id = m.vehicle_id 
                GROUP BY v.id 
                LIMIT 5
            """)
            
            for row in c.fetchall():
                make, model, years, msg_count = row
                print(f"  - {make} {model} ({years}): {msg_count} messages")
            
            conn.close()
        else:
            print(f"ERROR: Failed to create database {output_db}")
    
    print(f"\nBatch processing complete!")
    print(f"  - Successfully processed: {processed} files")
    print(f"  - Errors: {errors} files")
    if processed > 0:
        print(f"  - Output database: {output_db}")

def main():
    """Main function with command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch process Racelogic .REF files")
    parser.add_argument("--input", "-i", 
                       default="can_bus_data/Vehicle_CAN_Files_REF",
                       help="Input directory containing .REF files")
    parser.add_argument("--output", "-o", 
                       default="can_bus_databases.sqlite",
                       help="Output SQLite database file")
    
    args = parser.parse_args()
    
    # Check if input directory exists
    if not os.path.exists(args.input):
        print(f"Error: Input directory does not exist: {args.input}")
        return
    
    # Process files
    batch_process_ref_files(args.input, args.output)

if __name__ == "__main__":
    main()