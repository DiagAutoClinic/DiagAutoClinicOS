# shared/advance.py - Mock data for Advanced tab in AutoDiag

"""
Mock data and functions for the Advanced diagnostics tab.
Provides simulated advanced diagnostic capabilities.
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import random


@dataclass
class AdvancedFunction:
    """Represents an advanced diagnostic function"""
    name: str
    description: str
    category: str
    complexity: str  # 'Basic', 'Advanced', 'Expert'
    estimated_time: str
    mock_result: Dict[str, Any]


# Mock advanced functions data
ADVANCED_FUNCTIONS = [
    AdvancedFunction(
        name="ECU Communication Test",
        description="Test communication with all ECUs on the vehicle network",
        category="Communication",
        complexity="Basic",
        estimated_time="2-3 minutes",
        mock_result={
            "status": "SUCCESS",
            "ecus_found": 8,
            "communication_speed": "500kbps",
            "errors": 0,
            "details": "All ECUs responded successfully"
        }
    ),
    AdvancedFunction(
        name="CAN Bus Analysis",
        description="Analyze CAN bus traffic and detect anomalies",
        category="Network",
        complexity="Advanced",
        estimated_time="5-7 minutes",
        mock_result={
            "status": "SUCCESS",
            "bus_load": "45%",
            "error_frames": 2,
            "dominant_nodes": ["Engine ECU", "ABS Module"],
            "warnings": ["Minor timing variations detected"]
        }
    ),
    AdvancedFunction(
        name="Signal Integrity Check",
        description="Verify signal integrity across all vehicle sensors",
        category="Sensors",
        complexity="Advanced",
        estimated_time="4-6 minutes",
        mock_result={
            "status": "SUCCESS",
            "sensors_tested": 24,
            "failed_sensors": 0,
            "signal_quality": "98%",
            "recommendations": ["All sensors within specifications"]
        }
    ),
    AdvancedFunction(
        name="Network Topology Scan",
        description="Map the complete vehicle network topology",
        category="Network",
        complexity="Expert",
        estimated_time="8-10 minutes",
        mock_result={
            "status": "SUCCESS",
            "nodes_discovered": 12,
            "gateways": 2,
            "subnets": ["Powertrain", "Chassis", "Body"],
            "topology_map": "Generated successfully"
        }
    ),
    AdvancedFunction(
        name="Flash Memory Dump",
        description="Create backup of ECU flash memory",
        category="Memory",
        complexity="Expert",
        estimated_time="15-20 minutes",
        mock_result={
            "status": "SUCCESS",
            "memory_size": "2.5MB",
            "checksum": "0xA4F2B8C1",
            "backup_location": "/backups/ecu_flash_20241127.bin",
            "warnings": ["Ensure ignition remains ON during process"]
        }
    ),
    AdvancedFunction(
        name="Adaptive Parameters Reset",
        description="Reset all adaptive/learned parameters to factory defaults",
        category="Calibration",
        complexity="Advanced",
        estimated_time="3-5 minutes",
        mock_result={
            "status": "SUCCESS",
            "parameters_reset": 156,
            "systems_affected": ["Engine", "Transmission", "ABS"],
            "relearn_required": True,
            "notes": ["Test drive required for parameter relearning"]
        }
    ),
    AdvancedFunction(
        name="Security Access Test",
        description="Test security access levels and permissions",
        category="Security",
        complexity="Expert",
        estimated_time="1-2 minutes",
        mock_result={
            "status": "SUCCESS",
            "access_level": "FULL",
            "security_methods": ["Seed/Key", "PIN"],
            "vulnerabilities": 0,
            "recommendations": ["Security system intact"]
        }
    ),
    AdvancedFunction(
        name="Data Logging Setup",
        description="Configure advanced data logging parameters",
        category="Logging",
        complexity="Basic",
        estimated_time="1-2 minutes",
        mock_result={
            "status": "SUCCESS",
            "log_parameters": 45,
            "sample_rate": "100Hz",
            "storage_location": "/logs/advanced_session.log",
            "duration": "Unlimited"
        }
    )
]


def get_advanced_functions() -> List[AdvancedFunction]:
    """Get all available advanced functions"""
    return ADVANCED_FUNCTIONS


def get_functions_by_category(category: str) -> List[AdvancedFunction]:
    """Get advanced functions filtered by category"""
    return [func for func in ADVANCED_FUNCTIONS if func.category.lower() == category.lower()]


def get_functions_by_complexity(complexity: str) -> List[AdvancedFunction]:
    """Get advanced functions filtered by complexity level"""
    return [func for func in ADVANCED_FUNCTIONS if func.complexity.lower() == complexity.lower()]


def simulate_function_execution(function_name: str) -> Dict[str, Any]:
    """Simulate execution of an advanced function"""
    # Find the function
    func = next((f for f in ADVANCED_FUNCTIONS if f.name == function_name), None)
    if not func:
        return {
            "status": "ERROR",
            "error": f"Function '{function_name}' not found",
            "timestamp": datetime.now().isoformat()
        }

    # Simulate execution time
    execution_time = random.uniform(1, 5)

    # Add some randomness to results
    result = func.mock_result.copy()
    result["execution_time"] = f"{execution_time:.1f}s"
    result["timestamp"] = datetime.now().isoformat()

    # Add some random variations
    if "bus_load" in result:
        result["bus_load"] = f"{random.randint(35, 65)}%"
    if "signal_quality" in result:
        result["signal_quality"] = f"{random.randint(95, 100)}%"

    return result


def get_mock_advanced_data() -> Dict[str, Any]:
    """Get mock data for advanced diagnostics dashboard"""
    return {
        "system_status": {
            "overall_health": random.randint(85, 98),
            "network_status": "ACTIVE",
            "last_scan": datetime.now().isoformat(),
            "active_monitors": random.randint(8, 12)
        },
        "performance_metrics": {
            "cpu_usage": random.randint(15, 35),
            "memory_usage": random.randint(45, 65),
            "network_latency": f"{random.randint(2, 8)}ms",
            "throughput": f"{random.randint(450, 550)}kbps"
        },
        "recent_activities": [
            {
                "timestamp": datetime.now().isoformat(),
                "action": "ECU Communication Test",
                "status": "SUCCESS",
                "duration": "2.3s"
            },
            {
                "timestamp": (datetime.now().replace(second=datetime.now().second - 120)).isoformat(),
                "action": "Signal Integrity Check",
                "status": "SUCCESS",
                "duration": "4.1s"
            },
            {
                "timestamp": (datetime.now().replace(second=datetime.now().second - 300)).isoformat(),
                "action": "CAN Bus Analysis",
                "status": "WARNING",
                "duration": "6.8s"
            }
        ]
    }


# Export functions for use in main application
__all__ = [
    'get_advanced_functions',
    'get_functions_by_category',
    'get_functions_by_complexity',
    'simulate_function_execution',
    'get_mock_advanced_data',
    'AdvancedFunction'
]