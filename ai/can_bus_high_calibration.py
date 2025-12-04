#!/usr/bin/env python3
"""
CAN Bus High Calibration Module
Advanced CAN bus analysis and calibration for Land Rover diagnostic applications
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
import json

logger = logging.getLogger(__name__)

class CANBusHighCalibration:
    """
    Advanced CAN bus calibration and analysis system
    """
    
    def __init__(self):
        """Initialize high calibration CAN bus analyzer"""
        self.calibration_active = False
        self.baseline_captured = False
        self.calibration_data = {}
        self.land_rover_profiles = self._load_land_rover_profiles()
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.message_classifier = DBSCAN(eps=0.1, min_samples=5)
        self.scaler = StandardScaler()
        
    def _load_land_rover_profiles(self) -> Dict[str, Any]:
        """Load Land Rover specific CAN bus profiles and parameters"""
        return {
            "range_rover_sport_2009": {
                "protocol": "ISO15765-11BIT",
                "baud_rate": 500000,
                "ecu_list": {
                    "7E8": {"name": "Engine ECU", "priority": "high", "messages_per_sec": 15},
                    "7E0": {"name": "Engine ECU Commands", "priority": "high", "messages_per_sec": 12},
                    "760": {"name": "Transmission ECU", "priority": "high", "messages_per_sec": 8},
                    "7A0": {"name": "ABS ECU", "priority": "medium", "messages_per_sec": 6},
                    "740": {"name": "Body ECU", "priority": "medium", "messages_per_sec": 5},
                    "7C0": {"name": "Air Suspension ECU", "priority": "high", "messages_per_sec": 4},
                    "720": {"name": "Instrument Cluster", "priority": "medium", "messages_per_sec": 3},
                    "7E2": {"name": "Diagnostic ECU", "priority": "low", "messages_per_sec": 2},
                    "780": {"name": "Climate Control", "priority": "medium", "messages_per_sec": 3},
                    "7B0": {"name": "Audio System", "priority": "low", "messages_per_sec": 2},
                    "7D0": {"name": "Navigation", "priority": "low", "messages_per_sec": 1},
                    "7F0": {"name": "Security System", "priority": "medium", "messages_per_sec": 2}
                },
                "critical_parameters": {
                    "engine_rpm": {"id": "7E8", "pid": "0C", "range": (0, 8000), "normal": (600, 3500)},
                    "coolant_temp": {"id": "7E8", "pid": "05", "range": (40, 120), "normal": (80, 95)},
                    "throttle_position": {"id": "7E8", "pid": "11", "range": (0, 100), "normal": (0, 20)},
                    "engine_load": {"id": "7E8", "pid": "43", "range": (0, 100), "normal": (10, 40)},
                    "fuel_pressure": {"id": "7E8", "pid": "0A", "range": (0, 800), "normal": (300, 500)},
                    "intake_temp": {"id": "7E8", "pid": "0F", "range": (-40, 150), "normal": (20, 40)},
                    "vehicle_speed": {"id": "7E8", "pid": "0D", "range": (0, 250), "normal": (0, 120)},
                    "air_suspension_height": {"id": "7C0", "pid": "21", "range": (0, 255), "normal": (128, 200)},
                    "abs_brake_pressure": {"id": "7A0", "pid": "31", "range": (0, 200), "normal": (0, 50)}
                },
                "calibration_thresholds": {
                    "message_frequency_variance": 0.15,
                    "parameter_deviation": 0.20,
                    "can_bus_load": 0.75,
                    "error_rate_threshold": 0.01
                }
            }
        }
    
    def start_high_calibration(self, vehicle_profile: str = "range_rover_sport_2009") -> Dict[str, Any]:
        """
        Start high calibration process for CAN bus analysis
        
        Args:
            vehicle_profile: Vehicle profile name
            
        Returns:
            Calibration status and configuration
        """
        try:
            if vehicle_profile not in self.land_rover_profiles:
                raise ValueError(f"Vehicle profile {vehicle_profile} not found")
            
            profile = self.land_rover_profiles[vehicle_profile]
            
            self.calibration_active = True
            self.calibration_data = {
                "start_time": datetime.now().isoformat(),
                "vehicle_profile": vehicle_profile,
                "protocol": profile["protocol"],
                "baseline_captured": False,
                "calibration_phases": {
                    "baseline": {"status": "pending", "messages_collected": 0},
                    "stability": {"status": "pending", "variance_analysis": {}},
                    "performance": {"status": "pending", "throughput_metrics": {}},
                    "anomaly_detection": {"status": "pending", "thresholds": {}}
                }
            }
            
            logger.info(f"Started high calibration for {vehicle_profile}")
            return {
                "status": "calibration_started",
                "profile": vehicle_profile,
                "protocol": profile["protocol"],
                "ecu_count": len(profile["ecu_list"]),
                "calibration_phases": 4
            }
            
        except Exception as e:
            logger.error(f"Error starting high calibration: {e}")
            return {"status": "error", "error": str(e)}
    
    def capture_baseline(self, can_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Capture baseline CAN bus data for calibration
        
        Args:
            can_messages: List of CAN messages with timestamps
            
        Returns:
            Baseline capture results
        """
        if not self.calibration_active:
            return {"status": "error", "error": "Calibration not active"}
        
        try:
            df = pd.DataFrame(can_messages)
            
            # Analyze message frequencies
            id_counts = df['arbitration_id'].value_counts()
            message_rates = {}
            for msg_id, count in id_counts.items():
                message_rates[hex(msg_id)] = count / len(can_messages)
            
            # Calculate message intervals
            intervals = []
            for msg_id in df['arbitration_id'].unique():
                msg_times = df[df['arbitration_id'] == msg_id]['timestamp'].values
                if len(msg_times) > 1:
                    msg_intervals = np.diff(msg_times)
                    intervals.extend(msg_intervals)
            
            baseline_metrics = {
                "total_messages": len(can_messages),
                "unique_ids": len(id_counts),
                "message_rate_per_id": message_rates,
                "average_interval": np.mean(intervals) if intervals else 0.0,
                "interval_variance": np.var(intervals) if intervals else 0.0,
                "timestamp_range": {
                    "start": float(df['timestamp'].min()),
                    "end": float(df['timestamp'].max()),
                    "duration": float(df['timestamp'].max() - df['timestamp'].min())
                }
            }
            
            # Update calibration data
            self.calibration_data["baseline_captured"] = True
            self.calibration_data["calibration_phases"]["baseline"] = {
                "status": "completed",
                "messages_collected": len(can_messages),
                "metrics": baseline_metrics
            }
            
            self.baseline_captured = True
            
            logger.info(f"Baseline captured: {len(can_messages)} messages, {len(id_counts)} unique IDs")
            return {
                "status": "baseline_captured",
                "metrics": baseline_metrics,
                "recommended_measurement_period": len(can_messages) * 2  # Double for stability
            }
            
        except Exception as e:
            logger.error(f"Error capturing baseline: {e}")
            return {"status": "error", "error": str(e)}
    
    def perform_stability_analysis(self, extended_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform stability analysis on extended CAN data collection
        
        Args:
            extended_messages: Extended list of CAN messages
            
        Returns:
            Stability analysis results
        """
        if not self.baseline_captured:
            return {"status": "error", "error": "Baseline not captured"}
        
        try:
            df = pd.DataFrame(extended_messages)
            
            # Rolling window analysis
            window_size = max(100, len(extended_messages) // 10)
            rolling_metrics = []
            
            for i in range(window_size, len(df), window_size//2):
                window_data = df.iloc[i-window_size:i]
                
                # Calculate stability metrics for this window
                id_counts = window_data['arbitration_id'].value_counts()
                
                window_metrics = {
                    "window_start": float(window_data['timestamp'].iloc[0]),
                    "window_end": float(window_data['timestamp'].iloc[-1]),
                    "message_count": len(window_data),
                    "unique_ids": len(id_counts),
                    "id_distribution": {hex(k): v for k, v in id_counts.items()}
                }
                
                rolling_metrics.append(window_metrics)
            
            # Stability variance calculation
            id_variances = {}
            for msg_id in df['arbitration_id'].unique():
                msg_data = df[df['arbitration_id'] == msg_id]
                if len(msg_data) > 1:
                    intervals = np.diff(msg_data['timestamp'].values)
                    id_variances[hex(msg_id)] = {
                        "mean_interval": float(np.mean(intervals)),
                        "variance": float(np.var(intervals)),
                        "stability_score": 1.0 / (1.0 + np.var(intervals))
                    }
            
            stability_results = {
                "stability_score": np.mean([m["stability_score"] for m in id_variances.values()]) if id_variances else 0.0,
                "rolling_window_count": len(rolling_metrics),
                "id_variance_analysis": id_variances,
                "overall_stability": "stable" if len(rolling_metrics) > 5 else "insufficient_data"
            }
            
            # Update calibration data
            self.calibration_data["calibration_phases"]["stability"] = {
                "status": "completed",
                "analysis_results": stability_results,
                "windows_analyzed": len(rolling_metrics)
            }
            
            logger.info(f"Stability analysis completed: {stability_results['stability_score']:.3f} score")
            return {
                "status": "stability_analyzed",
                "results": stability_results
            }
            
        except Exception as e:
            logger.error(f"Error performing stability analysis: {e}")
            return {"status": "error", "error": str(e)}
    
    def analyze_performance_metrics(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze CAN bus performance metrics
        
        Args:
            performance_data: Performance measurement data
            
        Returns:
            Performance analysis results
        """
        try:
            # Calculate throughput metrics
            throughput = {
                "messages_per_second": performance_data.get("message_rate", 0),
                "bytes_per_second": performance_data.get("byte_rate", 0),
                "bus_utilization": performance_data.get("bus_load", 0) / 100.0,
                "error_rate": performance_data.get("error_rate", 0)
            }
            
            # Performance benchmarks (Land Rover specific)
            benchmarks = {
                "target_message_rate": 45.0,  # Messages per second for Range Rover Sport
                "target_bus_utilization": 0.65,  # 65% max for stable operation
                "target_error_rate": 0.001  # 0.1% error rate target
            }
            
            performance_scores = {}
            for metric, value in throughput.items():
                if metric in benchmarks:
                    target = benchmarks[metric]
                    if metric == "error_rate":  # Lower is better for error rate
                        score = max(0, 1.0 - (value / target))
                    else:  # Higher is better for other metrics
                        score = min(1.0, value / target)
                    performance_scores[metric] = score
            
            overall_score = np.mean(list(performance_scores.values())) if performance_scores else 0.0
            
            performance_results = {
                "throughput_metrics": throughput,
                "benchmark_comparison": {
                    "scores": performance_scores,
                    "overall_score": overall_score,
                    "rating": self._get_performance_rating(overall_score)
                },
                "recommendations": self._generate_performance_recommendations(throughput, benchmarks)
            }
            
            # Update calibration data
            self.calibration_data["calibration_phases"]["performance"] = {
                "status": "completed",
                "metrics": performance_results
            }
            
            logger.info(f"Performance analysis completed: {overall_score:.3f} overall score")
            return {
                "status": "performance_analyzed",
                "results": performance_results
            }
            
        except Exception as e:
            logger.error(f"Error analyzing performance metrics: {e}")
            return {"status": "error", "error": str(e)}
    
    def setup_anomaly_detection(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Setup anomaly detection for CAN bus data
        
        Args:
            training_data: Training data for anomaly detection
            
        Returns:
            Anomaly detection setup results
        """
        try:
            # Extract features for anomaly detection
            features = self._extract_can_features(training_data)
            
            if len(features) < 10:
                return {"status": "error", "error": "Insufficient training data"}
            
            # Train anomaly detector
            self.anomaly_detector.fit(features)
            
            # Train message classifier
            features_scaled = self.scaler.fit_transform(features)
            clusters = self.message_classifier.fit_predict(features_scaled)
            
            anomaly_thresholds = {
                "contamination_level": 0.1,
                "feature_dimensions": features.shape[1],
                "training_samples": len(features),
                "cluster_count": len(set(clusters)) - (1 if -1 in clusters else 0)
            }
            
            # Update calibration data
            self.calibration_data["calibration_phases"]["anomaly_detection"] = {
                "status": "completed",
                "thresholds": anomaly_thresholds,
                "model_trained": True
            }
            
            logger.info(f"Anomaly detection trained on {len(features)} samples")
            return {
                "status": "anomaly_detection_ready",
                "thresholds": anomaly_thresholds
            }
            
        except Exception as e:
            logger.error(f"Error setting up anomaly detection: {e}")
            return {"status": "error", "error": str(e)}
    
    def detect_can_anomalies(self, test_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect anomalies in CAN bus messages
        
        Args:
            test_messages: Test CAN messages to analyze
            
        Returns:
            Anomaly detection results
        """
        try:
            if not self.calibration_data.get("calibration_phases", {}).get("anomaly_detection", {}).get("status") == "completed":
                return {"status": "error", "error": "Anomaly detection not trained"}
            
            # Extract features
            features = self._extract_can_features(test_messages)
            
            if len(features) == 0:
                return {"status": "no_messages", "anomalies": []}
            
            # Detect anomalies
            features_scaled = self.scaler.transform(features)
            anomaly_scores = self.anomaly_detector.decision_function(features_scaled)
            is_anomaly = self.anomaly_detector.predict(features_scaled)
            
            # Analyze anomalies
            anomalies = []
            for i, (score, is_anom) in enumerate(zip(anomaly_scores, is_anomaly)):
                if is_anom == -1:  # Anomaly detected
                    anomalies.append({
                        "message_index": i,
                        "anomaly_score": float(score),
                        "severity": "high" if score < -0.5 else "medium",
                        "message_id": test_messages[i].get("arbitration_id", "unknown")
                    })
            
            # Calculate overall CAN bus health
            health_score = max(0, (len(test_messages) - len(anomalies)) / len(test_messages))
            
            anomaly_results = {
                "total_messages": len(test_messages),
                "anomalies_detected": len(anomalies),
                "health_score": health_score,
                "anomaly_details": anomalies,
                "recommendations": self._generate_anomaly_recommendations(anomalies)
            }
            
            logger.info(f"Anomaly detection: {len(anomalies)} anomalies from {len(test_messages)} messages")
            return {
                "status": "anomalies_detected",
                "results": anomaly_results
            }
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return {"status": "error", "error": str(e)}
    
    def _extract_can_features(self, can_messages: List[Dict[str, Any]]) -> np.ndarray:
        """Extract features from CAN messages for ML processing"""
        features = []
        
        for msg in can_messages:
            feature_vector = [
                float(msg.get("arbitration_id", 0)),
                float(len(msg.get("data", []))),
                float(msg.get("timestamp", 0.0)),
                float(msg.get("dlc", 0)),
                float(msg.get("extended_id", 0)),
                float(msg.get("is_remote_frame", 0))
            ]
            
            # Add message-specific features
            data = msg.get("data", [])
            for i in range(8):  # CAN data is max 8 bytes
                feature_vector.append(float(data[i] if i < len(data) else 0))
            
            features.append(feature_vector)
        
        return np.array(features)
    
    def _get_performance_rating(self, score: float) -> str:
        """Get performance rating based on score"""
        if score >= 0.9:
            return "excellent"
        elif score >= 0.8:
            return "good"
        elif score >= 0.7:
            return "fair"
        elif score >= 0.6:
            return "poor"
        else:
            return "critical"
    
    def _generate_performance_recommendations(self, throughput: Dict[str, Any], benchmarks: Dict[str, float]) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        if throughput.get("bus_utilization", 0) > benchmarks.get("target_bus_utilization", 0.65):
            recommendations.append("High bus utilization detected - consider optimizing message frequency")
        
        if throughput.get("error_rate", 0) > benchmarks.get("target_error_rate", 0.001):
            recommendations.append("High error rate - check wiring and connections")
        
        if throughput.get("messages_per_second", 0) < benchmarks.get("target_message_rate", 45):
            recommendations.append("Low message rate - verify ECU communication")
        
        if not recommendations:
            recommendations.append("CAN bus performance within normal parameters")
        
        return recommendations
    
    def _generate_anomaly_recommendations(self, anomalies: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on detected anomalies"""
        if not anomalies:
            return ["No anomalies detected - CAN bus operating normally"]
        
        recommendations = []
        
        if len(anomalies) > 10:
            recommendations.append("Multiple anomalies detected - perform comprehensive CAN bus inspection")
        
        high_severity_count = sum(1 for a in anomalies if a.get("severity") == "high")
        if high_severity_count > 3:
            recommendations.append("Critical anomalies detected - immediate diagnostic required")
        
        unique_ids = set(a.get("message_id") for a in anomalies)
        if len(unique_ids) < len(anomalies) / 2:
            recommendations.append("Repeated anomalies from specific ECUs - focus diagnostic on those modules")
        
        return recommendations
    
    def get_calibration_summary(self) -> Dict[str, Any]:
        """Get comprehensive calibration summary"""
        return {
            "calibration_status": self.calibration_data,
            "land_rover_profile": "range_rover_sport_2009",
            "ready_for_ai_learning": self.baseline_captured,
            "next_steps": [
                "Complete performance analysis",
                "Finalize anomaly detection thresholds",
                "Begin AI model training",
                "Validate calibration accuracy"
            ]
        }

# Global high calibration instance
can_bus_high_calibration = CANBusHighCalibration()
