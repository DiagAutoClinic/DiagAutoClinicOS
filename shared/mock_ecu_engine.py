#!/usr/bin/env python3
"""
Mock ECU Engine for Vehicle Emulation
Provides comprehensive ECU programming and diagnostic simulation
"""

import os
import json
import random
import time
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime

class MockECUEngine:
    """
    Advanced mock ECU engine for testing ECU programming scenarios
    Simulates dead ECU recovery, readiness checks, and file operations
    """

    def __init__(self, brand: str = "Volkswagen", model: str = "Generic"):
        self.brand = brand
        self.model = model
        self.ecu_state = {
            "power_status": "off",
            "communication_status": "disconnected",
            "security_access": "locked",
            "programming_session": "inactive",
            "start_ready": False,
            "immo_status": "active",
            "flash_memory": {},
            "dtc_codes": [],
            "parameters": {},
            "file_imports": []
        }

        # Load mock data
        self._load_mock_data()

    def _load_mock_data(self):
        """Load mock ECU data from fixtures"""
        try:
            fixture_path = Path(__file__).parent / ".." / "tests" / "fictures" / "vehicle_responses"
            if self.brand.lower() == "volkswagen":
                data_file = fixture_path / "vw_responses.json"
            elif self.brand.lower() == "toyota":
                data_file = fixture_path / "toyota_responses.json"
            else:
                data_file = fixture_path / "toyota_responses.json"  # fallback

            if data_file.exists():
                with open(data_file, 'r', encoding='utf-8-sig') as f:
                    self.mock_data = json.load(f)
            else:
                self.mock_data = self._create_default_mock_data()
        except Exception as e:
            print(f"Warning: Could not load mock data: {e}")
            self.mock_data = self._create_default_mock_data()

    def _create_default_mock_data(self) -> dict:
        """Create default mock data structure"""
        return {
            "ecu_states": {
                "dead_ecu": {
                    "communication_status": "no_response",
                    "start_ready": False,
                    "immo_status": "unknown",
                    "flash_memory": "corrupted"
                },
                "recovered_ecu": {
                    "communication_status": "ok",
                    "start_ready": True,
                    "immo_status": "disabled",
                    "flash_memory": "programmed"
                }
            },
            "programming_responses": {
                "security_access_granted": "0x67",
                "flash_write_success": "0x76",
                "checksum_valid": "0x77"
            }
        }

    def connect_to_ecu(self, ecu_address: str = "0x7E0") -> bool:
        """Simulate ECU connection"""
        if self.ecu_state["power_status"] == "off":
            return False

        self.ecu_state["communication_status"] = "connected"
        self.ecu_state["ecu_address"] = ecu_address
        return True

    def check_start_ready(self) -> Dict[str, Any]:
        """
        Check if ECU is start-ready for programming
        Simulates the readiness validation you need for dead ECUs
        """
        # Simulate various readiness conditions
        battery_voltage = round(random.uniform(11.5, 14.2), 1)
        communication_ok = self.ecu_state["communication_status"] == "connected"
        security_unlocked = self.ecu_state["security_access"] == "unlocked"
        programming_ready = self.ecu_state["programming_session"] == "active"

        # Determine overall readiness
        start_ready = (
            battery_voltage >= 12.0 and
            communication_ok and
            security_unlocked and
            programming_ready
        )

        self.ecu_state["start_ready"] = start_ready

        return {
            "start_ready": start_ready,
            "battery_voltage": battery_voltage,
            "communication_status": "OK" if communication_ok else "FAILED",
            "security_access": "GRANTED" if security_unlocked else "DENIED",
            "programming_session": "ACTIVE" if programming_ready else "INACTIVE",
            "timestamp": datetime.now().isoformat(),
            "diagnostics": self._get_readiness_diagnostics()
        }

    def _get_readiness_diagnostics(self) -> List[str]:
        """Get detailed readiness diagnostics"""
        diagnostics = []

        if self.ecu_state["communication_status"] != "connected":
            diagnostics.append("ECU communication failed - check power and connections")

        if self.ecu_state["security_access"] == "locked":
            diagnostics.append("Security access required - provide seed/key")

        if self.ecu_state["programming_session"] == "inactive":
            diagnostics.append("Programming session not active - initiate diagnostic session")

        if not self.ecu_state["start_ready"]:
            diagnostics.append("ECU not ready for programming - resolve above issues")

        return diagnostics

    def request_security_access(self, seed: Optional[str] = None) -> Dict[str, Any]:
        """
        Simulate security access for ECU programming
        """
        if seed is None:
            # Generate mock seed
            seed = f"{random.randint(0x1000, 0xFFFF):04X}"

        # Simple mock key calculation (real would be more complex)
        key = f"{int(seed, 16) ^ 0xABCD:04X}"

        self.ecu_state["security_access"] = "unlocked"
        self.ecu_state["security_seed"] = seed
        self.ecu_state["security_key"] = key

        return {
            "access_granted": True,
            "seed": seed,
            "key_required": key,
            "security_level": "factory",
            "timeout_seconds": 300
        }

    def initiate_programming_session(self) -> bool:
        """Start ECU programming session"""
        if self.ecu_state["security_access"] != "unlocked":
            return False

        self.ecu_state["programming_session"] = "active"
        self.ecu_state["session_start_time"] = datetime.now().isoformat()
        return True

    def simulate_immo_off(self) -> Dict[str, Any]:
        """
        Simulate IMMO (Immobilizer) disable operation
        """
        if self.ecu_state["programming_session"] != "active":
            return {"success": False, "error": "Programming session not active"}

        # Simulate IMMO disable
        self.ecu_state["immo_status"] = "disabled"
        self.ecu_state["immo_disabled_time"] = datetime.now().isoformat()

        return {
            "success": True,
            "operation": "immo_disable",
            "status": "completed",
            "immo_status": "disabled",
            "warning": "Vehicle may not start without key programming"
        }

    def simulate_egr_dpf_removal(self) -> Dict[str, Any]:
        """
        Simulate EGR-DPF removal/modification
        """
        if self.ecu_state["programming_session"] != "active":
            return {"success": False, "error": "Programming session not active"}

        # Simulate parameter modifications
        modifications = {
            "egr_valve": "disabled",
            "dpf_regeneration": "bypassed",
            "emissions_checks": "disabled"
        }

        self.ecu_state["parameters"].update(modifications)

        return {
            "success": True,
            "operation": "egr_dpf_removal",
            "modifications": modifications,
            "status": "completed",
            "warning": "Emissions compliance affected"
        }

    def import_start_ready_file(self, file_path: str) -> Dict[str, Any]:
        """
        Simulate importing start-ready configuration file
        This is what you need for dead ECU recovery
        """
        if not os.path.exists(file_path):
            return {"success": False, "error": f"File not found: {file_path}"}

        try:
            # Simulate file parsing and validation
            file_size = os.path.getsize(file_path)
            file_hash = f"mock_hash_{random.randint(1000, 9999)}"

            # Simulate importing configuration
            imported_config = {
                "file_name": os.path.basename(file_path),
                "file_size": file_size,
                "checksum": file_hash,
                "imported_at": datetime.now().isoformat(),
                "start_ready_config": {
                    "engine_type": "detected_from_file",
                    "fuel_system": "configured",
                    "ignition_system": "ready",
                    "sensors": "calibrated"
                }
            }

            self.ecu_state["file_imports"].append(imported_config)
            self.ecu_state["start_ready"] = True

            return {
                "success": True,
                "operation": "file_import",
                "file_info": imported_config,
                "start_ready_status": "enabled",
                "validation": "passed"
            }

        except Exception as e:
            return {"success": False, "error": f"Import failed: {str(e)}"}

    def add_start_ready_dtc(self, dtc_code: str = "P0000") -> Dict[str, Any]:
        """
        Add DTC that enables start-ready mode
        """
        if dtc_code not in self.ecu_state["dtc_codes"]:
            self.ecu_state["dtc_codes"].append({
                "code": dtc_code,
                "description": "Start Ready Enable Code",
                "status": "active",
                "severity": "info"
            })

        self.ecu_state["start_ready"] = True

        return {
            "success": True,
            "dtc_added": dtc_code,
            "start_ready_enabled": True,
            "operation": "dtc_injection"
        }

    def flash_ecu_memory(self, data: bytes, address: int = 0x0000) -> Dict[str, Any]:
        """
        Simulate ECU flash memory programming
        """
        if self.ecu_state["programming_session"] != "active":
            return {"success": False, "error": "Programming session not active"}

        # Simulate flash operation
        checksum = sum(data) & 0xFFFF
        flash_id = f"flash_{address:04X}"

        self.ecu_state["flash_memory"][flash_id] = {
            "data": data.hex(),
            "address": address,
            "size": len(data),
            "checksum": f"0x{checksum:04X}",
            "programmed_at": datetime.now().isoformat()
        }

        return {
            "success": True,
            "operation": "flash_write",
            "address": f"0x{address:04X}",
            "size": len(data),
            "checksum": f"0x{checksum:04X}",
            "verification": "passed"
        }

    def read_ecu_memory(self, address: int, length: int) -> Dict[str, Any]:
        """
        Simulate ECU memory reading
        """
        flash_id = f"flash_{address:04X}"

        if flash_id in self.ecu_state["flash_memory"]:
            stored_data = self.ecu_state["flash_memory"][flash_id]
            return {
                "success": True,
                "address": f"0x{address:04X}",
                "data": stored_data["data"],
                "length": stored_data["size"],
                "checksum": stored_data["checksum"]
            }
        else:
            # Return mock data
            mock_data = bytes([random.randint(0, 255) for _ in range(length)])
            return {
                "success": True,
                "address": f"0x{address:04X}",
                "data": mock_data.hex(),
                "length": length,
                "source": "mock_generated"
            }

    def get_ecu_status(self) -> Dict[str, Any]:
        """Get comprehensive ECU status"""
        return {
            "ecu_info": {
                "brand": self.brand,
                "model": self.model,
                "state": self.ecu_state.copy()
            },
            "diagnostics": self._get_readiness_diagnostics(),
            "capabilities": [
                "security_access",
                "flash_programming",
                "parameter_modification",
                "dtc_management",
                "file_import_export"
            ]
        }

    def reset_ecu(self) -> bool:
        """Reset ECU to default state"""
        self.ecu_state = {
            "power_status": "off",
            "communication_status": "disconnected",
            "security_access": "locked",
            "programming_session": "inactive",
            "start_ready": False,
            "immo_status": "active",
            "flash_memory": {},
            "dtc_codes": [],
            "parameters": {},
            "file_imports": []
        }
        return True