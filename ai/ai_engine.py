#!/usr/bin/env python3
"""
AI Engine Module
Core AI functionality for fault prediction and diagnostic analysis
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import ML libraries
try:
    import tensorflow as tf
    import numpy as np
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logging.warning("ML libraries not available, AI engine will run in limited mode")

from ai.data_processor import DataProcessor

logger = logging.getLogger(__name__)

class AIEngine:
    """
    Core AI engine for diagnostic analysis and fault prediction
    """

    def __init__(self, data_processor: Optional[DataProcessor] = None):
        """
        Initialize AI engine

        Args:
            data_processor: Data processor instance for data access
        """
        self.data_processor = data_processor or DataProcessor()
        self.model_loaded = False
        self.scaler = StandardScaler()
        self.fault_prediction_model = None
        self._initialize_ai_components()

    def _initialize_ai_components(self):
        """Initialize AI components and load models"""
        if ML_AVAILABLE:
            try:
                # Initialize TensorFlow model
                self.fault_prediction_model = self._build_fault_prediction_model()
                self.model_loaded = True
                logger.info("AI engine initialized with TensorFlow model")
            except Exception as e:
                logger.error(f"Error initializing AI model: {e}")
                self.model_loaded = False
        else:
            logger.warning("AI engine running in limited mode (ML libraries not available)")

    def _build_fault_prediction_model(self) -> tf.keras.Model:
        """
        Build fault prediction neural network model

        Returns:
            Compiled TensorFlow Keras model
        """
        # Simple feedforward neural network for fault prediction
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=(32,)),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])

        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )

        return model

    def train_fault_prediction_model(self, training_data: List[Dict[str, Any]]):
        """
        Train fault prediction model using historical diagnostic data

        Args:
            training_data: List of diagnostic sessions for training
        """
        if not ML_AVAILABLE or not self.model_loaded:
            logger.warning("Cannot train model - ML libraries not available")
            return False

        try:
            # Prepare training data
            X, y = self._prepare_training_data(training_data)

            if X.size == 0 or y.size == 0:
                logger.warning("No valid training data available")
                return False

            # Split data into training and validation sets
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Train model
            history = self.fault_prediction_model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=50,
                batch_size=32,
                verbose=1
            )

            # Evaluate model
            loss, accuracy = self.fault_prediction_model.evaluate(X_val, y_val, verbose=0)
            logger.info(f"Model training completed - Validation accuracy: {accuracy:.4f}")

            return True

        except Exception as e:
            logger.error(f"Error training fault prediction model: {e}")
            return False

    def _prepare_training_data(self, training_data: List[Dict[str, Any]]) -> tuple:
        """
        Prepare training data for model training

        Args:
            training_data: List of diagnostic sessions

        Returns:
            Tuple of (features, labels) numpy arrays
        """
        features = []
        labels = []

        for session in training_data:
            try:
                # Extract features from diagnostic data
                session_features = self._extract_features(session)

                # Determine label (1 if faults detected, 0 if no faults)
                has_faults = len(session.get('dtc_codes', [])) > 0
                label = 1 if has_faults else 0

                if session_features is not None:
                    features.append(session_features)
                    labels.append(label)

            except Exception as e:
                logger.warning(f"Error processing session {session.get('session_id', 'unknown')}: {e}")
                continue

        if not features:
            return np.array([]), np.array([])

        # Convert to numpy arrays
        X = np.array(features)
        y = np.array(labels)

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        return X_scaled, y

    def _extract_features(self, session: Dict[str, Any]) -> Optional[List[float]]:
        """
        Extract features from a diagnostic session

        Args:
            session: Diagnostic session data

        Returns:
            List of feature values or None if extraction fails
        """
        try:
            # Initialize feature vector (32 features)
            features = [0.0] * 32

            # Feature 0-9: DTC pattern features
            dtc_codes = session.get('dtc_codes', [])
            features[0] = len(dtc_codes)  # Number of DTCs
            features[1] = 1.0 if any('P0' in code for code in dtc_codes) else 0.0  # Powertrain DTCs
            features[2] = 1.0 if any('P1' in code for code in dtc_codes) else 0.0  # Manufacturer-specific DTCs

            # Feature 10-19: Live parameter features
            live_params = session.get('live_parameters', {})
            features[10] = live_params.get('engine_rpm', {}).get('value', 0.0) / 8000.0  # Normalized RPM
            features[11] = live_params.get('coolant_temp', {}).get('value', 0.0) / 150.0  # Normalized temp
            features[12] = live_params.get('throttle_position', {}).get('value', 0.0) / 100.0  # Normalized %

            # Feature 20-29: Vehicle context features
            vehicle_info = session.get('vehicle_context', {})
            features[20] = float(vehicle_info.get('year', 2000)) / 2025.0  # Normalized year
            features[21] = 1.0 if vehicle_info.get('make', '').lower() == 'chevrolet' else 0.0
            features[22] = 1.0 if vehicle_info.get('make', '').lower() == 'toyota' else 0.0

            # Feature 30-31: Session metadata
            features[30] = session.get('session_duration', 0.0) / 3600.0  # Normalized hours
            features[31] = 1.0 if session.get('device_type', '').lower() == 'j2534' else 0.0

            return features

        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return None

    def predict_faults(self, diagnostic_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict potential faults based on diagnostic data

        Args:
            diagnostic_data: Current diagnostic session data

        Returns:
            Dictionary containing prediction results
        """
        if not ML_AVAILABLE or not self.model_loaded:
            logger.warning("Cannot make predictions - ML libraries not available")
            return {
                'predictions': [],
                'confidence': 0.0,
                'model_status': 'unavailable',
                'timestamp': datetime.now().isoformat()
            }

        try:
            # Extract features from current diagnostic data
            features = self._extract_features(diagnostic_data)

            if features is None:
                return {
                    'predictions': [],
                    'confidence': 0.0,
                    'model_status': 'feature_extraction_failed',
                    'timestamp': datetime.now().isoformat()
                }

            # Scale features using the same scaler
            features_scaled = self.scaler.transform([features])

            # Make prediction
            prediction = self.fault_prediction_model.predict(features_scaled, verbose=0)
            confidence = float(prediction[0][0])

            # Generate prediction results
            results = {
                'predictions': self._generate_predictions(confidence, diagnostic_data),
                'confidence': confidence,
                'model_status': 'success',
                'timestamp': datetime.now().isoformat()
            }

            return results

        except Exception as e:
            logger.error(f"Error making fault prediction: {e}")
            return {
                'predictions': [],
                'confidence': 0.0,
                'model_status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

    def _generate_predictions(self, confidence: float, diagnostic_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate specific fault predictions based on confidence and diagnostic data

        Args:
            confidence: Prediction confidence score
            diagnostic_data: Current diagnostic session data

        Returns:
            List of prediction dictionaries
        """
        predictions = []

        # Basic threshold-based prediction
        if confidence > 0.8:
            predictions.append({
                'type': 'critical_fault',
                'description': 'High probability of critical system fault',
                'severity': 'critical',
                'confidence': confidence,
                'suggested_action': 'Immediate diagnostic inspection recommended'
            })
        elif confidence > 0.6:
            predictions.append({
                'type': 'potential_issue',
                'description': 'Potential system issue detected',
                'severity': 'warning',
                'confidence': confidence,
                'suggested_action': 'Monitor system and perform detailed diagnostics'
            })
        else:
            predictions.append({
                'type': 'normal_operation',
                'description': 'System operating within normal parameters',
                'severity': 'info',
                'confidence': 1.0 - confidence,
                'suggested_action': 'Continue normal operation'
            })

        # Add DTC-specific predictions if available
        dtc_codes = diagnostic_data.get('dtc_codes', [])
        if dtc_codes:
            for dtc in dtc_codes:
                predictions.append({
                    'type': 'dtc_analysis',
                    'description': f'DTC {dtc} requires attention',
                    'severity': 'high',
                    'confidence': 0.95,
                    'suggested_action': f'Address DTC {dtc} according to service manual'
                })

        return predictions

    def analyze_diagnostic_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive analysis of a diagnostic session with AI insights

        Args:
            session_data: Complete diagnostic session data

        Returns:
            Dictionary containing AI analysis results
        """
        analysis_results = {
            'session_id': session_data.get('session_id', 'unknown'),
            'timestamp': datetime.now().isoformat(),
            'ai_analysis': {
                'fault_predictions': [],
                'health_score': 0.0,
                'maintenance_recommendations': [],
                'performance_metrics': {}
            }
        }

        # Store session data for future training
        if self.data_processor:
            session_id = self.data_processor.store_diagnostic_session(session_data)
            analysis_results['session_id'] = session_id

        # Make fault predictions
        prediction_results = self.predict_faults(session_data)
        analysis_results['ai_analysis']['fault_predictions'] = prediction_results['predictions']

        # Calculate health score
        analysis_results['ai_analysis']['health_score'] = self._calculate_health_score(
            session_data, prediction_results['confidence']
        )

        # Generate maintenance recommendations
        analysis_results['ai_analysis']['maintenance_recommendations'] = self._generate_recommendations(
            session_data, prediction_results
        )

        # Calculate performance metrics
        analysis_results['ai_analysis']['performance_metrics'] = self._calculate_performance_metrics(session_data)

        return analysis_results

    def _calculate_health_score(self, session_data: Dict[str, Any], prediction_confidence: float) -> float:
        """
        Calculate overall vehicle health score

        Args:
            session_data: Diagnostic session data
            prediction_confidence: AI prediction confidence

        Returns:
            Health score between 0.0 (critical) and 1.0 (excellent)
        """
        # Base score calculation
        base_score = 1.0 - prediction_confidence  # Inverse of fault prediction

        # Adjust based on DTC count
        dtc_count = len(session_data.get('dtc_codes', []))
        dtc_penalty = min(dtc_count * 0.1, 0.8)  # Max 80% penalty for many DTCs
        adjusted_score = max(0.0, base_score - dtc_penalty)

        # Adjust based on live parameters (simplified)
        live_params = session_data.get('live_parameters', {})
        if 'coolant_temp' in live_params:
            temp = live_params['coolant_temp'].get('value', 90.0)
            if temp > 110.0:  # Overheating
                adjusted_score = max(0.0, adjusted_score - 0.3)

        return round(adjusted_score, 2)

    def _generate_recommendations(self, session_data: Dict[str, Any], prediction_results: Dict[str, Any]) -> List[str]:
        """
        Generate maintenance recommendations based on analysis

        Args:
            session_data: Diagnostic session data
            prediction_results: AI prediction results

        Returns:
            List of maintenance recommendations
        """
        recommendations = []

        # Basic recommendations based on predictions
        for prediction in prediction_results['predictions']:
            if prediction['severity'] in ['critical', 'high']:
                recommendations.append(f"URGENT: {prediction['suggested_action']}")
            elif prediction['severity'] == 'warning':
                recommendations.append(f"RECOMMENDED: {prediction['suggested_action']}")

        # Vehicle-specific recommendations
        vehicle_info = session_data.get('vehicle_context', {})
        vehicle_age = datetime.now().year - vehicle_info.get('year', 2000)
        if vehicle_age > 5:
            recommendations.append("RECOMMENDED: Perform comprehensive vehicle inspection due to age")

        # DTC-specific recommendations
        dtc_codes = session_data.get('dtc_codes', [])
        if dtc_codes:
            recommendations.append(f"RECOMMENDED: Clear DTCs {', '.join(dtc_codes)} after addressing root causes")

        return recommendations

    def _calculate_performance_metrics(self, session_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate performance metrics from diagnostic data

        Args:
            session_data: Diagnostic session data

        Returns:
            Dictionary of performance metrics
        """
        metrics = {}
        live_params = session_data.get('live_parameters', {})

        # Engine performance metrics
        if 'engine_rpm' in live_params and 'throttle_position' in live_params:
            rpm = live_params['engine_rpm'].get('value', 0.0)
            throttle = live_params['throttle_position'].get('value', 0.0)
            metrics['engine_responsiveness'] = min(rpm / max(throttle, 1.0), 10.0)  # Simplified metric

        # Cooling system metrics
        if 'coolant_temp' in live_params:
            temp = live_params['coolant_temp'].get('value', 90.0)
            metrics['cooling_efficiency'] = max(0.0, 1.0 - abs(temp - 90.0) / 50.0)

        return metrics

# Global AI engine instance
ai_engine = AIEngine()