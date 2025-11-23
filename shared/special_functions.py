#!/usr/bin/env python3

import logging
import re
import time
from typing import Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

class FunctionCategory(Enum):
    ADAPTATION = "adaptation"
    CALIBRATION = "calibration" 
    PROGRAMMING = "programming"
    SECURITY = "security"
    MAINTENANCE = "maintenance"
    DIAGNOSTIC = "diagnostic"

class EnhancedSpecialFunction:
    """Enhanced special function with comprehensive security"""
    
    def __init__(self, function_id: str, name: str, category: FunctionCategory, 
                 description: str, security_level: int, brand: str):
        self.function_id = function_id
        self.name = name
        self.category = category
        self.description = description
        self.security_level = security_level
        self.brand = brand
        self.parameters = {}
        self.prerequisites = []
        self.risks = []
        
    def add_parameter(self, name: str, param_type: str, required: bool = True, 
                     validation: str = None):
        self.parameters[name] = {
            'type': param_type, 
            'required': required,
            'validation': validation
        }
    
    def add_prerequisite(self, prerequisite: str):
        self.prerequisites.append(prerequisite)
        
    def add_risk(self, risk: str):
        self.risks.append(risk)

class EnhancedSpecialFunctionsManager:
    """Enhanced manager with comprehensive security and 25-brand support"""
    
    def __init__(self):
        self.functions_db = self._initialize_enhanced_functions_database()
        self.security_manager = None
        self.audit_log = []
        
    def _initialize_enhanced_functions_database(self) -> Dict[str, List[EnhancedSpecialFunction]]:
        """Initialize comprehensive functions database for 25 brands"""
        
        functions_db = {}
        
        # Toyota/Lexus (Enhanced)
        functions_db['Toyota'] = self._create_toyota_functions()
        functions_db['Lexus'] = self._create_lexus_functions()
        
        # Volkswagen Group
        functions_db['Volkswagen'] = self._create_volkswagen_functions()
        functions_db['Audi'] = self._create_audi_functions()
        functions_db['Skoda'] = self._create_skoda_functions()
        functions_db['Seat'] = self._create_seat_functions()
        
        # BMW Group
        functions_db['BMW'] = self._create_bmw_functions()
        functions_db['Mini'] = self._create_mini_functions()
        
        # Mercedes-Benz
        functions_db['Mercedes-Benz'] = self._create_mercedes_functions()
        
        # Ford Group
        functions_db['Ford'] = self._create_ford_functions()
        functions_db['Lincoln'] = self._create_lincoln_functions()
        
        # GM Group
        functions_db['Chevrolet'] = self._create_chevrolet_functions()
        functions_db['Cadillac'] = self._create_cadillac_functions()
        functions_db['GMC'] = self._create_gmc_functions()
        functions_db['Buick'] = self._create_buick_functions()
        
        # Hyundai-Kia
        functions_db['Hyundai'] = self._create_hyundai_functions()
        functions_db['Kia'] = self._create_kia_functions()
        
        # Stellantis
        functions_db['Jeep'] = self._create_jeep_functions()
        functions_db['Chrysler'] = self._create_chrysler_functions()
        functions_db['Dodge'] = self._create_dodge_functions()
        functions_db['Ram'] = self._create_ram_functions()
        
        # Japanese
        functions_db['Honda'] = self._create_honda_functions()
        functions_db['Nissan'] = self._create_nissan_functions()
        functions_db['Mazda'] = self._create_mazda_functions()
        functions_db['Subaru'] = self._create_subaru_functions()
        functions_db['Mitsubishi'] = self._create_mitsubishi_functions()
        
        # European
        functions_db['Volvo'] = self._create_volvo_functions()
        functions_db['Porsche'] = self._create_porsche_functions()
        functions_db['Jaguar'] = self._create_jaguar_functions()
        functions_db['Land Rover'] = self._create_landrover_functions()
        
        return functions_db
    
    def _create_toyota_functions(self) -> List[EnhancedSpecialFunction]:
        """Create Toyota special functions"""
        functions = []
        
        # Throttle Body Learning
        func = EnhancedSpecialFunction(
            "toyota_throttle_learn", 
            "Throttle Body Learning", 
            FunctionCategory.ADAPTATION,
            "Performs throttle body position learning and reset after cleaning or replacement",
            2, "Toyota"
        )
        func.add_parameter("engine_temperature", "int", True, "70-105")
        func.add_parameter("ignition_on", "bool", True)
        func.add_parameter("throttle_clean", "bool", False)
        func.add_prerequisite("Engine at operating temperature")
        func.add_prerequisite("Battery voltage > 12.5V")
        func.add_prerequisite("All electrical loads OFF")
        func.add_risk("Incorrect adaptation may cause poor idle quality")
        functions.append(func)
        
        # Immobilizer Registration
        func = EnhancedSpecialFunction(
            "toyota_immobilizer_reg", 
            "Immobilizer Registration", 
            FunctionCategory.SECURITY,
            "Register new keys to immobilizer system - requires security access",
            5, "Toyota"
        )
        func.add_parameter("key_count", "int", True, "1-8")
        func.add_parameter("security_code", "string", True)
        func.add_prerequisite("All keys present")
        func.add_prerequisite("Security code available")
        func.add_prerequisite("Stable power supply")
        func.add_risk("Vehicle may become immobilized if procedure fails")
        functions.append(func)
        
        # Steering Angle Calibration
        func = EnhancedSpecialFunction(
            "toyota_steering_angle", 
            "Steering Angle Sensor Calibration", 
            FunctionCategory.CALIBRATION,
            "Reset and calibrate steering angle sensor after alignment or sensor replacement",
            3, "Toyota"
        )
        func.add_parameter("wheel_alignment_done", "bool", True)
        func.add_prerequisite("Wheel alignment completed")
        func.add_prerequisite("Steering wheel centered")
        func.add_prerequisite("Vehicle on level surface")
        functions.append(func)
        
        return functions

    def _create_lexus_functions(self) -> List[EnhancedSpecialFunction]:
        """Create Lexus special functions"""
        functions = []
        
        # Throttle Body Learning
        func = EnhancedSpecialFunction(
            "lexus_throttle_learn", 
            "Throttle Body Learning", 
            FunctionCategory.ADAPTATION,
            "Performs throttle body position learning and reset after cleaning or replacement",
            2, "lexus"
        )
        func.add_parameter("engine_temperature", "int", True, "70-105")
        func.add_parameter("ignition_on", "bool", True)
        func.add_parameter("throttle_clean", "bool", False)
        func.add_prerequisite("Engine at operating temperature")
        func.add_prerequisite("Battery voltage > 12.5V")
        func.add_prerequisite("All electrical loads OFF")
        func.add_risk("Incorrect adaptation may cause poor idle quality")
        functions.append(func)
        
        # Immobilizer Registration
        func = EnhancedSpecialFunction(
            "Lexus_immobilizer_reg", 
            "Immobilizer Registration", 
            FunctionCategory.SECURITY,
            "Register new keys to immobilizer system - requires security access",
            5, "Lexus"
        )
        func.add_parameter("key_count", "int", True, "1-8")
        func.add_parameter("security_code", "string", True)
        func.add_prerequisite("All keys present")
        func.add_prerequisite("Security code available")
        func.add_prerequisite("Stable power supply")
        func.add_risk("Vehicle may become immobilized if procedure fails")
        functions.append(func)
        
        # Steering Angle Calibration
        func = EnhancedSpecialFunction(
            "lexus_steering_angle", 
            "Steering Angle Sensor Calibration", 
            FunctionCategory.CALIBRATION,
            "Reset and calibrate steering angle sensor after alignment or sensor replacement",
            3, "Toyota"
        )
        func.add_parameter("wheel_alignment_done", "bool", True)
        func.add_prerequisite("Wheel alignment completed")
        func.add_prerequisite("Steering wheel centered")
        func.add_prerequisite("Vehicle on level surface")
        functions.append(func)
        
        return functions
    
    def _create_volkswagen_functions(self) -> List[EnhancedSpecialFunction]:
        """Create Volkswagen special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "vw_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "Volkswagen"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "vw_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "Volkswagen"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions

    def _create_audi_functions(self) -> List[EnhancedSpecialFunction]:
        """Create Audi special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "audi_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "Audi"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "audi_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "Audi"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions    
    
    def _create_skoda_functions(self) -> List[EnhancedSpecialFunction]:
        """Create Skoda special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "sko_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "Skoda"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "sko_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "Skoda"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions    

    def _create_seat_functions(self) -> List[EnhancedSpecialFunction]:
        """Create Seat special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "vw_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "Seat"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "vw_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "Seat"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions    

    def _create_bmw_functions(self) -> List[EnhancedSpecialFunction]:
        """Create BMW special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "bmw_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "BMW"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "bmw_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "BMW"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions    

    def _create_mini_functions(self) -> List[EnhancedSpecialFunction]:
        """Create Mini special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "mini_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "Mini"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "mini_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "Mini"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions    

    def _create_mercedes_functions(self) -> List[EnhancedSpecialFunction]:
        """Create Mercedes-Benz special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "mb_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "Mercedes-Benz"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "mb_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "Mercedes-Benz"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions    

    def _create_ford_functions(self) -> List[EnhancedSpecialFunction]:
        """Create Ford special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "ford_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "Ford"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "ford_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "Ford"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions    

    def _create_lincoln_functions(self) -> List[EnhancedSpecialFunction]:
        """Create Lincoln special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "lincoln_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "Lincoln"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "lincoln_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "Lincoln"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions    

    def _create_chevrolet_functions(self) -> List[EnhancedSpecialFunction]:
        """Create Chevrolet special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "chev_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "Chevrolet"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "chev_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "Chevrolet"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions    

    def _create_cadillac_functions(self) -> List[EnhancedSpecialFunction]:
        """Create Cadillac special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "cadi_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "Cadillac"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "cadi_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "Cadillac"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions    

    def _create_gmc_functions(self) -> List[EnhancedSpecialFunction]:
        """Create GMC special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "gmc_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "GMC"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "gmc_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "GMC"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions    

    def _create_buick_functions(self) -> List[EnhancedSpecialFunction]:
        """Create Buick special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "bck_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "Buick"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "bck_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "Buick"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions    

    def _create_hyundai_functions(self) -> List[EnhancedSpecialFunction]:
        """Create Hyundai special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "hyu_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "Hyundai"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "hyu_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "Hyundai"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions    

    def _create_kia_functions(self) -> List[EnhancedSpecialFunction]:
        """Create Kia special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "kia_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "Kia"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "kia_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "Kia"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions    

    def _create_jeep_functions(self) -> List[EnhancedSpecialFunction]:
        """Create Jeep special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "jeep_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "Jeep"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "jeep_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "Jeep"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions    

    def _create_chrysler_functions(self) -> List[EnhancedSpecialFunction]:
        """Create Chrysler special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "cys_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "Chrysler"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "cys_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "Chrysler"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions    

    def _create_dodge_functions(self) -> List[EnhancedSpecialFunction]:
        """Create Dodge special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "dod_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "Dodge"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "dod_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "Dodge"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions    

    def _create_ram_functions(self) -> List[EnhancedSpecialFunction]:
        """Create RAM special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "ram_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "RAM"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "ram_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "RAM"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions    

    def _create_honda_functions(self) -> List[EnhancedSpecialFunction]:
        """Create Honda special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "hda_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "Honda"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "hda_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "Honda"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions    

    def _create_nissan_functions(self) -> List[EnhancedSpecialFunction]:
        """Create Audi special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "nsn_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "Nissan"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "nsn_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "Nissan"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions    

    def _create_mazda_functions(self) -> List[EnhancedSpecialFunction]:
        """Create Mazda special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "mza_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "Mazda"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "mza_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "Mazda"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions    

    def _create_subaru_functions(self) -> List[EnhancedSpecialFunction]:
        """Create Subaru special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "sub_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "Subaru"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "sub_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "Subaru"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions    

    def _create_mitsubishi_functions(self) -> List[EnhancedSpecialFunction]:
        """Create Mitsubishi special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "mit_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "Mitsubishi"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "mit_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "Mitsubishi"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions

    def _create_volvo_functions(self) -> List[EnhancedSpecialFunction]:
        """Create Volvo special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "vol_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "Volvo"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "vol_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "Volvo"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions    

    def _create_porsche_functions(self) -> List[EnhancedSpecialFunction]:
        """Create Porsche special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "psc_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "Porsche"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "psc_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "Porsche"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions    

    def _create_jaguar_functions(self) -> List[EnhancedSpecialFunction]:
        """Create Jaguar special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "jag_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "Jaguar"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "jag_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "Jaguar"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions    

    def _create_landrover_functions(self) -> List[EnhancedSpecialFunction]:
        """Create Land Rover special functions"""
        functions = []
        
        # DPF Regeneration
        func = EnhancedSpecialFunction(
            "jlr_dpf_regeneration", 
            "DPF Forced Regeneration", 
            FunctionCategory.MAINTENANCE,
            "Force diesel particulate filter regeneration when automatic regeneration fails",
            4, "Land Rover"
        )
        func.add_parameter("engine_temperature", "int", True, "80-100")
        func.add_parameter("vehicle_stationary", "bool", True)
        func.add_parameter("parking_brake", "bool", True)
        func.add_prerequisite("Adequate fuel level")
        func.add_prerequisite("DPF not physically damaged")
        func.add_prerequisite("No exhaust leaks")
        func.add_risk("High exhaust temperatures - ensure safe working area")
        functions.append(func)
        
        # Throttle Valve Adaptation
        func = EnhancedSpecialFunction(
            "jlr_throttle_adaptation", 
            "Throttle Valve Adaptation", 
            FunctionCategory.ADAPTATION,
            "Basic setting for throttle valve control module",
            3, "Land Rover"
        )
        func.add_parameter("ignition_on", "bool", True)
        func.add_prerequisite("Throttle body clean")
        func.add_prerequisite("No air leaks")
        functions.append(func)
        
        return functions        
    
    def execute_function(self, brand: str, function_id: str, parameters: Dict) -> Dict:
        """Enhanced function execution with comprehensive security"""
        
        # Input validation
        if not brand or not function_id:
            return {"success": False, "error": "Brand and function ID required"}
        
        # Security validation
        if not self.security_manager:
            return {"success": False, "error": "Security manager not configured"}
        
        if not self.security_manager.validate_session():
            return {"success": False, "error": "Session expired - please log in again"}
        
        function = self.get_function(brand, function_id)
        if not function:
            return {"success": False, "error": "Function not found"}
        
        # Enhanced security level check
        if not self._check_enhanced_security_clearance(function.security_level):
            return {
                "success": False, 
                "error": f"Insufficient security clearance. Required: Level {function.security_level}"
            }
        
        # Parameter validation
        validation_result = self._validate_parameters(function, parameters)
        if not validation_result["valid"]:
            return {"success": False, "error": f"Parameter validation failed: {validation_result['error']}"}
        
        try:
            # Log function execution attempt
            self._log_function_attempt(brand, function_id, parameters)
            
            # Execute the function
            result = self._execute_enhanced_brand_function(brand, function_id, parameters)
            
            # Log successful execution
            self._log_function_success(brand, function_id)
            
            return result
            
        except Exception as e:
            error_msg = f"Function execution failed: {str(e)}"
            logger.error(error_msg)
            self._log_function_failure(brand, function_id, error_msg)
            return {"success": False, "error": error_msg}
    
    def _validate_parameters(self, function: EnhancedSpecialFunction, parameters: Dict) -> Dict:
        """Enhanced parameter validation"""
        missing_params = []
        invalid_params = []
        
        for param_name, param_config in function.parameters.items():
            if param_config['required'] and param_name not in parameters:
                missing_params.append(param_name)
                continue
                
            if param_name in parameters:
                value = parameters[param_name]
                validation = param_config.get('validation')
                
                if validation and not self._validate_parameter_value(value, validation):
                    invalid_params.append(f"{param_name} (validation: {validation})")
        
        if missing_params:
            return {
                "valid": False, 
                "error": f"Missing required parameters: {', '.join(missing_params)}"
            }
            
        if invalid_params:
            return {
                "valid": False,
                "error": f"Invalid parameter values: {', '.join(invalid_params)}"
            }
            
        return {"valid": True}
    
    def _validate_parameter_value(self, value, validation: str) -> bool:
        """Validate parameter value against validation rules"""
        try:
            if validation == "70-105":
                return 70 <= int(value) <= 105
            elif validation == "1-8":
                return 1 <= int(value) <= 8
            # Add more validation rules as needed
            return True
        except (ValueError, TypeError):
            return False
    
    def _check_enhanced_security_clearance(self, required_level: int) -> bool:
        """Enhanced security clearance check"""
        if not self.security_manager:
            return False
            
        current_level = self.security_manager.get_security_level()
        return current_level.value >= required_level
    
    def _log_function_attempt(self, brand: str, function_id: str, parameters: Dict):
        """Log function execution attempt"""
        if self.security_manager and self.security_manager.current_user:
            username = self.security_manager.current_user
            # Mask sensitive parameters
            masked_params = {k: "***" if "code" in k.lower() or "password" in k.lower() else v 
                           for k, v in parameters.items()}
            
            log_entry = {
                'timestamp': time.time(),
                'brand': brand,
                'function_id': function_id,
                'username': username,
                'parameters': masked_params,
                'status': 'attempted'
            }
            self.audit_log.append(log_entry)
    
    def _log_function_success(self, brand: str, function_id: str):
        """Log successful function execution"""
        if self.security_manager and self.security_manager.current_user:
            log_entry = {
                'timestamp': time.time(),
                'brand': brand,
                'function_id': function_id,
                'username': self.security_manager.current_user,
                'status': 'success'
            }
            self.audit_log.append(log_entry)
    
    def _log_function_failure(self, brand: str, function_id: str, error: str):
        """Log function execution failure"""
        if self.security_manager and self.security_manager.current_user:
            log_entry = {
                'timestamp': time.time(),
                'brand': brand,
                'function_id': function_id,
                'username': self.security_manager.current_user,
                'status': 'failed',
                'error': error
            }
            self.audit_log.append(log_entry)

    # Keep existing methods but enhance them...
    def get_brand_functions(self, brand: str) -> List[EnhancedSpecialFunction]:
        return self.functions_db.get(brand, [])
    
    def get_function(self, brand: str, function_id: str) -> Optional[EnhancedSpecialFunction]:
        functions = self.get_brand_functions(brand)
        return next((f for f in functions if f.function_id == function_id), None)

# Enhanced singleton instance
special_functions_manager = EnhancedSpecialFunctionsManager()
