#!/usr/bin/env python3
"""
AutoDiag Implementation Test Script
Tests the current implementation status and validates Day 1 objectives
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(PROJECT_ROOT))

# Import required modules at the top level
try:
    from AutoDiag.core.vci_manager import get_vci_manager
    from AutoDiag.core.can_bus_ref_parser import ref_parser, get_vehicle_database
    from AutoDiag.core.diagnostics import DiagnosticsController
    from AutoDiag.core.events import get_event_manager, EventType, Event
    logger.info("✅ All test dependencies imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import test dependencies: {e}")
    sys.exit(1)

def test_imports():
    """Test that all required modules can be imported"""
    logger.info("🔧 Testing module imports...")
    
    try:
        # Test core imports
        from AutoDiag.main import AutoDiagPro
        logger.info("✅ AutoDiagPro imported successfully")
        
        from AutoDiag.core.diagnostics import DiagnosticsController
        logger.info("✅ DiagnosticsController imported successfully")
        
        from AutoDiag.core.events import EventManager, get_event_manager
        logger.info("✅ Event system imported successfully")
        
        from AutoDiag.core.vci_manager import VCIManager, get_vci_manager
        logger.info("✅ VCI Manager imported successfully")
        
        from AutoDiag.core.can_bus_ref_parser import ref_parser, get_vehicle_database
        logger.info("✅ CAN bus REF parser imported successfully")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during imports: {e}")
        return False

def test_vci_manager():
    """Test VCI Manager functionality"""
    logger.info("🔧 Testing VCI Manager...")
    
    try:
        vci_manager = get_vci_manager()
        
        # Test device scanning
        logger.info("🔍 Scanning for VCI devices...")
        devices = vci_manager.scan_for_devices(timeout=5)
        logger.info(f"✅ Found {len(devices)} VCI devices")
        
        for device in devices:
            logger.info(f"  - {device.name} ({device.device_type.value})")
            if device.port:
                logger.info(f"    Port: {device.port}")
            logger.info(f"    Capabilities: {', '.join(device.capabilities)}")
        
        # Test supported devices
        supported = vci_manager.get_supported_devices()
        logger.info(f"✅ Supported VCI devices: {', '.join(supported)}")
        
        # Test connection status
        is_connected = vci_manager.is_connected()
        logger.info(f"✅ VCI connected: {is_connected}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ VCI Manager test failed: {e}")
        return False

def test_can_database():
    """Test CAN database functionality"""
    logger.info("🔧 Testing CAN Database...")
    
    try:
        # Test available vehicles
        vehicles = ref_parser.list_available_vehicles()
        logger.info(f"✅ Found {len(vehicles)} vehicle databases")
        
        # Test manufacturers
        manufacturers = ref_parser.get_manufacturers()
        logger.info(f"✅ Available manufacturers: {', '.join(manufacturers[:5])}...")
        
        # Test specific vehicle database
        if vehicles:
            test_vehicle = vehicles[0]
            logger.info(f"🔍 Testing database for {test_vehicle[0]} {test_vehicle[1]}")
            
            db = get_vehicle_database(test_vehicle[0], test_vehicle[1])
            if db:
                logger.info(f"✅ Database loaded: {len(db.messages)} messages")
                
                # Show some sample messages
                sample_messages = list(db.messages.values())[:3]
                for msg in sample_messages:
                    logger.info(f"  - 0x{msg.can_id:03X} {msg.name} ({len(msg.signals)} signals)")
                
                return True
            else:
                logger.error("❌ Failed to load vehicle database")
                return False
        else:
            logger.warning("⚠️ No vehicle databases found")
            return True
            
    except Exception as e:
        logger.error(f"❌ CAN Database test failed: {e}")
        return False

def test_diagnostics_controller():
    """Test Diagnostics Controller functionality"""
    logger.info("🔧 Testing Diagnostics Controller...")
    
    try:
        # Create diagnostics controller
        controller = DiagnosticsController()
        logger.info("✅ DiagnosticsController created")
        
        # Test available manufacturers
        manufacturers = controller.get_available_manufacturers()
        logger.info(f"✅ Available manufacturers: {len(manufacturers)}")
        
        # Test brand setting
        controller.set_brand("Toyota")
        logger.info(f"✅ Brand set to: {controller.get_brand()}")
        
        # Test voltage reading
        voltage = controller.get_current_voltage()
        logger.info(f"✅ Current voltage: {voltage}V")
        
        # Test VCI status
        vci_status = controller.get_vci_status()
        logger.info(f"✅ VCI status: {vci_status.get('status', 'unknown')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Diagnostics Controller test failed: {e}")
        return False

def test_event_system():
    """Test Event System functionality"""
    logger.info("🔧 Testing Event System...")
    
    try:
        event_manager = get_event_manager()
        logger.info("✅ Event Manager created")
        
        # Test event creation
        from AutoDiag.core.events import EventType, Event
        test_event = Event.create(EventType.SYSTEM_STARTUP, "test", {"message": "Test event"})
        logger.info("✅ Event created successfully")
        
        # Test event emission
        def test_callback(event):
            logger.info(f"✅ Event received: {event.event_type.value}")
        
        # Subscribe and emit
        sub_id = event_manager.subscribe(test_callback, [EventType.SYSTEM_STARTUP])
        event_manager.emit(test_event)
        
        # Cleanup
        event_manager.unsubscribe(sub_id)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Event System test failed: {e}")
        return False

def test_basic_operations():
    """Test basic diagnostic operations"""
    logger.info("🔧 Testing Basic Diagnostic Operations...")
    
    try:
        controller = DiagnosticsController()
        
        # Test quick scan
        logger.info("🔍 Running quick scan...")
        scan_result = controller.run_quick_scan("Toyota")
        logger.info(f"✅ Quick scan result: {scan_result.get('status', 'unknown')}")
        
        # Test DTC reading
        logger.info("🔍 Reading DTCs...")
        dtc_result = controller.read_dtcs("Toyota")
        logger.info(f"✅ DTC read result: {dtc_result.get('status', 'unknown')}")
        
        # Test ECU info
        logger.info("🔍 Getting ECU info...")
        ecu_result = controller.get_ecu_info("Toyota")
        logger.info(f"✅ ECU info result: {ecu_result.get('status', 'unknown')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Basic operations test failed: {e}")
        return False

def main():
    """Main test execution"""
    logger.info("🚀 Starting AutoDiag Implementation Tests")
    logger.info("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("VCI Manager", test_vci_manager),
        ("CAN Database", test_can_database),
        ("Diagnostics Controller", test_diagnostics_controller),
        ("Event System", test_event_system),
        ("Basic Operations", test_basic_operations),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    logger.info(f"\n📈 Overall: {passed} passed, {failed} failed")
    
    if failed == 0:
        logger.info("🎉 All tests passed! AutoDiag implementation is working correctly.")
        return 0
    else:
        logger.warning("⚠️ Some tests failed. Check the logs above for details.")
        return 1

if __name__ == '__main__':
    sys.exit(main())