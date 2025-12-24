#!/usr/bin/env python3
"""
Test Bench: OBDLink MX+ ECU Communication Test
Tests MX+ device with ECU for connection and data transfer performance
"""

import logging
import time
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[0]
import sys
sys.path.insert(0, str(PROJECT_ROOT))

# Import Charlemaine for AI diagnosis
import charlemaine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class BenchResult:
    """Test bench result data"""
    test_name: str
    timestamp: float
    success: bool
    duration_ms: float
    data_received: int
    error_message: Optional[str] = None

class MXBench:
    """Test bench for OBDLink MX+ device"""

    def __init__(self):
        self.results: List[BenchResult] = []
        self.device = None

    def initialize_device(self) -> bool:
        """Initialize OBDLink MX+ device"""
        logger.info("Initializing OBDLink MX+...")

        try:
            from shared.obdlink_mxplus import create_obdlink_mxplus
            self.device = create_obdlink_mxplus(mock_mode=False)
            logger.info("✓ OBDLink MX+ initialized")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to initialize OBDLink MX+: {e}")
            return False

    def connect_device(self) -> bool:
        """Connect MX+ to ECU"""
        logger.info("Connecting OBDLink MX+ to ECU...")

        try:
            # Try common ports for MX+
            ports_to_try = ["COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "COM10"]
            for port in ports_to_try:
                logger.debug(f"Trying port {port}...")
                if self.device.connect_serial(port, 38400):
                    logger.info(f"✓ OBDLink MX+ connected on {port}")
                    return True

            logger.error("✗ OBDLink MX+ connection failed - no available ports")
            return False

        except Exception as e:
            logger.error(f"✗ OBDLink MX+ connection error: {e}")
            return False

    def run_connection_test(self) -> BenchResult:
        """Run ECU connection test"""
        logger.info("Running ECU connection test...")

        start_time = time.time()
        success = False
        data_received = 0
        error_message = None

        try:
            if self.device and self.device.is_connected:
                # Send ATI command to test ECU response
                self.device._send_command(b'ATI\r\n')
                time.sleep(0.2)
                response = self.device._read_response(timeout=2.0)

                if response and len(response.strip()) > 0:
                    success = True
                    data_received = len(response)
                    logger.info(f"✓ ECU responded: {response.strip()}")
                else:
                    error_message = "No response from ECU"
            else:
                error_message = "Device not connected"

        except Exception as e:
            error_message = str(e)
            logger.error(f"Connection test error: {e}")

        duration = (time.time() - start_time) * 1000  # ms

        result = BenchResult(
            test_name="ECU Connection Test",
            timestamp=time.time(),
            success=success,
            duration_ms=duration,
            data_received=data_received,
            error_message=error_message
        )

        self.results.append(result)
        return result

    def run_can_monitoring_test(self, duration_sec: int = 15) -> BenchResult:
        """Run CAN bus monitoring performance test"""
        logger.info(f"Running CAN monitoring test ({duration_sec}s)...")

        start_time = time.time()
        success = False
        data_received = 0
        error_message = None

        try:
            if self.device and self.device.is_connected:
                # Configure for CAN sniffing
                if self.device.configure_can_sniffing():
                    logger.info("✓ CAN sniffing configured")

                    # Start monitoring
                    if self.device.start_monitoring():
                        logger.info("✓ CAN monitoring started")

                        # Monitor for specified duration
                        messages = []
                        monitor_start = time.time()

                        while time.time() - monitor_start < duration_sec:
                            new_messages = self.device.read_messages(count=50, timeout_ms=100)
                            messages.extend(new_messages)
                            time.sleep(0.05)  # Small delay

                        # Stop monitoring
                        self.device.stop_monitoring()
                        data_received = len(messages)
                        success = True

                        logger.info(f"✓ Captured {data_received} CAN messages")

                        # Log some sample messages
                        if messages:
                            logger.info("Sample CAN messages:")
                            for msg in messages[:5]:  # Show first 5
                                logger.info(f"  {msg}")

                    else:
                        error_message = "Failed to start CAN monitoring"
                else:
                    error_message = "Failed to configure CAN sniffing"
            else:
                error_message = "Device not connected"

        except Exception as e:
            error_message = str(e)
            logger.error(f"CAN monitoring test error: {e}")

        duration = (time.time() - start_time) * 1000  # ms

        result = BenchResult(
            test_name=f"CAN Monitoring Test ({duration_sec}s)",
            timestamp=time.time(),
            success=success,
            duration_ms=duration,
            data_received=data_received,
            error_message=error_message
        )

        self.results.append(result)
        return result

    def run_protocol_test(self) -> BenchResult:
        """Test different protocol configurations"""
        logger.info("Running protocol configuration test...")

        start_time = time.time()
        success = False
        data_received = 0
        error_message = None

        try:
            if self.device and self.device.is_connected:
                from shared.obdlink_mxplus import OBDLinkProtocol

                protocols = [OBDLinkProtocol.ISO15765_11BIT, OBDLinkProtocol.ISO15765_29BIT, OBDLinkProtocol.AUTO]
                working_protocols = []

                for protocol in protocols:
                    try:
                        if self.device.configure_can_sniffing(protocol):
                            working_protocols.append(protocol.value)
                            data_received += 1
                    except Exception as e:
                        logger.debug(f"Protocol {protocol.value} failed: {e}")

                if working_protocols:
                    success = True
                    logger.info(f"✓ Working protocols: {', '.join(working_protocols)}")
                else:
                    error_message = "No protocols working"
            else:
                error_message = "Device not connected"

        except Exception as e:
            error_message = str(e)
            logger.error(f"Protocol test error: {e}")

        duration = (time.time() - start_time) * 1000  # ms

        result = BenchResult(
            test_name="Protocol Configuration Test",
            timestamp=time.time(),
            success=success,
            duration_ms=duration,
            data_received=data_received,
            error_message=error_message
        )

        self.results.append(result)
        return result

    def run_full_bench_test(self) -> List[BenchResult]:
        """Run complete benchmark test suite"""
        logger.info("Starting OBDLink MX+ benchmark test suite...")

        # Initialize device
        if not self.initialize_device():
            logger.error("Failed to initialize device")
            return []

        # Connect device
        if not self.connect_device():
            logger.error("Failed to connect device")
            return []

        # Run tests
        test_results = []

        # Connection test
        result = self.run_connection_test()
        test_results.append(result)

        # Protocol test
        result = self.run_protocol_test()
        test_results.append(result)

        # CAN monitoring tests
        result = self.run_can_monitoring_test(10)  # 10 second test
        test_results.append(result)

        result = self.run_can_monitoring_test(30)  # 30 second test
        test_results.append(result)

        # Cleanup
        self.cleanup()

        return test_results

    def cleanup(self):
        """Clean up device connection"""
        try:
            if self.device:
                self.device.disconnect()
                logger.info("OBDLink MX+ disconnected")
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")

    def print_results(self, results: List[BenchResult]):
        """Print test results in a formatted way"""
        print("\n" + "="*80)
        print("OBDLINK MX+ ECU TEST BENCH RESULTS")
        print("="*80)

        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Tests Run: {len(results)}")
        print()

        successful_tests = sum(1 for r in results if r.success)
        total_data = sum(r.data_received for r in results)

        print("TEST RESULTS:")
        print("-" * 40)

        for result in results:
            status = "✓ PASS" if result.success else "✗ FAIL"
            print(f"  {result.test_name}: {status}")
            print(".2f")
            if result.data_received > 0:
                print(f"    Data Received: {result.data_received}")
            if result.error_message:
                print(f"    Error: {result.error_message}")
            print()

        print("SUMMARY:")
        print("-" * 40)
        print(f"Success Rate: {successful_tests}/{len(results)} tests")
        print(f"Total Data Processed: {total_data}")
        print(".2f")

        if successful_tests == len(results):
            print("🎉 All tests passed! MX+ is working correctly with ECU.")
        elif successful_tests > 0:
            print("⚠️  Partial success - some tests passed.")
        else:
            print("❌ All tests failed - check connections and ECU.")

def main():
    """Main test bench execution"""
    print("OBDLink MX+ ECU Test Bench")
    print("Testing MX+ device with ECU communication")
    print("="*50)

    bench = MXBench()
    results = bench.run_full_bench_test()

    if results:
        bench.print_results(results)
    else:
        print("No test results - check device connections and try again")

    print("\nTest bench completed.")

if __name__ == "__main__":
    main()