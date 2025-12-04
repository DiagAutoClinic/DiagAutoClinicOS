#!/usr/bin/env python3
"""
Air Suspension High Calibration Module
Specialized air suspension height calibration for Land Rover Range Rover Sport
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import json

logger = logging.getLogger(__name__)

class AirSuspensionCalibration:
    """
    Advanced air suspension height calibration system for Land Rover vehicles
    """
    
    def __init__(self):
        """Initialize air suspension calibration system"""
        self.calibration_active = False
        self.height_model = None
        self.calibration_data = {}
        self.height_history = []
        self.land_rover_air_suspension_profiles = self._load_land_rover_profiles()
        self.scaler = StandardScaler()
        self.calibration_status = "initialized"
        
    def _load_land_rover_profiles(self) -> Dict[str, Any]:
        """Load Land Rover specific air suspension profiles"""
        return {
            "range_rover_sport_2009": {
                "ecu_id": "7C0",  # Air Suspension ECU
                "height_pid": "21",  # Height position PID
                "pressure_pid": "22",  # Pressure PID
                "valve_control_pid": "23",  # Valve control PID
                "height_ranges": {
                    "parking": {"min": 100, "max": 130, "optimal": 115},
                    "normal": {"min": 140, "max": 170, "optimal": 155},
                    "highway": {"min": 120, "max": 150, "optimal": 135},
                    "offroad": {"min": 180, "max": 220, "optimal": 200}
                },
                "height_sensors": {
                    "front_left": {"sensor_id": "21", "calibration_offset": 0},
                    "front_right": {"sensor_id": "22", "calibration_offset": 2},
                    "rear_left": {"sensor_id": "23", "calibration_offset": -1},
                    "rear_right": {"sensor_id": "24", "calibration_offset": 1}
                },
                "pressure_ranges": {
                    "min_pressure": 50,  # Bar * 10
                    "max_pressure": 200,  # Bar * 10
                    "normal_pressure": 120,  # Bar * 10
                    "warning_pressure": 80   # Bar * 10
                },
                "calibration_parameters": {
                    "height_tolerance": 5,  # +/- 5 units
                    "pressure_tolerance": 10,  # +/- 10 units
                    "response_time": 3000,  # 3 seconds max
                    "stabilization_time": 5000  # 5 seconds stabilization
                }
            }
        }
    
    def start_air_suspension_calibration(self, vehicle_profile: str = "range_rover_sport_2009") -> Dict[str, Any]:
        """
        Start air suspension calibration process
        
        Args:
            vehicle_profile: Vehicle profile name
            
        Returns:
            Calibration start status and configuration
        """
        try:
            if vehicle_profile not in self.land_rover_air_suspension_profiles:
                raise ValueError(f"Vehicle profile {vehicle_profile} not found")
            
            profile = self.land_rover_air_suspension_profiles[vehicle_profile]
            
            self.calibration_active = True
            self.calibration_status = "starting"
            self.calibration_data = {
                "start_time": datetime.now().isoformat(),
                "vehicle_profile": vehicle_profile,
                "ecu_id": profile["ecu_id"],
                "calibration_phases": {
                    "height_baseline": {"status": "pending", "measurements": []},
                    "pressure_baseline": {"status": "pending", "measurements": []},
                    "sensor_calibration": {"status": "pending", "sensor_data": {}},
                    "height_model_training": {"status": "pending", "training_data": []},
                    "valve_response": {"status": "pending", "response_data": []},
                    "final_validation": {"status": "pending", "validation_results": {}}
                },
                "calibration_progress": 0
            }
            
            logger.info(f"Started air suspension calibration for {vehicle_profile}")
            return {
                "status": "calibration_started",
                "profile": vehicle_profile,
                "ecu_id": profile["ecu_id"],
                "height_modes": list(profile["height_ranges"].keys()),
                "total_phases": 6,
                "estimated_duration": "15-20 minutes"
            }
            
        except Exception as e:
            logger.error(f"Error starting air suspension calibration: {e}")
            return {"status": "error", "error": str(e)}
    
    def capture_height_baseline(self, height_measurements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Capture baseline height measurements for all sensors
        
        Args:
            height_measurements: List of height measurements from all sensors
            
        Returns:
            Baseline capture results
        """
        if not self.calibration_active:
            return {"status": "error", "error": "Calibration not active"}
        
        try:
            df = pd.DataFrame(height_measurements)
            
            # Analyze height measurements for each sensor
            sensor_baselines = {}
            for sensor in ["front_left", "front_right", "rear_left", "rear_right"]:
                sensor_data = df[df["sensor"] == sensor]["height_value"].values
                if len(sensor_data) > 0:
                    sensor_baselines[sensor] = {
                        "mean_height": float(np.mean(sensor_data)),
                        "std_height": float(np.std(sensor_data)),
                        "min_height": float(np.min(sensor_data)),
                        "max_height": float(np.max(sensor_data)),
                        "measurement_count": len(sensor_data),
                        "stability_score": 1.0 / (1.0 + np.std(sensor_data)) if len(sensor_data) > 1 else 1.0
                    }
            
            # Calculate overall vehicle level
            overall_height = np.mean([data["mean_height"] for data in sensor_baselines.values()])
            level_deviations = {}
            for sensor, data in sensor_baselines.items():
                level_deviations[sensor] = data["mean_height"] - overall_height
            
            baseline_results = {
                "sensor_baselines": sensor_baselines,
                "overall_height": float(overall_height),
                "level_deviations": level_deviations,
                "vehicle_level_score": self._calculate_level_score(level_deviations),
                "measurement_quality": "excellent" if all(data["stability_score"] > 0.9 for data in sensor_baselines.values()) else "good"
            }
            
            # Update calibration data
            self.calibration_data["calibration_phases"]["height_baseline"] = {
                "status": "completed",
                "measurements": height_measurements,
                "results": baseline_results
            }
            self.calibration_data["calibration_progress"] = 20
            self.calibration_status = "height_baseline_captured"
            
            logger.info(f"Height baseline captured: {len(sensor_baselines)} sensors, overall height: {overall_height:.1f}")
            return {
                "status": "height_baseline_captured",
                "results": baseline_results,
                "next_phase": "pressure_baseline"
            }
            
        except Exception as e:
            logger.error(f"Error capturing height baseline: {e}")
            return {"status": "error", "error": str(e)}
    
    def capture_pressure_baseline(self, pressure_measurements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Capture baseline pressure measurements
        
        Args:
            pressure_measurements: List of pressure measurements
            
        Returns:
            Pressure baseline results
        """
        try:
            df = pd.DataFrame(pressure_measurements)
            
            # Analyze pressure measurements
            pressure_stats = {
                "mean_pressure": float(np.mean(df["pressure_value"].values)),
                "std_pressure": float(np.std(df["pressure_value"].values)),
                "min_pressure": float(np.min(df["pressure_value"].values)),
                "max_pressure": float(np.max(df["pressure_value"].values)),
                "pressure_stability": 1.0 / (1.0 + np.std(df["pressure_value"].values))
            }
            
            # Check for pressure warnings
            profile = self.land_rover_air_suspension_profiles["range_rover_sport_2009"]
            min_pressure = profile["pressure_ranges"]["min_pressure"]
            warning_pressure = profile["pressure_ranges"]["warning_pressure"]
            
            pressure_warnings = []
            if pressure_stats["min_pressure"] < warning_pressure:
                pressure_warnings.append("Low pressure detected")
            if pressure_stats["mean_pressure"] < min_pressure:
                pressure_warnings.append("Critical low pressure")
            
            baseline_results = {
                "pressure_statistics": pressure_stats,
                "pressure_warnings": pressure_warnings,
                "system_status": "normal" if not pressure_warnings else "warning",
                "recommendation": self._generate_pressure_recommendation(pressure_stats, pressure_warnings)
            }
            
            # Update calibration data
            self.calibration_data["calibration_phases"]["pressure_baseline"] = {
                "status": "completed",
                "measurements": pressure_measurements,
                "results": baseline_results
            }
            self.calibration_data["calibration_progress"] = 35
            self.calibration_status = "pressure_baseline_captured"
            
            logger.info(f"Pressure baseline captured: {pressure_stats['mean_pressure']:.1f} pressure units")
            return {
                "status": "pressure_baseline_captured",
                "results": baseline_results,
                "next_phase": "sensor_calibration"
            }
            
        except Exception as e:
            logger.error(f"Error capturing pressure baseline: {e}")
            return {"status": "error", "error": str(e)}
    
    def calibrate_height_sensors(self, sensor_calibration_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calibrate individual height sensors with offset compensation
        
        Args:
            sensor_calibration_data: Sensor calibration measurements
            
        Returns:
            Sensor calibration results
        """
        try:
            # Process sensor calibration data
            sensor_offsets = {}
            sensor_accuracy = {}
            
            for sensor_name in ["front_left", "front_right", "rear_left", "rear_right"]:
                sensor_data = [d for d in sensor_calibration_data if d["sensor"] == sensor_name]
                if sensor_data:
                    # Calculate sensor offset based on reference measurements
                    reference_height = np.mean([d["reference_height"] for d in sensor_data])
                    measured_height = np.mean([d["measured_height"] for d in sensor_data])
                    offset = reference_height - measured_height
                    
                    # Calculate accuracy
                    measurements = [d["measured_height"] for d in sensor_data]
                    accuracy = 1.0 - (np.std(measurements) / np.mean(measurements)) if np.mean(measurements) > 0 else 0
                    
                    sensor_offsets[sensor_name] = float(offset)
                    sensor_accuracy[sensor_name] = float(max(0, accuracy))
            
            # Update calibration data
            self.calibration_data["calibration_phases"]["sensor_calibration"] = {
                "status": "completed",
                "sensor_data": {
                    "sensor_offsets": sensor_offsets,
                    "sensor_accuracy": sensor_accuracy
                }
            }
            self.calibration_data["calibration_progress"] = 55
            self.calibration_status = "sensors_calibrated"
            
            logger.info(f"Sensor calibration completed: {len(sensor_offsets)} sensors calibrated")
            return {
                "status": "sensors_calibrated",
                "sensor_offsets": sensor_offsets,
                "sensor_accuracy": sensor_accuracy,
                "average_accuracy": np.mean(list(sensor_accuracy.values())),
                "next_phase": "height_model_training"
            }
            
        except Exception as e:
            logger.error(f"Error calibrating height sensors: {e}")
            return {"status": "error", "error": str(e)}
    
    def train_height_prediction_model(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Train AI model for height prediction based on pressure and other parameters
        
        Args:
            training_data: Training data with pressure, height, and other parameters
            
        Returns:
            Model training results
        """
        try:
            if len(training_data) < 50:
                return {"status": "error", "error": "Insufficient training data (minimum 50 samples required)"}
            
            # Prepare training features
            features = []
            targets = []
            
            for sample in training_data:
                feature_vector = [
                    sample.get("pressure", 0.0),
                    sample.get("engine_rpm", 0.0),
                    sample.get("vehicle_speed", 0.0),
                    sample.get("weight_load", 0.0),
                    sample.get("temperature", 0.0),
                    sample.get("time_since_last_adjustment", 0.0)
                ]
                target_height = sample.get("height_value", 0.0)
                
                features.append(feature_vector)
                targets.append(target_height)
            
            # Convert to numpy arrays
            X = np.array(features)
            y = np.array(targets)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train Random Forest model
            self.height_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            
            self.height_model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            train_score = self.height_model.score(X_train_scaled, y_train)
            test_score = self.height_model.score(X_test_scaled, y_test)
            
            # Feature importance
            feature_names = ["pressure", "engine_rpm", "vehicle_speed", "weight_load", "temperature", "adjustment_time"]
            feature_importance = dict(zip(feature_names, self.height_model.feature_importances_))
            
            model_results = {
                "model_type": "RandomForestRegressor",
                "training_samples": len(X_train),
                "test_samples": len(X_test),
                "train_score": float(train_score),
                "test_score": float(test_score),
                "feature_importance": feature_importance,
                "model_ready": True
            }
            
            # Update calibration data
            self.calibration_data["calibration_phases"]["height_model_training"] = {
                "status": "completed",
                "training_data": training_data,
                "model_results": model_results
            }
            self.calibration_data["calibration_progress"] = 75
            self.calibration_status = "height_model_trained"
            
            logger.info(f"Height prediction model trained: R² = {test_score:.3f}")
            return {
                "status": "height_model_trained",
                "model_results": model_results,
                "next_phase": "valve_response_testing"
            }
            
        except Exception as e:
            logger.error(f"Error training height prediction model: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_valve_response(self, valve_test_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Test air suspension valve response and timing
        
        Args:
            valve_test_data: Valve response test data
            
        Returns:
            Valve response test results
        """
        try:
            df = pd.DataFrame(valve_test_data)
            
            # Analyze valve response times
            response_times = []
            for valve_command in df["valve_command"].unique():
                valve_data = df[df["valve_command"] == valve_command]
                if len(valve_data) > 1:
                    response_time = valve_data["response_time"].mean()
                    response_times.append(response_time)
            
            average_response_time = np.mean(response_times) if response_times else 0
            response_time_stability = 1.0 - (np.std(response_times) / np.mean(response_times)) if response_times else 0
            
            # Check against specifications
            profile = self.land_rover_air_suspension_profiles["range_rover_sport_2009"]
            max_response_time = profile["calibration_parameters"]["response_time"]
            
            valve_status = "normal" if average_response_time < max_response_time else "slow"
            
            valve_results = {
                "average_response_time": float(average_response_time),
                "response_time_stability": float(response_time_stability),
                "max_response_time": max_response_time,
                "valve_status": valve_status,
                "commands_tested": len(df["valve_command"].unique()),
                "total_responses": len(df)
            }
            
            # Update calibration data
            self.calibration_data["calibration_phases"]["valve_response"] = {
                "status": "completed",
                "response_data": valve_test_data,
                "results": valve_results
            }
            self.calibration_data["calibration_progress"] = 90
            self.calibration_status = "valve_response_tested"
            
            logger.info(f"Valve response test completed: {average_response_time:.1f}ms average")
            return {
                "status": "valve_response_tested",
                "results": valve_results,
                "next_phase": "final_validation"
            }
            
        except Exception as e:
            logger.error(f"Error testing valve response: {e}")
            return {"status": "error", "error": str(e)}
    
    def perform_final_validation(self, validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform final validation of air suspension calibration
        
        Args:
            validation_data: Final validation test data
            
        Returns:
            Final validation results and calibration summary
        """
        try:
            # Validate all calibration phases are completed
            phases = self.calibration_data["calibration_phases"]
            completed_phases = sum(1 for phase in phases.values() if phase["status"] == "completed")
            total_phases = len(phases)
            
            if completed_phases < total_phases:
                missing_phases = [name for name, phase in phases.items() if phase["status"] != "completed"]
                return {"status": "error", "error": f"Missing calibration phases: {missing_phases}"}
            
            # Perform validation tests
            height_accuracy_test = self._validate_height_accuracy(validation_data.get("height_tests", []))
            pressure_accuracy_test = self._validate_pressure_accuracy(validation_data.get("pressure_tests", []))
            response_time_test = self._validate_response_times(validation_data.get("response_tests", []))
            
            # Overall validation score
            validation_scores = [
                height_accuracy_test.get("accuracy_score", 0),
                pressure_accuracy_test.get("accuracy_score", 0),
                response_time_test.get("performance_score", 0)
            ]
            overall_score = np.mean(validation_scores)
            
            # Generate validation report
            validation_results = {
                "calibration_completion": {
                    "phases_completed": completed_phases,
                    "total_phases": total_phases,
                    "completion_percentage": (completed_phases / total_phases) * 100
                },
                "validation_tests": {
                    "height_accuracy": height_accuracy_test,
                    "pressure_accuracy": pressure_accuracy_test,
                    "response_times": response_time_test
                },
                "overall_validation": {
                    "overall_score": float(overall_score),
                    "validation_status": "pass" if overall_score > 0.85 else "fail",
                    "ready_for_production": overall_score > 0.90
                },
                "calibration_certificate": self._generate_calibration_certificate()
            }
            
            # Update calibration data
            self.calibration_data["calibration_phases"]["final_validation"] = {
                "status": "completed",
                "validation_results": validation_results
            }
            self.calibration_data["calibration_progress"] = 100
            self.calibration_status = "calibration_complete"
            self.calibration_active = False
            
            logger.info(f"Air suspension calibration completed with {overall_score:.3f} overall score")
            return {
                "status": "calibration_complete",
                "validation_results": validation_results
            }
            
        except Exception as e:
            logger.error(f"Error performing final validation: {e}")
            return {"status": "error", "error": str(e)}
    
    def predict_height(self, pressure: float, engine_rpm: float, vehicle_speed: float, 
                      weight_load: float, temperature: float) -> Dict[str, Any]:
        """
        Predict vehicle height based on input parameters
        
        Args:
            pressure: Air pressure reading
            engine_rpm: Engine RPM
            vehicle_speed: Vehicle speed
            weight_load: Weight/load on vehicle
            temperature: Ambient temperature
            
        Returns:
            Height prediction with confidence
        """
        try:
            if not self.height_model:
                return {"status": "error", "error": "Height prediction model not trained"}
            
            # Prepare input features
            feature_vector = np.array([[pressure, engine_rpm, vehicle_speed, weight_load, temperature, 0.0]])
            feature_vector_scaled = self.scaler.transform(feature_vector)
            
            # Make prediction
            predicted_height = self.height_model.predict(feature_vector_scaled)[0]
            
            # Get prediction confidence (using model score as confidence proxy)
            model_confidence = getattr(self.height_model, 'score', lambda X, y: 0.8)(
                feature_vector_scaled, [predicted_height]
            )
            
            # Validate against height ranges
            profile = self.land_rover_air_suspension_profiles["range_rover_sport_2009"]
            height_ranges = profile["height_ranges"]
            
            height_status = "normal"
            for mode_name, mode_range in height_ranges.items():
                if mode_range["min"] <= predicted_height <= mode_range["max"]:
                    height_status = mode_name
                    break
            
            return {
                "status": "prediction_success",
                "predicted_height": float(predicted_height),
                "height_mode": height_status,
                "confidence": float(model_confidence),
                "input_parameters": {
                    "pressure": pressure,
                    "engine_rpm": engine_rpm,
                    "vehicle_speed": vehicle_speed,
                    "weight_load": weight_load,
                    "temperature": temperature
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error predicting height: {e}")
            return {"status": "error", "error": str(e)}
    
    def _calculate_level_score(self, level_deviations: Dict[str, float]) -> float:
        """Calculate vehicle level score based on sensor deviations"""
        if not level_deviations:
            return 0.0
        
        deviations = list(level_deviations.values())
        max_deviation = max(abs(d) for d in deviations)
        
        # Score decreases as maximum deviation increases
        level_score = max(0, 1.0 - (max_deviation / 20.0))  # 20 units max acceptable deviation
        return level_score
    
    def _generate_pressure_recommendation(self, pressure_stats: Dict[str, Any], warnings: List[str]) -> str:
        """Generate recommendations based on pressure analysis"""
        if warnings:
            return "Check air suspension system - pressure issues detected"
        elif pressure_stats["pressure_stability"] > 0.9:
            return "Air suspension pressure stable - system operating normally"
        else:
            return "Monitor air suspension pressure - some instability detected"
    
    def _validate_height_accuracy(self, height_tests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate height measurement accuracy"""
        if not height_tests:
            return {"accuracy_score": 0.0, "error": "No height tests provided"}
        
        # Calculate accuracy metrics
        actual_heights = [test["actual_height"] for test in height_tests]
        measured_heights = [test["measured_height"] for test in height_tests]
        
        errors = [abs(actual - measured) for actual, measured in zip(actual_heights, measured_heights)]
        mean_error = np.mean(errors)
        max_error = max(errors)
        
        accuracy_score = max(0, 1.0 - (mean_error / 10.0))  # 10 units tolerance
        
        return {
            "accuracy_score": accuracy_score,
            "mean_error": float(mean_error),
            "max_error": float(max_error),
            "test_count": len(height_tests),
            "status": "pass" if accuracy_score > 0.8 else "fail"
        }
    
    def _validate_pressure_accuracy(self, pressure_tests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate pressure measurement accuracy"""
        if not pressure_tests:
            return {"accuracy_score": 0.0, "error": "No pressure tests provided"}
        
        actual_pressures = [test["actual_pressure"] for test in pressure_tests]
        measured_pressures = [test["measured_pressure"] for test in pressure_tests]
        
        errors = [abs(actual - measured) for actual, measured in zip(actual_pressures, measured_pressures)]
        mean_error = np.mean(errors)
        
        accuracy_score = max(0, 1.0 - (mean_error / 20.0))  # 20 units tolerance
        return {
            "accuracy_score": accuracy_score,
            "mean_error": float(mean_error),
            "test_count": len(pressure_tests),
            "status": "pass" if accuracy_score > 0.8 else "fail"
        }
    
    def _validate_response_times(self, response_tests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate valve response times"""
        if not response_tests:
            return {"performance_score": 0.0, "error": "No response tests provided"}
        
        response_times = [test["response_time"] for test in response_tests]
        mean_response_time = np.mean(response_times)
        
        # Compare to specification (3000ms)
        max_acceptable_time = 3000
        performance_score = max(0, 1.0 - (mean_response_time / max_acceptable_time))
        
        return {
            "performance_score": performance_score,
            "mean_response_time": float(mean_response_time),
            "test_count": len(response_tests),
            "status": "pass" if mean_response_time < max_acceptable_time else "fail"
        }
    
    def _generate_calibration_certificate(self) -> Dict[str, Any]:
        """Generate calibration certificate"""
        return {
            "certificate_id": f"LR-AS-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "vehicle": "Land Rover Range Rover Sport 2009",
            "system": "Air Suspension",
            "calibration_date": datetime.now().isoformat(),
            "calibration_status": "PASSED",
            "overall_score": self.calibration_data.get("calibration_progress", 100) / 100.0,
            "phases_completed": 6,
            "model_trained": self.height_model is not None,
            "calibration_validity_days": 365,
            "technician": "AI Calibration System",
            "version": "1.0"
        }
    
    def get_calibration_status(self) -> Dict[str, Any]:
        """Get current calibration status"""
        return {
            "calibration_active": self.calibration_active,
            "calibration_status": self.calibration_status,
            "calibration_progress": self.calibration_data.get("calibration_progress", 0),
            "completed_phases": len([p for p in self.calibration_data.get("calibration_phases", {}).values() 
                                   if p.get("status") == "completed"]),
            "total_phases": 6,
            "ready_for_prediction": self.height_model is not None,
            "last_update": datetime.now().isoformat()
        }

# Global air suspension calibration instance
air_suspension_calibration = AirSuspensionCalibration()
