#!/usr/bin/env python3
"""
Database Compression Summary Report
Shows all compression results and file sizes
"""

import os
from pathlib import Path

def format_size(size_bytes):
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def main():
    """Generate compression summary"""
    db_path = Path("can_bus_databases.sqlite")
    
    print("AUTODIAG DATABASE COMPRESSION SUMMARY")
    print("=" * 50)
    
    # Check if original database exists
    if not db_path.exists():
        print("ERROR: Original database not found!")
        return 1
    
    # Get file sizes
    original_size = db_path.stat().st_size
    backup_path = db_path.with_suffix('.sqlite.backup')
    backup_size = backup_path.stat().st_size if backup_path.exists() else 0
    
    gzip_path = db_path.with_suffix('.sqlite.gz')
    gzip_size = gzip_path.stat().st_size if gzip_path.exists() else 0
    
    zlib_path = db_path.with_suffix('.sqlite.zlib')
    zlib_size = zlib_path.stat().st_size if zlib_path.exists() else 0
    
    print(f"ORIGINAL DATABASE:")
    print(f"  File: {db_path}")
    print(f"  Size: {format_size(original_size)}")
    print()
    
    print(f"COMPRESSION RESULTS:")
    print(f"-" * 30)
    
    # SQLite Optimization (VACUUM + WAL)
    sqlite_savings = original_size - backup_size
    sqlite_ratio = (sqlite_savings / original_size) * 100 if original_size > 0 else 0
    print(f"SQLite Optimization:")
    print(f"  Backup: {format_size(backup_size)}")
    print(f"  Savings: {format_size(sqlite_savings)} ({sqlite_ratio:.1f}%)")
    print()
    
    # Gzip Compression
    if gzip_size > 0:
        gzip_savings = original_size - gzip_size
        gzip_ratio = (gzip_savings / original_size) * 100 if original_size > 0 else 0
        print(f"Gzip Compression:")
        print(f"  File: {gzip_path}")
        print(f"  Size: {format_size(gzip_size)}")
        print(f"  Savings: {format_size(gzip_savings)} ({gzip_ratio:.1f}%)")
        print()
    
    # Zlib Compression
    if zlib_size > 0:
        zlib_savings = original_size - zlib_size
        zlib_ratio = (zlib_savings / original_size) * 100 if original_size > 0 else 0
        print(f"Zlib Compression:")
        print(f"  File: {zlib_path}")
        print(f"  Size: {format_size(zlib_size)}")
        print(f"  Savings: {format_size(zlib_savings)} ({zlib_ratio:.1f}%)")
        print()
    
    # Best compression method
    if gzip_size > 0 and zlib_size > 0:
        if gzip_size < zlib_size:
            best_method = "gzip"
            best_size = gzip_size
            best_file = gzip_path
        else:
            best_method = "zlib"
            best_size = zlib_size
            best_file = zlib_path
        
        best_savings = original_size - best_size
        best_ratio = (best_savings / original_size) * 100 if original_size > 0 else 0
        
        print(f"BEST COMPRESSION METHOD:")
        print(f"  Method: {best_method.upper()}")
        print(f"  File: {best_file}")
        print(f"  Total Savings: {format_size(best_savings)} ({best_ratio:.1f}%)")
        print()
    
    print(f"RECOMMENDATIONS:")
    print(f"-" * 20)
    print(f"1. Use the main database (can_bus_databases.sqlite) for regular operations")
    print(f"2. Keep the SQLite backup for recovery purposes")
    print(f"3. Use compressed files for long-term storage or distribution")
    print(f"4. The zlib compressed file provides the best compression ratio")
    
    return 0

if __name__ == "__main__":
    exit(main())