#!/usr/bin/env python3
"""
Advanced Database Compression Script
This script provides multiple compression strategies including file-level compression.
"""

import sqlite3
import gzip
import zlib
import os
import shutil
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedDatabaseCompressor:
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.compressed_path = self.db_path.with_suffix('.sqlite.gz')
        
    def compress_file_gzip(self):
        """Compress database file using gzip"""
        logger.info("Compressing database file with gzip...")
        
        with open(self.db_path, 'rb') as f_in:
            with gzip.open(self.compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        original_size = self.db_path.stat().st_size
        compressed_size = self.compressed_path.stat().st_size
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        logger.info(f"Gzip compression results:")
        logger.info(f"  Original: {original_size:,} bytes")
        logger.info(f"  Compressed: {compressed_size:,} bytes")
        logger.info(f"  Ratio: {compression_ratio:.1f}%")
        
        return {
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': compression_ratio,
            'method': 'gzip'
        }
    
    def compress_file_zlib(self):
        """Compress database file using zlib"""
        logger.info("Compressing database file with zlib...")
        
        compressed_path = self.db_path.with_suffix('.sqlite.zlib')
        
        with open(self.db_path, 'rb') as f:
            data = f.read()
        
        compressed_data = zlib.compress(data, level=9)  # Maximum compression
        
        with open(compressed_path, 'wb') as f:
            f.write(compressed_data)
        
        original_size = self.db_path.stat().st_size
        compressed_size = compressed_path.stat().st_size
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        logger.info(f"Zlib compression results:")
        logger.info(f"  Original: {original_size:,} bytes")
        logger.info(f"  Compressed: {compressed_size:,} bytes")
        logger.info(f"  Ratio: {compression_ratio:.1f}%")
        
        return {
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': compression_ratio,
            'method': 'zlib',
            'compressed_path': compressed_path
        }
    
    def create_compressed_backup(self):
        """Create a highly compressed backup"""
        logger.info("Creating compressed backup...")
        
        # Test different compression methods
        gzip_result = self.compress_file_gzip()
        zlib_result = self.compress_file_zlib()
        
        # Choose the best compression
        if gzip_result['compression_ratio'] > zlib_result['compression_ratio']:
            best_method = 'gzip'
            best_result = gzip_result
        else:
            best_method = 'zlib'
            best_result = zlib_result
        
        logger.info(f"Best compression method: {best_method}")
        logger.info(f"Maximum space savings: {best_result['compression_ratio']:.1f}%")
        
        return best_result
    
    def decompress_file(self, compressed_path, output_path):
        """Decompress a compressed file"""
        if compressed_path.suffix == '.gz':
            with gzip.open(compressed_path, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        elif compressed_path.suffix == '.zlib':
            with open(compressed_path, 'rb') as f:
                compressed_data = f.read()
            decompressed_data = zlib.decompress(compressed_data)
            with open(output_path, 'wb') as f:
                f.write(decompressed_data)

def main():
    """Main function for advanced compression"""
    db_path = "can_bus_databases.sqlite"
    
    print("Advanced Database Compression Tool")
    print("=" * 40)
    
    if not Path(db_path).exists():
        print(f"Database file not found: {db_path}")
        return 1
    
    compressor = AdvancedDatabaseCompressor(db_path)
    
    try:
        result = compressor.create_compressed_backup()
        print(f"\nCompressed backup created successfully!")
        print(f"Compression ratio: {result['compression_ratio']:.1f}%")
        print(f"Method used: {result['method']}")
        
        if result['method'] == 'gzip':
            print(f"Compressed file: {compressor.compressed_path}")
        else:
            print(f"Compressed file: {result['compressed_path']}")
            
    except Exception as e:
        print(f"Compression failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())