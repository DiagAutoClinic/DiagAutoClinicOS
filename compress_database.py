#!/usr/bin/env python3
"""
Database Compression Script for AutoDiag CAN Bus Database
This script performs comprehensive database compression and optimization.
"""

import sqlite3
import os
import shutil
from pathlib import Path
import tempfile
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_compression.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseCompressor:
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.backup_path = self.db_path.with_suffix('.sqlite.backup')
        self.temp_path = None
        
    def get_file_size(self, path):
        """Get file size in bytes"""
        return path.stat().st_size if path.exists() else 0
        
    def format_size(self, size_bytes):
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
        
    def analyze_database(self, conn):
        """Analyze database structure and statistics"""
        logger.info("Analyzing database structure...")
        
        cursor = conn.cursor()
        
        # Get basic database info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        logger.info(f"Found {len(tables)} tables:")
        
        total_rows = 0
        total_indexes = 0
        
        for table in tables:
            table_name = table[0]
            logger.info(f"  - {table_name}")
            
            # Get row count
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                row_count = cursor.fetchone()[0]
                total_rows += row_count
                logger.info(f"    Rows: {row_count:,}")
            except sqlite3.Error as e:
                logger.warning(f"    Could not count rows: {e}")
            
            # Get indexes
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='{table_name}';")
            indexes = cursor.fetchall()
            total_indexes += len(indexes)
            if indexes:
                logger.info(f"    Indexes: {len(indexes)}")
        
        # Get database page info
        cursor.execute("PRAGMA page_size;")
        page_size = cursor.fetchone()[0]
        
        cursor.execute("PRAGMA page_count;")
        page_count = cursor.fetchone()[0]
        
        cursor.execute("PRAGMA freelist_count;")
        freelist_count = cursor.fetchone()[0]
        
        logger.info(f"Database statistics:")
        logger.info(f"  Page size: {page_size} bytes")
        logger.info(f"  Total pages: {page_count:,}")
        logger.info(f"  Free pages: {freelist_count:,}")
        logger.info(f"  Total rows: {total_rows:,}")
        logger.info(f"  Total indexes: {total_indexes}")
        
        return {
            'tables': len(tables),
            'total_rows': total_rows,
            'total_indexes': total_indexes,
            'page_size': page_size,
            'page_count': page_count,
            'freelist_count': freelist_count
        }
        
    def create_backup(self):
        """Create a backup of the original database"""
        logger.info("Creating backup...")
        if self.backup_path.exists():
            self.backup_path.unlink()
        shutil.copy2(self.db_path, self.backup_path)
        logger.info(f"Backup created: {self.backup_path}")
        
    def optimize_database(self, conn):
        """Optimize database structure and performance"""
        logger.info("Optimizing database...")
        
        cursor = conn.cursor()
        
        # Enable WAL mode for better performance and smaller file size
        try:
            cursor.execute("PRAGMA journal_mode=WAL;")
            wal_mode = cursor.fetchone()[0]
            logger.info(f"WAL mode enabled: {wal_mode}")
        except sqlite3.Error as e:
            logger.warning(f"Could not enable WAL mode: {e}")
        
        # Set synchronous to NORMAL for better performance
        try:
            cursor.execute("PRAGMA synchronous=NORMAL;")
            logger.info("Synchronous mode set to NORMAL")
        except sqlite3.Error as e:
            logger.warning(f"Could not set synchronous mode: {e}")
        
        # Set cache size to optimal value
        try:
            cursor.execute("PRAGMA cache_size=10000;")  # 10MB cache
            logger.info("Cache size set to 10MB")
        except sqlite3.Error as e:
            logger.warning(f"Could not set cache size: {e}")
        
        # Analyze all tables for query optimization
        try:
            cursor.execute("ANALYZE;")
            logger.info("Database analysis completed")
        except sqlite3.Error as e:
            logger.warning(f"Could not analyze database: {e}")
        
        conn.commit()
        
    def vacuum_database(self, conn):
        """Vacuum the database to reclaim space"""
        logger.info("Vacuuming database to reclaim space...")
        
        try:
            conn.execute("VACUUM;")
            logger.info("Database vacuum completed successfully")
        except sqlite3.Error as e:
            logger.error(f"Database vacuum failed: {e}")
            raise
            
    def compress_with_temp_db(self):
        """Create a new compressed database using a temporary file"""
        logger.info("Creating compressed database using temporary file...")
        
        with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as temp_file:
            self.temp_path = Path(temp_file.name)
            
        try:
            # Connect to original database and backup to temp
            source_conn = sqlite3.connect(self.db_path)
            dest_conn = sqlite3.connect(self.temp_path)
            
            # Copy data to new database
            source_conn.backup(dest_conn)
            
            # Close connections
            source_conn.close()
            dest_conn.close()
            
            # Vacuum the temporary database
            temp_conn = sqlite3.connect(self.temp_path)
            self.vacuum_database(temp_conn)
            temp_conn.close()
            
            # Replace original with compressed version
            if self.db_path.exists():
                self.db_path.unlink()
            shutil.move(str(self.temp_path), str(self.db_path))
            
            logger.info("Database compression completed successfully")
            
        except Exception as e:
            logger.error(f"Error during compression: {e}")
            if self.temp_path and self.temp_path.exists():
                self.temp_path.unlink()
            raise
            
    def compress_database(self):
        """Main compression method"""
        start_time = datetime.now()
        
        # Check if database exists
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database file not found: {self.db_path}")
        
        original_size = self.get_file_size(self.db_path)
        logger.info(f"Starting database compression: {self.format_size(original_size)}")
        
        # Create backup
        self.create_backup()
        
        try:
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            
            # Analyze database
            stats = self.analyze_database(conn)
            
            # Optimize database settings
            self.optimize_database(conn)
            
            # Vacuum
            self.vacuum_database(conn)
            
            # Close connection
            conn.close()
            
            # Get new size
            new_size = self.get_file_size(self.db_path)
            compression_ratio = (1 - new_size / original_size) * 100 if original_size > 0 else 0
            
            # Calculate savings
            saved_bytes = original_size - new_size
            end_time = datetime.now()
            duration = end_time - start_time
            
            logger.info("=" * 50)
            logger.info("COMPRESSION RESULTS:")
            logger.info(f"Original size: {self.format_size(original_size)}")
            logger.info(f"Compressed size: {self.format_size(new_size)}")
            logger.info(f"Space saved: {self.format_size(saved_bytes)} ({compression_ratio:.1f}%)")
            logger.info(f"Duration: {duration.total_seconds():.2f} seconds")
            logger.info(f"Backup saved: {self.backup_path}")
            logger.info("=" * 50)
            
            # Clean up temporary files
            if self.temp_path and self.temp_path.exists():
                self.temp_path.unlink()
                
            return {
                'original_size': original_size,
                'compressed_size': new_size,
                'saved_bytes': saved_bytes,
                'compression_ratio': compression_ratio,
                'duration': duration.total_seconds(),
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            
            # Restore backup if compression failed
            if self.backup_path.exists():
                logger.info("Restoring from backup...")
                shutil.copy2(self.backup_path, self.db_path)
                logger.info("Database restored from backup")
            
            raise

def main():
    """Main function"""
    db_path = "can_bus_databases.sqlite"
    
    print("AutoDiag Database Compression Tool")
    print("=" * 40)
    
    compressor = DatabaseCompressor(db_path)
    
    try:
        results = compressor.compress_database()
        print(f"\n✅ Database compression completed successfully!")
        print(f"💾 Space saved: {results['compression_ratio']:.1f}%")
        print(f"📁 Backup created: {compressor.backup_path}")
        
    except Exception as e:
        print(f"\n❌ Compression failed: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main())