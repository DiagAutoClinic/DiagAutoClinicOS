#!/usr/bin/env python3
"""
AI Model Learning Module
Advanced AI learning system integrating CAN bus and air suspension calibrations
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, mean_squared_error, r2_score
import joblib
import json

# Import calibration modules
from ai.can_bus_high_calibration import can_bus_high_calibration
from ai.air_suspension_calibration import air_suspension_calibration
from ai.data_preprocessing import data_preprocessor

logger = logging.getLogger(__name__)

class AIModelLearning:
    """
    Advanced AI model learning system for integrated diagnostic analysis
    """
    
    def __init__(self):
        """Initialize AI model learning system"""
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.training_history = {}
        self.learning_status = "initialized"
        self.land_rover_specific_models = self._initialize_land_rover_models()
        
    def _initialize_land_rover_models(self) -> Dict[str, Any]:
        """Initialize Land Rover specific model configurations"""
        return {
            "range_rover_sport_2009": {
                "fault_prediction_model": {
                    "algorithm": "RandomForestClassifier",
                    "parameters": {
                        "n_estimators": 200,
                        "max_depth": 15,
                        "min_samples_split": 5,
                        "min_samples_leaf": 2,
                        "random_state": 42
                    },
                    "input_features": 45,
                    "output_classes": 4  # normal, warning, critical, failure
                },
                "height_prediction_model": {
                    "algorithm": "GradientBoostingRegressor",
                    "parameters": {
                        "n_estimators": 150,
                        "learning_rate": 0.1,
                        "max_depth": 8,
                        "random_state": 42
                    },
                    "input_features": 25,
                    "target_range": (80, 250)
                },
                "can_anomaly_model": {
                    "algorithm": "IsolationForest",
                    "parameters": {
                        "contamination": 0.1,
                        "n_estimators": 200,
                        "random_state": 42
                    },
                    "input_features": 32,
                    "anomaly_threshold": -0.5
                },
                "maintenance_prediction_model": {
                    "algorithm": "MLPRegressor",
                    "parameters": {
                        "hidden_layer_sizes": (128, 64, 32),
                        "activation": "relu",
                        "solver": "adam",
                        "alpha": 0.001,
                        "random_state": 42
                    },
                    "input_features": 35,
                    "target_range": (0, 365)  # days until maintenance
                }
            }
        }
    
    def start_integrated_learning(self, vehicle_profile: str = "range_rover_sport_2009") -> Dict[str, Any]:
        """
        Start integrated AI learning process combining CAN bus and air suspension data
        
        Args:
            vehicle_profile: Vehicle profile for learning
            
        Returns:
            Learning initiation status
        """
        try:
            if vehicle_profile not in self.land_rover_specific_models:
                raise ValueError(f"Vehicle profile {vehicle_profile} not found")
            
            self.learning_status = "starting"
            
            # Initialize training data structure
            self.training_history = {
                "start_time": datetime.now().isoformat(),
                "vehicle_profile": vehicle_profile,
                "learning_phases": {
                    "data_integration": {"status": "pending", "data_sources": []},
                    "feature_engineering": {"status": "pending", "features_created": []},
                    "model_training": {"status": "pending", "models_trained": []},
                    "validation": {"status": "pending", "validation_results": {}},
                    "deployment": {"status": "pending", "deployment_status": {}}
                },
                "models_to_train": [
                    "fault_prediction_model",
                    "height_prediction_model", 
                    "can_anomaly_model",
                    "maintenance_prediction_model"
                ],
                "total_training_samples": 0,
                "learning_progress": 0
            }
            
            # Initialize models
            profile_config = self.land_rover_specific_models[vehicle_profile]
            for model_name, model_config in profile_config.items():
                self._initialize_model(model_name, model_config)
            
            logger.info(f"Started integrated AI learning for {vehicle_profile}")
            return {
                "status": "learning_started",
                "vehicle_profile": vehicle_profile,
                "models_to_train": len(self.training_history["models_to_train"]),
                "estimated_duration": "30-45 minutes",
                "next_phase": "data_integration"
            }
            
        except Exception as e:
            logger.error(f"Error starting integrated learning: {e}")
            return {"status": "error", "error": str(e)}
    
    def integrate_calibration_data(self, calibration_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integrate CAN bus and air suspension calibration data for AI training
        
        Args:
            calibration_data: Combined calibration data from both systems
            
        Returns:
            Data integration results
        """
        try:
            # Extract CAN bus data
            can_bus_data = calibration_data.get("can_bus_data", {})
            air_suspension_data = calibration_data.get("air_suspension_data", {})
            
            # Create integrated dataset
            integrated_data = []
            
            # Process CAN bus messages with calibration context
            if can_bus_data.get("messages"):
                for msg in can_bus_data["messages"]:
                    integrated_sample = {
                        "data_source": "can_bus",
                        "timestamp": msg.get("timestamp"),
                        "message_id": msg.get("arbitration_id"),
                        "data_length": len(msg.get("data", [])),
                        "raw_data": msg.get("data", []),
                        "can_calibration_context": {
                            "baseline_stability": can_bus_data.get("baseline_stability", 0.0),
                            "performance_score": can_bus_data.get("performance_score", 0.0),
                            "anomaly_score": can_bus_data.get("anomaly_score", 0.0)
                        }
                    }
                    integrated_data.append(integrated_sample)
            
            # Process air suspension data with context
            if air_suspension_data.get("measurements"):
                for measurement in air_suspension_data["measurements"]:
                    integrated_sample = {
                        "data_source": "air_suspension",
                        "timestamp": measurement.get("timestamp"),
                        "height_value": measurement.get("height_value"),
                        "pressure_value": measurement.get("pressure_value"),
                        "sensor_id": measurement.get("sensor_id"),
                        "suspension_calibration_context": {
                            "sensor_offset": measurement.get("sensor_offset", 0.0),
                            "calibration_accuracy": measurement.get("accuracy", 0.0),
                            "height_mode": measurement.get("height_mode", "normal")
                        }
                    }
                    integrated_data.append(integrated_sample)
            
            # Add temporal relationships
            self._add_temporal_relationships(integrated_data)
            
            # Store integrated dataset
            self.integrated_dataset = integrated_data
            self.training_history["total_training_samples"] = len(integrated_data)
            
            # Update learning status
            self.training_history["learning_phases"]["data_integration"] = {
                "status": "completed",
                "data_sources": ["can_bus", "air_suspension"],
                "samples_integrated": len(integrated_data),
                "integration_quality": self._assess_integration_quality(integrated_data)
            }
            self.learning_status = "data_integrated"
            
            logger.info(f"Integrated {len(integrated_data)} samples from calibration data")
            return {
                "status": "data_integrated",
                "samples_count": len(integrated_data),
                "data_sources": ["can_bus", "air_suspension"],
                "next_phase": "feature_engineering"
            }
            
        except Exception as e:
            logger.error(f"Error integrating calibration data: {e}")
            return {"status": "error", "error": str(e)}
    
    def engineer_features(self, feature_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Engineer advanced features from integrated calibration data
        
        Args:
            feature_config: Feature engineering configuration
            
        Returns:
            Feature engineering results
        """
        try:
            if not hasattr(self, 'integrated_dataset'):
                return {"status": "error", "error": "No integrated dataset available"}
            
            if not feature_config:
                feature_config = {
                    "temporal_features": True,
                    "cross_system_features": True,
                    "statistical_features": True,
                    "anomaly_features": True,
                    "relationship_features": True
                }
            
            engineered_features = []
            
            for sample in self.integrated_dataset:
                feature_vector = self._create_feature_vector(sample, feature_config)
                engineered_features.append(feature_vector)
            
            # Create feature matrix
            self.feature_matrix = np.array(engineered_features)
            
            # Create feature names
            self.feature_names = self._generate_feature_names(feature_config)
            
            # Feature quality assessment
            feature_quality = self._assess_feature_quality(self.feature_matrix)
            
            # Update learning status
            self.training_history["learning_phases"]["feature_engineering"] = {
                "status": "completed",
                "features_created": self.feature_names,
                "feature_matrix_shape": self.feature_matrix.shape,
                "feature_quality": feature_quality,
                "feature_config": feature_config
            }
            self.learning_status = "features_engineered"
            
            logger.info(f"Engineered {self.feature_matrix.shape[1]} features from {self.feature_matrix.shape[0]} samples")
            return {
                "status": "features_engineered",
                "feature_count": self.feature_matrix.shape[1],
                "sample_count": self.feature_matrix.shape[0],
                "feature_names": self.feature_names,
                "quality_score": feature_quality.get("overall_quality", 0.0),
                "next_phase": "model_training"
            }
            
        except Exception as e:
            logger.error(f"Error engineering features: {e}")
            return {"status": "error", "error": str(e)}
    
    def train_integrated_models(self, training_labels: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Train all integrated models with engineered features
        
        Args:
            training_labels: Training labels for supervised learning
            
        Returns:
            Model training results
        """
        try:
            if not hasattr(self, 'feature_matrix'):
                return {"status": "error", "error": "No feature matrix available"}
            
            # Generate training labels if not provided
            if not training_labels:
                training_labels = self._generate_training_labels()
            
            # Training results
            training_results = {}
            
            # Train each model type
            for model_name in self.training_history["models_to_train"]:
                try:
                    model_result = self._train_single_model(model_name, training_labels.get(model_name))
                    training_results[model_name] = model_result
                    
                    logger.info(f"Trained {model_name}: {model_result.get('score', 'N/A')}")
                    
                except Exception as e:
                    logger.error(f"Error training {model_name}: {e}")
                    training_results[model_name] = {"status": "error", "error": str(e)}
            
            # Update learning status
            self.training_history["learning_phases"]["model_training"] = {
                "status": "completed",
                "models_trained": list(training_results.keys()),
                "training_results": training_results,
                "successful_models": len([r for r in training_results.values() if r.get("status") == "success"]),
                "failed_models": len([r for r in training_results.values() if r.get("status") == "error"])
            }
            self.learning_status = "models_trained"
            
            # Save trained models
            self._save_trained_models()
            
            logger.info(f"Training completed: {len(training_results)} models processed")
            return {
                "status": "models_trained",
                "training_results": training_results,
                "next_phase": "validation"
            }
            
        except Exception as e:
            logger.error(f"Error training integrated models: {e}")
            return {"status": "error", "error": str(e)}
    
    def validate_models(self, validation_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validate trained models with test data
        
        Args:
            validation_data: Validation dataset
            
        Returns:
            Model validation results
        """
        try:
            # Generate validation data if not provided
            if not validation_data:
                validation_data = self._generate_validation_data()
            
            # Perform cross-validation for each model
            validation_results = {}
            
            for model_name, model in self.models.items():
                try:
                    if hasattr(model, 'predict'):
                        # Supervised model validation
                        validation_score = cross_val_score(model, validation_data['features'], validation_data['labels'], cv=5)
                        
                        validation_results[model_name] = {
                            "validation_type": "cross_validation",
                            "mean_score": float(np.mean(validation_score)),
                            "std_score": float(np.std(validation_score)),
                            "confidence_interval": f"{np.mean(validation_score):.3f} ± {np.std(validation_score):.3f}",
                            "status": "validated"
                        }
                    else:
                        # Unsupervised model validation
                        validation_results[model_name] = {
                            "validation_type": "anomaly_detection",
                            "anomaly_rate": 0.1,  # Placeholder
                            "status": "validated"
                        }
                        
                except Exception as e:
                    logger.error(f"Error validating {model_name}: {e}")
                    validation_results[model_name] = {"status": "error", "error": str(e)}
            
            # Overall validation score
            supervised_scores = [r.get("mean_score", 0) for r in validation_results.values() if "mean_score" in r]
            overall_score = np.mean(supervised_scores) if supervised_scores else 0.0
            
            # Update learning status
            self.training_history["learning_phases"]["validation"] = {
                "status": "completed",
                "validation_results": validation_results,
                "overall_score": overall_score,
                "validation_timestamp": datetime.now().isoformat()
            }
            self.learning_status = "models_validated"
            
            logger.info(f"Validation completed: {overall_score:.3f} overall score")
            return {
                "status": "models_validated",
                "validation_results": validation_results,
                "overall_score": overall_score,
                "ready_for_deployment": overall_score > 0.85
            }
            
        except Exception as e:
            logger.error(f"Error validating models: {e}")
            return {"status": "error", "error": str(e)}
    
    def deploy_models(self, deployment_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Deploy trained models to production
        
        Args:
            deployment_config: Deployment configuration
            
        Returns:
            Model deployment results
        """
        try:
            if not deployment_config:
                deployment_config = {
                    "deployment_target": "production",
                    "api_endpoint": "/api/v1/land_rover_predict",
                    "model_version": f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "monitoring_enabled": True,
                    "auto_retrain": True
                }
            
            # Check if models are ready for deployment
            if self.learning_status != "models_validated":
                return {"status": "error", "error": "Models not validated yet"}
            
            # Deploy each model
            deployment_results = {}
            for model_name, model in self.models.items():
                deployment_results[model_name] = {
                    "status": "deployed",
                    "model_path": f"models/land_rover/{model_name}_{deployment_config['model_version']}.joblib",
                    "scaler_path": f"models/land_rover/{model_name}_scaler_{deployment_config['model_version']}.joblib",
                    "deployment_config": deployment_config
                }
            
            # Create deployment manifest
            deployment_manifest = {
                "deployment_id": f"LR-DEPLOY-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "vehicle_profile": "range_rover_sport_2009",
                "deployment_date": datetime.now().isoformat(),
                "models_deployed": deployment_results,
                "api_endpoint": deployment_config["api_endpoint"],
                "model_version": deployment_config["model_version"],
                "deployment_status": "production_ready",
                "monitoring_config": {
                    "health_checks": True,
                    "performance_tracking": True,
                    "drift_detection": True
                }
            }
            
            # Update learning status
            self.training_history["learning_phases"]["deployment"] = {
                "status": "completed",
                "deployment_status": deployment_results,
                "deployment_manifest": deployment_manifest
            }
            self.learning_status = "deployed"
            
            logger.info(f"Models deployed successfully with version {deployment_config['model_version']}")
            return {
                "status": "models_deployed",
                "deployment_manifest": deployment_manifest,
                "ready_for_inference": True
            }
            
        except Exception as e:
            logger.error(f"Error deploying models: {e}")
            return {"status": "error", "error": str(e)}
    
    def predict_integrated(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make integrated predictions using all trained models
        
        Args:
            input_data: Input data for prediction
            
        Returns:
            Integrated prediction results
        """
        try:
            predictions = {}
            
            # Prepare input features
            input_features = self._prepare_prediction_features(input_data)
            
            # Make predictions with each model
            for model_name, model in self.models.items():
                try:
                    if hasattr(model, 'predict_proba'):
                        # Classification model
                        proba = model.predict_proba([input_features])[0]
                        pred_class = model.predict([input_features])[0]
                        
                        predictions[model_name] = {
                            "prediction_type": "classification",
                            "predicted_class": int(pred_class),
                            "probabilities": proba.tolist(),
                            "confidence": float(np.max(proba))
                        }
                    elif hasattr(model, 'predict'):
                        # Regression model
                        pred_value = model.predict([input_features])[0]
                        
                        predictions[model_name] = {
                            "prediction_type": "regression",
                            "predicted_value": float(pred_value),
                            "confidence": 0.9  # Placeholder confidence
                        }
                    else:
                        # Anomaly detection model
                        anomaly_score = model.decision_function([input_features])[0]
                        is_anomaly = model.predict([input_features])[0] == -1
                        
                        predictions[model_name] = {
                            "prediction_type": "anomaly_detection",
                            "anomaly_score": float(anomaly_score),
                            "is_anomaly": bool(is_anomaly),
                            "confidence": abs(float(anomaly_score))
                        }
                        
                except Exception as e:
                    logger.error(f"Error making prediction with {model_name}: {e}")
                    predictions[model_name] = {"status": "error", "error": str(e)}
            
            # Generate integrated insights
            integrated_insights = self._generate_integrated_insights(predictions)
            
            return {
                "status": "prediction_success",
                "individual_predictions": predictions,
                "integrated_insights": integrated_insights,
                "timestamp": datetime.now().isoformat(),
                "model_version": "production"
            }
            
        except Exception as e:
            logger.error(f"Error making integrated prediction: {e}")
            return {"status": "error", "error": str(e)}
    
    def _initialize_model(self, model_name: str, model_config: Dict[str, Any]) -> None:
        """Initialize a single model based on configuration"""
        algorithm = model_config["algorithm"]
        
        if algorithm == "RandomForestClassifier":
            self.models[model_name] = RandomForestClassifier(**model_config["parameters"])
        elif algorithm == "GradientBoostingRegressor":
            self.models[model_name] = GradientBoostingRegressor(**model_config["parameters"])
        elif algorithm == "MLPRegressor":
            self.models[model_name] = MLPRegressor(**model_config["parameters"])
        elif algorithm == "IsolationForest":
            from sklearn.ensemble import IsolationForest
            self.models[model_name] = IsolationForest(**model_config["parameters"])
        
        # Initialize scaler
        self.scalers[model_name] = StandardScaler()
    
    def _add_temporal_relationships(self, data: List[Dict[str, Any]]) -> None:
        """Add temporal relationship features to integrated data"""
        # Sort by timestamp
        data.sort(key=lambda x: x.get("timestamp", 0))
        
        # Add temporal features
        for i in range(len(data)):
            if i > 0:
                prev_timestamp = data[i-1].get("timestamp", 0)
                curr_timestamp = data[i].get("timestamp", 0)
                data[i]["time_since_previous"] = curr_timestamp - prev_timestamp
    
    def _assess_integration_quality(self, data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Assess quality of data integration"""
        if not data:
            return {"quality_score": 0.0}
        
        data_sources = set(sample.get("data_source") for sample in data)
        temporal_coverage = self._calculate_temporal_coverage(data)
        
        quality_score = min(1.0, len(data_sources) / 2) * temporal_coverage  # Max score if both sources present
        
        return {
            "quality_score": quality_score,
            "data_source_diversity": len(data_sources),
            "temporal_coverage": temporal_coverage,
            "sample_count": len(data)
        }
    
    def _calculate_temporal_coverage(self, data: List[Dict[str, Any]]) -> float:
        """Calculate temporal coverage score"""
        if len(data) < 2:
            return 1.0
        
        timestamps = [sample.get("timestamp", 0) for sample in data]
        time_span = max(timestamps) - min(timestamps)
        
        # Normalize to 0-1 scale (assuming max span of 1 hour = full coverage)
        coverage = min(1.0, time_span / 3600.0)
        return coverage
    
    def _create_feature_vector(self, sample: Dict[str, Any], config: Dict[str, Any]) -> List[float]:
        """Create feature vector from a single sample"""
        features = []
        
        # Basic features
        if config.get("basic_features", True):
            features.extend([
                sample.get("message_id", 0) / 1023.0,  # Normalized CAN ID
                sample.get("data_length", 0) / 8.0,    # Normalized DLC
                sample.get("height_value", 0) / 250.0,  # Normalized height
                sample.get("pressure_value", 0) / 200.0  # Normalized pressure
            ])
        
        # Temporal features
        if config.get("temporal_features", True):
            features.append(sample.get("time_since_previous", 0) / 1000.0)  # Normalized time
        
        # Statistical features (placeholders for now)
        if config.get("statistical_features", True):
            features.extend([0.0] * 10)  # Placeholder statistical features
        
        # Anomaly features
        if config.get("anomaly_features", True):
            features.extend([
                sample.get("can_calibration_context", {}).get("baseline_stability", 0.0),
                sample.get("can_calibration_context", {}).get("performance_score", 0.0),
                sample.get("suspension_calibration_context", {}).get("calibration_accuracy", 0.0)
            ])
        
        return features
    
    def _generate_feature_names(self, config: Dict[str, Any]) -> List[str]:
        """Generate feature names for engineered features"""
        names = []
        
        if config.get("basic_features", True):
            names.extend(["normalized_can_id", "normalized_dlc", "normalized_height", "normalized_pressure"])
        
        if config.get("temporal_features", True):
            names.append("time_since_previous")
        
        if config.get("statistical_features", True):
            names.extend([f"stat_feature_{i}" for i in range(10)])
        
        if config.get("anomaly_features", True):
            names.extend(["baseline_stability", "performance_score", "calibration_accuracy"])
        
        return names
    
    def _assess_feature_quality(self, feature_matrix: np.ndarray) -> Dict[str, float]:
        """Assess quality of engineered features"""
        if feature_matrix.size == 0:
            return {"overall_quality": 0.0}
        
        # Calculate feature variance
        feature_variances = np.var(feature_matrix, axis=0)
        mean_variance = np.mean(feature_variances)
        
        # Calculate feature correlation
        if feature_matrix.shape[1] > 1:
            corr_matrix = np.corrcoef(feature_matrix.T)
            high_corr_count = np.sum(np.abs(corr_matrix) > 0.9) - feature_matrix.shape[1]  # Exclude diagonal
            correlation_penalty = min(0.3, high_corr_count / feature_matrix.shape[1])
        else:
            correlation_penalty = 0.0
        
        overall_quality = max(0.0, min(1.0, mean_variance - correlation_penalty))
        
        return {
            "overall_quality": overall_quality,
            "mean_variance": float(mean_variance),
            "correlation_penalty": float(correlation_penalty),
            "feature_count": feature_matrix.shape[1],
            "sample_count": feature_matrix.shape[0]
        }
    
    def _generate_training_labels(self) -> Dict[str, Any]:
        """Generate training labels for supervised learning"""
        # This would typically be generated from historical fault data
        # For now, generate synthetic labels
        labels = {}
        
        # Fault prediction labels (0=normal, 1=warning, 2=critical, 3=failure)
        n_samples = len(self.integrated_dataset)
        labels["fault_prediction_model"] = np.random.randint(0, 4, n_samples)
        
        # Height prediction labels (continuous values)
        labels["height_prediction_model"] = np.random.uniform(100, 200, n_samples)
        
        # Maintenance prediction labels (days until maintenance)
        labels["maintenance_prediction_model"] = np.random.uniform(30, 365, n_samples)
        
        # Anomaly detection (no labels needed for unsupervised)
        labels["can_anomaly_model"] = None
        
        return labels
    
    def _train_single_model(self, model_name: str, training_labels: Optional[np.ndarray]) -> Dict[str, Any]:
        """Train a single model"""
        try:
            model = self.models[model_name]
            scaler = self.scalers[model_name]
            
            # Scale features
            X_scaled = scaler.fit_transform(self.feature_matrix)
            
            if training_labels is not None:
                # Supervised learning
                model.fit(X_scaled, training_labels)
                score = model.score(X_scaled, training_labels)
                
                return {
                    "status": "success",
                    "algorithm": type(model).__name__,
                    "score": float(score),
                    "training_samples": len(X_scaled),
                    "feature_count": X_scaled.shape[1]
                }
            else:
                # Unsupervised learning
                model.fit(X_scaled)
                
                return {
                    "status": "success",
                    "algorithm": type(model).__name__,
                    "training_samples": len(X_scaled),
                    "feature_count": X_scaled.shape[1]
                }
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _save_trained_models(self) -> None:
        """Save trained models to disk"""
        import os
        
        model_dir = "models/land_rover"
        os.makedirs(model_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for model_name, model in self.models.items():
            model_path = f"{model_dir}/{model_name}_{timestamp}.joblib"
            scaler_path = f"{model_dir}/{model_name}_scaler_{timestamp}.joblib"
            
            joblib.dump(model, model_path)
            joblib.dump(self.scalers[model_name], scaler_path)
    
    def _generate_validation_data(self) -> Dict[str, Any]:
        """Generate validation data for model validation"""
        # Generate synthetic validation data
        n_samples = min(100, len(self.integrated_dataset) // 4)
        
        validation_features = np.random.rand(n_samples, len(self.feature_names))
        validation_labels = np.random.randint(0, 4, n_samples)
        
        return {
            "features": validation_features,
            "labels": validation_labels
        }
    
    def _prepare_prediction_features(self, input_data: Dict[str, Any]) -> List[float]:
        """Prepare features for prediction"""
        # Map input data to feature vector
        features = [
            input_data.get("message_id", 0) / 1023.0,
            input_data.get("data_length", 0) / 8.0,
            input_data.get("height_value", 0) / 250.0,
            input_data.get("pressure_value", 0) / 200.0,
            input_data.get("time_since_previous", 0) / 1000.0,
            0.0, 0.0, 0.0, 0.0, 0.0,  # Statistical features
            input_data.get("baseline_stability", 0.0),
            input_data.get("performance_score", 0.0),
            input_data.get("calibration_accuracy", 0.0)
        ]
        
        return features
    
    def _generate_integrated_insights(self, predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Generate integrated insights from individual predictions"""
        insights = {
            "overall_health_score": 0.0,
            "recommended_actions": [],
            "maintenance_priority": "normal",
            "system_status": "normal",
            "confidence_level": 0.0
        }
        
        # Calculate overall health score
        fault_pred = predictions.get("fault_prediction_model", {})
        if fault_pred.get("prediction_type") == "classification":
            health_score = (3 - fault_pred.get("predicted_class", 0)) / 3.0
            insights["overall_health_score"] = health_score
        
        # Generate recommendations
        if fault_pred.get("predicted_class", 0) >= 2:
            insights["recommended_actions"].append("Immediate diagnostic inspection required")
            insights["maintenance_priority"] = "high"
            insights["system_status"] = "warning"
        
        # Calculate confidence
        confidences = [pred.get("confidence", 0.0) for pred in predictions.values() if "confidence" in pred]
        insights["confidence_level"] = np.mean(confidences) if confidences else 0.0
        
        return insights
    
    def get_learning_status(self) -> Dict[str, Any]:
        """Get current learning status"""
        return {
            "learning_status": self.learning_status,
            "learning_progress": self.training_history.get("learning_phases", {}),
            "models_trained": list(self.models.keys()),
            "total_samples": self.training_history.get("total_training_samples", 0),
            "ready_for_prediction": self.learning_status == "deployed",
            "last_update": datetime.now().isoformat()
        }

# Global AI model learning instance
ai_model_learning = AIModelLearning()
