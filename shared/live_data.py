#!/usr/bin/env python3
"""
Real Live Data System with CAN Bus Integration
Uses real automotive parameters from .REF files and VCI hardware
"""

import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class LiveDataGenerator:
    """Enhanced live data generator with real CAN bus integration"""
    
    def __init__(self):
        self.is_streaming = False
        self.last_update = time.time()
        self.mock_data_sources = {}
        self.real_can_data = {}
        self.current_brand = "Toyota"
        self.can_bus_manager = None
        
        # Initialize data sources
        self._initialize_data_sources()
        
    def _initialize_data_sources(self):
        """Initialize data source configuration - no mock data"""
        # Data sources will be populated from CAN database only
        pass
        
    def set_can_bus_manager(self, can_bus_manager):
        """Set the CAN bus data manager for real data integration"""
        self.can_bus_manager = can_bus_manager
        
    def set_current_brand(self, brand: str):
        """Set current vehicle brand for appropriate data"""
        self.current_brand = brand
        logger.info(f"Live data brand set to: {brand}")
        
        # Try to load real CAN data for this brand
        if self.can_bus_manager:
            success = self.can_bus_manager.load_brand_data(brand)
            if success:
                logger.info(f"Real CAN data loaded for {brand}")
            else:
                logger.warning(f"No CAN data available for {brand} — live data disabled until VCI connects")
    
    def start_stream(self):
        """Start live data streaming"""
        self.is_streaming = True
        self.last_update = time.time()
        logger.info("Live data streaming started")
        
    def stop_stream(self):
        """Stop live data streaming"""
        self.is_streaming = False
        logger.info("Live data streaming stopped")
        
    def get_live_data(self) -> List[tuple]:
        """Get current live data from real CAN bus sources only"""
        current_time = time.time()

        # If streaming, update timestamp
        if self.is_streaming:
            self.last_update = current_time

        # Get real CAN data only
        real_data = self._get_real_can_data()

        # If no real data available, return empty list
        if not real_data:
            logger.warning("No real CAN data available - live data streaming disabled")
            return []

        # Sort by parameter name for consistency
        real_data.sort(key=lambda x: x[0])

        return real_data
    
    def _get_real_can_data(self) -> List[tuple]:
        """Get real CAN bus data for current brand"""
        real_data = []

        if not self.can_bus_manager or not self.is_streaming:
            logger.debug("CAN bus manager not available or not streaming")
            return real_data

        try:
            # Get live CAN messages directly from the VCI hardware layer
            if not hasattr(self.can_bus_manager, 'read_live_messages'):
                logger.error("CAN bus manager has no read_live_messages — cannot stream live data")
                return real_data

            live_messages = self.can_bus_manager.read_live_messages()
            if not live_messages:
                logger.debug("No CAN messages from hardware")
                return real_data

            # Check if we have a DBC decoder for this brand
            available_brands = self.can_bus_manager.get_available_brands()
            if self.current_brand not in available_brands:
                logger.warning(f"Brand {self.current_brand} not in CAN database — cannot decode frames")
                return real_data

            real_parameters = self.can_bus_manager.get_real_time_data(
                self.current_brand, live_messages
            )

            for param_name, param_data in real_parameters.items():
                real_data.append((
                    param_name,
                    f"{param_data['value']:.1f}",
                    param_data['unit']
                ))

            if real_data:
                logger.debug(f"Retrieved {len(real_data)} CAN parameters for {self.current_brand}")

        except Exception as e:
            logger.error(f"Error retrieving real CAN data: {e}")

        return real_data
    
    def get_parameter_history(self, parameter_name: str, max_entries: int = 50) -> List[tuple]:
        """Get historical data for a parameter from the recorded buffer"""
        if not hasattr(self, '_history_buffer'):
            return []
        return list(self._history_buffer.get(parameter_name, []))[-max_entries:]

    def record_parameter(self, parameter_name: str, value: float):
        """Record a parameter value with timestamp for history"""
        if not hasattr(self, '_history_buffer'):
            from collections import deque
            self._history_buffer = {}
        if parameter_name not in self._history_buffer:
            from collections import deque
            self._history_buffer[parameter_name] = deque(maxlen=500)
        self._history_buffer[parameter_name].append((time.time(), value))
    
    def export_live_data(self, filename: Optional[str] = None) -> bool:
        """Export current live data to file"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"live_data_{self.current_brand}_{timestamp}.csv"
            
            import csv
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Parameter', 'Value', 'Unit', 'Timestamp'])
                
                live_data = self.get_live_data()
                for param_name, value, unit in live_data:
                    writer.writerow([param_name, value, unit, datetime.now().isoformat()])
            
            logger.info(f"Live data exported to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting live data: {e}")
            return False

# Global live data generator instance
live_data_generator = LiveDataGenerator()

def start_live_stream():
    """Start live data streaming"""
    live_data_generator.start_stream()

def stop_live_stream():
    """Stop live data streaming"""
    live_data_generator.stop_stream()

def get_live_data() -> List[tuple]:
    """Get current live data from real CAN sources"""
    return live_data_generator.get_live_data()

def set_brand_for_live_data(brand: str):
    """Set brand for live data generation"""
    live_data_generator.set_current_brand(brand)

def get_real_can_data_status() -> Dict[str, Any]:
    """Get status of real CAN data availability"""
    status = {
        'streaming': live_data_generator.is_streaming,
        'current_brand': live_data_generator.current_brand,
        'has_can_manager': live_data_generator.can_bus_manager is not None
    }
    
    if live_data_generator.can_bus_manager:
        status['available_brands'] = live_data_generator.can_bus_manager.get_available_brands()
        status['has_real_data'] = live_data_generator.current_brand in status['available_brands']
    else:
        status['available_brands'] = []
        status['has_real_data'] = False
    
    return status