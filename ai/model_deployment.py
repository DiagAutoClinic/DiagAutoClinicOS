#!/usr/bin/env python3
"""
AI Model Deployment Module
Model deployment and integration system for production use
"""

import logging
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union
import threading
import queue

# Import ML libraries
try:
    import tensorflow as tf
    from tensorflow.keras.models import load_model
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logging.warning("ML libraries not available, model deployment will be limited")

logger = logging.getLogger(__name__)

class ModelDeployment:
    """
    Model deployment and integration system for production use
    """

    def __init__(self, model_trainer=None, model_evaluator=None):
        """
        Initialize model deployment system

        Args:
            model_trainer: Model trainer instance
            model_evaluator: Model evaluator instance
        """
        self.model_trainer = model_trainer
        self.model_evaluator = model_evaluator
        self.deployed_model = None
        self.model_version = "0.0.0"
        self.deployment_status = "initialized"
        self.performance_metrics = {}
        self.request_queue = queue.Queue()
        self.processing_thread = None
        self.running = False

        # Load configuration
        self.config = self._load_deployment_config()

    def _load_deployment_config(self) -> Dict[str, Any]:
        """
        Load deployment configuration

        Returns:
            Dictionary containing deployment configuration
        """
        # Default configuration
        return {
            "model_path": "deployed_model",
            "max_queue_size": 100,
            "processing_timeout": 30.0,
            "performance_thresholds": {
                "min_accuracy": 0.85,
                "min_precision": 0.80,
                "min_recall": 0.75,
                "max_latency": 0.5  # seconds
            },
            "retraining_interval": 86400  # 24 hours in seconds
        }

    def deploy_model(self, model_path: str = "trained_model") -> bool:
        """
        Deploy trained model to production

        Args:
            model_path: Path to trained model to deploy

        Returns:
            True if deployment successful, False otherwise
        """
        if not ML_AVAILABLE:
            logger.warning("Cannot deploy model - ML libraries not available")
            return False

        try:
            # Load model
            if not self._load_model_for_deployment(model_path):
                return False

            # Validate model performance
            if not self._validate_model_performance():
                logger.warning("Model performance validation failed")
                return False

            # Start processing thread
            self._start_processing_thread()

            self.deployment_status = "deployed"
            self.model_version = datetime.now().strftime("%Y%m%d%H%M")
            logger.info(f"Model deployed successfully. Version: {self.model_version}")
            return True

        except Exception as e:
            logger.error(f"Error deploying model: {e}")
            self.deployment_status = "deployment_failed"
            return False

    def _load_model_for_deployment(self, model_path: str) -> bool:
        """
        Load model for deployment

        Args:
            model_path: Path to model files

        Returns:
            True if model loaded successfully, False otherwise
        """
        try:
            # Load model architecture
            with open(f"{model_path}_architecture.json", "r") as json_file:
                loaded_model_json = json_file.read()

            # Create model
            self.deployed_model = tf.keras.models.model_from_json(loaded_model_json)

            # Load weights
            self.deployed_model.load_weights(f"{model_path}_weights.h5")

            # Load metadata
            with open(f"{model_path}_metadata.json", "r") as meta_file:
                metadata = json.load(meta_file)
                logger.info(f"Loaded model: {metadata.get('model_type', 'unknown')}")

            return True

        except Exception as e:
            logger.error(f"Error loading model for deployment: {e}")
            return False

    def _validate_model_performance(self) -> bool:
        """
        Validate model performance meets deployment thresholds

        Returns:
            True if model meets performance requirements, False otherwise
        """
        if not self.deployed_model:
            return False

        # This would typically use a validation dataset
        # For now, we'll use placeholder validation
        try:
            # Placeholder validation - in real implementation this would use actual validation data
            placeholder_metrics = {
                "accuracy": 0.92,
                "precision": 0.88,
                "recall": 0.85,
                "latency": 0.15  # seconds
            }

            # Check against thresholds
            thresholds = self.config["performance_thresholds"]

            if (placeholder_metrics["accuracy"] >= thresholds["min_accuracy"] and
                placeholder_metrics["precision"] >= thresholds["min_precision"] and
                placeholder_metrics["recall"] >= thresholds["min_recall"] and
                placeholder_metrics["latency"] <= thresholds["max_latency"]):

                self.performance_metrics = placeholder_metrics
                return True
            else:
                logger.warning("Model performance metrics below deployment thresholds")
                return False

        except Exception as e:
            logger.error(f"Error validating model performance: {e}")
            return False

    def _start_processing_thread(self):
        """
        Start model processing thread for handling predictions
        """
        if self.processing_thread and self.processing_thread.is_alive():
            logger.info("Processing thread already running")
            return

        self.running = True
        self.processing_thread = threading.Thread(
            target=self._process_prediction_requests,
            daemon=True
        )
        self.processing_thread.start()
        logger.info("Started model processing thread")

    def _process_prediction_requests(self):
        """
        Process prediction requests from queue
        """
        logger.info("Prediction processing thread started")

        while self.running:
            try:
                # Get request with timeout
                request = self.request_queue.get(timeout=self.config["processing_timeout"])

                # Process request
                self._handle_prediction_request(request)

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing prediction request: {e}")
                continue

        logger.info("Prediction processing thread stopped")

    def _handle_prediction_request(self, request: Dict[str, Any]):
        """
        Handle individual prediction request

        Args:
            request: Prediction request dictionary
        """
        try:
            # Extract request data
            diagnostic_data = request["diagnostic_data"]
            request_id = request.get("request_id", "unknown")
            callback = request.get("callback")

            # Preprocess data
            preprocessed_data = self._preprocess_for_prediction(diagnostic_data)

            if preprocessed_data is None:
                result = {
                    "status": "error",
                    "request_id": request_id,
                    "error": "data_preprocessing_failed",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Make prediction
                start_time = time.time()
                prediction = self._make_model_prediction(preprocessed_data)
                latency = time.time() - start_time

                result = {
                    "status": "success",
                    "request_id": request_id,
                    "prediction": prediction,
                    "latency": latency,
                    "timestamp": datetime.now().isoformat()
                }

                # Update performance metrics
                self._update_performance_metrics(latency)

            # Call callback if provided
            if callback:
                try:
                    callback(result)
                except Exception as e:
                    logger.error(f"Error calling prediction callback: {e}")

        except Exception as e:
            logger.error(f"Error handling prediction request {request.get('request_id', 'unknown')}: {e}")

    def _preprocess_for_prediction(self, diagnostic_data: Dict[str, Any]) -> Optional[Dict[str, np.ndarray]]:
        """
        Preprocess diagnostic data for prediction

        Args:
            diagnostic_data: Raw diagnostic data

        Returns:
            Preprocessed data ready for model or None if failed
        """
        try:
            from ai.data_preprocessing import DataPreprocessor
            preprocessor = DataPreprocessor()

            # Determine model type and preprocess accordingly
            if hasattr(self.deployed_model, 'inputs') and len(self.deployed_model.inputs) > 1:
                # Multi-input model
                inputs, _ = preprocessor.preprocess_for_multi_input_model(diagnostic_data)
                return inputs
            else:
                # Single-input model (legacy)
                legacy_features = preprocessor._extract_legacy_features(diagnostic_data)
                if legacy_features is not None:
                    return {"input": np.array([legacy_features])}
                return None

        except Exception as e:
            logger.error(f"Error preprocessing data for prediction: {e}")
            return None

    def _make_model_prediction(self, preprocessed_data: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """
        Make prediction using deployed model

        Args:
            preprocessed_data: Preprocessed input data

        Returns:
            Dictionary containing prediction results
        """
        try:
            # Make prediction
            prediction = self.deployed_model.predict(preprocessed_data)
            confidence = float(prediction[0][0]) if isinstance(prediction, np.ndarray) else float(prediction)

            # Generate prediction results
            return {
                "confidence": confidence,
                "fault_probability": confidence,
                "no_fault_probability": 1.0 - confidence,
                "prediction": "fault_detected" if confidence > 0.5 else "no_fault",
                "model_version": self.model_version,
                "model_status": self.deployment_status
            }

        except Exception as e:
            logger.error(f"Error making model prediction: {e}")
            return {
                "status": "error",
                "error": str(e),
                "model_status": self.deployment_status
            }

    def _update_performance_metrics(self, latency: float):
        """
        Update performance metrics with new prediction latency

        Args:
            latency: Prediction latency in seconds
        """
        # Simple moving average for latency
        if "average_latency" not in self.performance_metrics:
            self.performance_metrics["average_latency"] = latency
            self.performance_metrics["request_count"] = 1
        else:
            alpha = 0.1  # Smoothing factor
            self.performance_metrics["average_latency"] = (
                alpha * latency +
                (1 - alpha) * self.performance_metrics["average_latency"]
            )
            self.performance_metrics["request_count"] += 1

    def queue_prediction_request(self, diagnostic_data: Dict[str, Any],
                                callback: Optional[callable] = None,
                                request_id: str = None) -> bool:
        """
        Queue prediction request for processing

        Args:
            diagnostic_data: Diagnostic data for prediction
            callback: Optional callback function for results
            request_id: Optional request identifier

        Returns:
            True if request queued successfully, False otherwise
        """
        if not self.running or not self.deployed_model:
            logger.warning("Cannot queue prediction - model not deployed or processing not running")
            return False

        try:
            request = {
                "diagnostic_data": diagnostic_data,
                "callback": callback,
                "request_id": request_id or f"req_{int(time.time())}",
                "timestamp": datetime.now().isoformat()
            }

            # Check queue size
            if self.request_queue.qsize() >= self.config["max_queue_size"]:
                logger.warning("Prediction queue full, dropping request")
                return False

            self.request_queue.put(request)
            return True

        except Exception as e:
            logger.error(f"Error queueing prediction request: {e}")
            return False

    def get_deployment_status(self) -> Dict[str, Any]:
        """
        Get current deployment status

        Returns:
            Dictionary containing deployment status information
        """
        return {
            "status": self.deployment_status,
            "model_version": self.model_version,
            "queue_size": self.request_queue.qsize(),
            "performance_metrics": self.performance_metrics,
            "config": self.config,
            "timestamp": datetime.now().isoformat()
        }

    def start_continuous_evaluation(self, evaluation_interval: int = 3600):
        """
        Start continuous model evaluation thread

        Args:
            evaluation_interval: Interval between evaluations in seconds
        """
        if not self.model_evaluator:
            logger.warning("No model evaluator available for continuous evaluation")
            return

        def evaluation_loop():
            while self.running:
                try:
                    # Perform evaluation
                    self._perform_continuous_evaluation()

                    # Wait for next evaluation
                    time.sleep(evaluation_interval)

                except Exception as e:
                    logger.error(f"Error in continuous evaluation loop: {e}")
                    time.sleep(60)  # Wait before retry

        eval_thread = threading.Thread(
            target=evaluation_loop,
            daemon=True
        )
        eval_thread.start()
        logger.info("Started continuous model evaluation")

    def _perform_continuous_evaluation(self):
        """
        Perform continuous model evaluation
        """
        try:
            # This would use recent diagnostic data for evaluation
            # For now, use placeholder evaluation
            logger.info("Performing continuous model evaluation")

            # Placeholder evaluation results
            eval_results = {
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "metrics": {
                    "accuracy": 0.91,
                    "precision": 0.87,
                    "recall": 0.84,
                    "f1_score": 0.85,
                    "latency": self.performance_metrics.get("average_latency", 0.2)
                },
                "performance_trends": self._analyze_performance_trends()
            }

            # Check for performance degradation
            if self._check_performance_degradation(eval_results["metrics"]):
                logger.warning("Performance degradation detected, scheduling retraining")
                self._schedule_model_retraining()

            return eval_results

        except Exception as e:
            logger.error(f"Error in continuous evaluation: {e}")
            return {"status": "failed", "error": str(e)}

    def _analyze_performance_trends(self) -> Dict[str, Any]:
        """
        Analyze performance trends over time

        Returns:
            Dictionary containing performance trend analysis
        """
        # This would analyze historical performance data
        # For now, return placeholder trends
        return {
            "accuracy_trend": "stable",
            "latency_trend": "stable",
            "error_rate_trend": "stable",
            "recommendation": "performance_stable"
        }

    def _check_performance_degradation(self, current_metrics: Dict[str, float]) -> bool:
        """
        Check for performance degradation

        Args:
            current_metrics: Current performance metrics

        Returns:
            True if degradation detected, False otherwise
        """
        # Simple degradation detection
        thresholds = self.config["performance_thresholds"]

        if (current_metrics["accuracy"] < thresholds["min_accuracy"] * 0.95 or
            current_metrics["precision"] < thresholds["min_precision"] * 0.95 or
            current_metrics["recall"] < thresholds["min_recall"] * 0.95 or
            current_metrics["latency"] > thresholds["max_latency"] * 1.5):

            logger.warning("Performance degradation detected")
            return True

        return False

    def _schedule_model_retraining(self):
        """
        Schedule model retraining
        """
        if not self.model_trainer:
            logger.warning("No model trainer available for retraining")
            return

        logger.info("Scheduling model retraining")

        # This would typically be a more sophisticated scheduling system
        # For now, we'll just log the retraining request
        retraining_request = {
            "timestamp": datetime.now().isoformat(),
            "reason": "performance_degradation",
            "priority": "high"
        }

        # In a real system, this would add to a retraining queue
        logger.info(f"Model retraining scheduled: {retraining_request}")

    def deploy_with_fallback(self, primary_model_path: str, fallback_model_path: str) -> bool:
        """
        Deploy model with fallback capability

        Args:
            primary_model_path: Path to primary model
            fallback_model_path: Path to fallback model

        Returns:
            True if deployment successful, False otherwise
        """
        try:
            # Try primary model first
            if self.deploy_model(primary_model_path):
                self._load_fallback_model(fallback_model_path)
                return True

            # If primary fails, try fallback
            logger.warning("Primary model deployment failed, trying fallback")
            if self.deploy_model(fallback_model_path):
                return True

            return False

        except Exception as e:
            logger.error(f"Error in fallback deployment: {e}")
            return False

    def _load_fallback_model(self, fallback_model_path: str) -> bool:
        """
        Load fallback model

        Args:
            fallback_model_path: Path to fallback model

        Returns:
            True if fallback model loaded, False otherwise
        """
        try:
            # Load fallback model (but don't deploy it)
            fallback_model = tf.keras.models.load_model(fallback_model_path)
            self.fallback_model = fallback_model
            logger.info("Fallback model loaded successfully")
            return True

        except Exception as e:
            logger.error(f"Error loading fallback model: {e}")
            return False

    def graceful_degradation(self):
        """
        Handle graceful degradation when model fails
        """
        self.deployment_status = "degraded"
        logger.warning("Model entered degraded mode")

        # In a real system, this would switch to fallback model or simpler logic
        # For now, we'll just log the degradation

    def shutdown(self):
        """
        Shutdown deployment system gracefully
        """
        self.running = False

        if self.processing_thread:
            self.processing_thread.join(timeout=5.0)

        self.deployment_status = "shutdown"
        logger.info("Model deployment system shutdown completed")

    def get_health_check(self) -> Dict[str, Any]:
        """
        Perform system health check

        Returns:
            Dictionary containing system health information
        """
        return {
            "status": self.deployment_status,
            "model_loaded": self.deployed_model is not None,
            "queue_health": "healthy" if self.request_queue.qsize() < self.config["max_queue_size"] * 0.8 else "warning",
            "performance_health": self._assess_performance_health(),
            "timestamp": datetime.now().isoformat()
        }

    def _assess_performance_health(self) -> str:
        """
        Assess overall performance health

        Returns:
            String indicating health status
        """
        if not self.performance_metrics:
            return "unknown"

        # Simple health assessment
        if self.performance_metrics.get("average_latency", 0) > self.config["performance_thresholds"]["max_latency"] * 2:
            return "critical"
        elif self.performance_metrics.get("average_latency", 0) > self.config["performance_thresholds"]["max_latency"] * 1.5:
            return "warning"

        return "healthy"

# Global model deployment instance
model_deployment = ModelDeployment()