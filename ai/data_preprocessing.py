#!/usr/bin/env python3
"""
AI Data Preprocessing Module
Advanced data preprocessing pipeline for machine learning
"""

import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.feature_selection import SelectKBest, f_classif

# Import ML libraries
try:
    import tensorflow as tf
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logging.warning("ML libraries not available, preprocessing will be limited")

logger = logging.getLogger(__name__)

class DataPreprocessor:
    """
    Advanced data preprocessing pipeline for automotive diagnostics
    """

    def __init__(self):
        """
        Initialize data preprocessor with scaling and normalization pipelines
        """
        self.dtc_scaler = StandardScaler()
        self.params_scaler = RobustScaler()
        self.vehicle_scaler = MinMaxScaler()

        # Feature selection and preprocessing pipelines
        self._initialize_pipelines()

        # Vehicle-specific normalization ranges
        self.vehicle_ranges = self._load_vehicle_ranges()

    def _initialize_pipelines(self):
        """Initialize preprocessing pipelines"""
        # DTC features pipeline
        self.dtc_pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='constant', fill_value=0)),
            ('scaler', StandardScaler())
        ])

        # Live parameters pipeline
        self.params_pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', RobustScaler())
        ])

        # Vehicle context pipeline
        self.vehicle_pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('scaler', MinMaxScaler())
        ])

        # Feature selection
        self.feature_selector = SelectKBest(score_func=f_classif, k=10)

    def _load_vehicle_ranges(self) -> Dict[str, Dict[str, Dict[str, Tuple[float, float]]]]:
        """
        Load vehicle-specific parameter ranges for normalization

        Returns:
            Dictionary of vehicle parameter ranges
        """
        # This would typically be loaded from a configuration file or database
        # For now, we'll use some common ranges
        return {
            'default': {
                'engine_rpm': (0, 8000),
                'coolant_temp': (40, 120),
                'throttle_position': (0, 100),
                'engine_load': (0, 100),
                'intake_temp': (-40, 150),
                'maf_airflow': (0, 1000),
                'fuel_pressure': (0, 1000),
                'oil_pressure': (0, 800),
                'battery_voltage': (9, 16),
                'speed': (0, 250),
                'lambda': (0.5, 1.5)
            },
            'chevrolet': {
                'engine_rpm': (0, 7500),
                'coolant_temp': (50, 115),
                'throttle_position': (0, 100),
                'engine_load': (0, 100),
                'intake_temp': (-30, 140),
                'maf_airflow': (0, 800),
                'fuel_pressure': (0, 800),
                'oil_pressure': (0, 700),
                'battery_voltage': (10, 15),
                'speed': (0, 220),
                'lambda': (0.5, 1.5)
            },
            'toyota': {
                'engine_rpm': (0, 7000),
                'coolant_temp': (45, 110),
                'throttle_position': (0, 100),
                'engine_load': (0, 100),
                'intake_temp': (-35, 135),
                'maf_airflow': (0, 900),
                'fuel_pressure': (0, 900),
                'oil_pressure': (0, 750),
                'battery_voltage': (10, 15),
                'speed': (0, 200),
                'lambda': (0.5, 1.5)
            }
        }

    def preprocess_for_multi_input_model(self, session_data: Dict[str, Any]) -> Tuple[Dict[str, np.ndarray], np.ndarray]:
        """
        Preprocess data for multi-input model architecture

        Args:
            session_data: Diagnostic session data

        Returns:
            Tuple of (input_dict, label) where input_dict contains separate arrays for each input branch
        """
        try:
            # Extract and preprocess DTC features
            dtc_features = self._extract_dtc_features(session_data)

            # Extract and preprocess live parameters
            param_features = self._extract_parameter_features(session_data)

            # Extract and preprocess vehicle context
            vehicle_features = self._extract_vehicle_features(session_data)

            # Determine label
            # Check for explicit label from training data (for Multi-Class/Falsification training)
            if 'label' in session_data:
                 # Ensure it's a one-hot vector or integer class
                 raw_label = session_data['label']
                 if isinstance(raw_label, (list, np.ndarray)):
                     label = np.array(raw_label)
                 else:
                     # If it's an integer class, we might need to one-hot encode it later
                     # But for now, let's assume the trainer handles sparse or we return it as is
                     # The trainer expects numpy array
                     label = int(raw_label)
            else:
                # Default Binary Logic
                has_dtcs = len(session_data.get('dtc_codes', [])) > 0
                
                # Check for Lean Condition (Lambda > 1.1)
                # We need to access the raw lambda value, not normalized
                live_params = session_data.get('live_parameters', {})
                lambda_val = live_params.get('lambda', {}).get('value', 1.0)
                is_lean = lambda_val > 1.1
                
                label = 1 if (has_dtcs or is_lean) else 0

            return {
                'dtc_input': dtc_features,
                'params_input': param_features,
                'vehicle_input': vehicle_features
            }, np.array([label])

        except Exception as e:
            logger.error(f"Error preprocessing data for multi-input model: {e}")
            return {}, np.array([])

    def _extract_dtc_features(self, session_data: Dict[str, Any]) -> np.ndarray:
        """
        Extract and preprocess DTC-related features

        Args:
            session_data: Diagnostic session data

        Returns:
            Array of DTC features
        """
        dtc_codes = session_data.get('dtc_codes', [])
        dtc_features = np.zeros(10)  # 10 DTC-related features

        # Feature 0: Number of DTCs
        dtc_features[0] = len(dtc_codes)

        # Feature 1: Has powertrain DTCs
        dtc_features[1] = 1.0 if any('P0' in str(code) for code in dtc_codes) else 0.0

        # Feature 2: Has manufacturer-specific DTCs
        dtc_features[2] = 1.0 if any('P1' in str(code) for code in dtc_codes) else 0.0

        # Feature 3: Has chassis DTCs
        dtc_features[3] = 1.0 if any('C' in str(code) for code in dtc_codes) else 0.0

        # Feature 4: Has body DTCs
        dtc_features[4] = 1.0 if any('B' in str(code) for code in dtc_codes) else 0.0

        # Feature 5: Has network DTCs
        dtc_features[5] = 1.0 if any('U' in str(code) for code in dtc_codes) else 0.0

        # Feature 6: Average DTC severity (simplified)
        severity_scores = []
        for code in dtc_codes:
            if 'P0' in str(code):
                severity_scores.append(0.8)  # High severity
            elif 'P1' in str(code):
                severity_scores.append(0.6)  # Medium severity
            else:
                severity_scores.append(0.4)  # Low severity

        dtc_features[6] = np.mean(severity_scores) if severity_scores else 0.0

        # Feature 7: DTC diversity score
        dtc_types = set()
        for code in dtc_codes:
            if 'P0' in str(code):
                dtc_types.add('powertrain')
            elif 'P1' in str(code):
                dtc_types.add('manufacturer')
            elif 'C' in str(code):
                dtc_types.add('chassis')
            elif 'B' in str(code):
                dtc_types.add('body')
            elif 'U' in str(code):
                dtc_types.add('network')

        dtc_features[7] = len(dtc_types) / 5.0  # Normalized diversity

        # Feature 8: Has critical DTCs (P03XX, P05XX, etc.)
        critical_patterns = ['P03', 'P05', 'P07', 'P01', 'P02']
        dtc_features[8] = 1.0 if any(any(pattern in str(code) for pattern in critical_patterns) for code in dtc_codes) else 0.0

        # Feature 9: DTC count severity (log scale)
        dtc_features[9] = np.log1p(len(dtc_codes)) / np.log1p(10)  # Normalized log count

        # Apply DTC preprocessing pipeline
        return self.dtc_pipeline.transform([dtc_features])[0]

    def _extract_parameter_features(self, session_data: Dict[str, Any]) -> np.ndarray:
        """
        Extract and preprocess live parameter features with vehicle-specific normalization
        
        Args:
            session_data: Diagnostic session data
            
        Returns:
            Array of parameter features
        """
        live_params = session_data.get('live_parameters', {})
        vehicle_info = session_data.get('vehicle_context', {})
        param_features = np.zeros(22)  # 22 parameter features

        # Get vehicle-specific ranges
        make = vehicle_info.get('make', '').lower()
        ranges = self.vehicle_ranges.get(make, self.vehicle_ranges['default'])

        # Feature 0: Engine RPM (normalized)
        rpm = live_params.get('engine_rpm', {}).get('value', 0.0)
        rpm_min, rpm_max = ranges['engine_rpm']
        param_features[0] = self._normalize_value(rpm, rpm_min, rpm_max)

        # Feature 1: Coolant temperature (normalized)
        temp = live_params.get('coolant_temp', {}).get('value', 90.0)
        temp_min, temp_max = ranges['coolant_temp']
        param_features[1] = self._normalize_value(temp, temp_min, temp_max)

        # Feature 2: Throttle position (normalized)
        throttle = live_params.get('throttle_position', {}).get('value', 0.0)
        param_features[2] = throttle / 100.0  # Already percentage

        # Feature 3: Engine load (normalized)
        load = live_params.get('engine_load', {}).get('value', 0.0)
        param_features[3] = load / 100.0  # Already percentage

        # Feature 4: Intake air temperature (normalized)
        intake_temp = live_params.get('intake_temp', {}).get('value', 20.0)
        temp_min, temp_max = ranges['intake_temp']
        param_features[4] = self._normalize_value(intake_temp, temp_min, temp_max)

        # Feature 5: MAF airflow (normalized)
        maf = live_params.get('maf_airflow', {}).get('value', 0.0)
        maf_min, maf_max = ranges['maf_airflow']
        param_features[5] = self._normalize_value(maf, maf_min, maf_max)

        # Feature 6: Fuel pressure (normalized)
        fuel_pressure = live_params.get('fuel_pressure', {}).get('value', 0.0)
        pressure_min, pressure_max = ranges['fuel_pressure']
        param_features[6] = self._normalize_value(fuel_pressure, pressure_min, pressure_max)

        # Feature 7: Oil pressure (normalized)
        oil_pressure = live_params.get('oil_pressure', {}).get('value', 0.0)
        pressure_min, pressure_max = ranges['oil_pressure']
        param_features[7] = self._normalize_value(oil_pressure, pressure_min, pressure_max)

        # Feature 8: Battery voltage (normalized)
        voltage = live_params.get('battery_voltage', {}).get('value', 12.0)
        volt_min, volt_max = ranges['battery_voltage']
        param_features[8] = self._normalize_value(voltage, volt_min, volt_max)

        # Feature 9: Vehicle speed (normalized)
        speed = live_params.get('speed', {}).get('value', 0.0)
        speed_min, speed_max = ranges['speed']
        param_features[9] = self._normalize_value(speed, speed_min, speed_max)
        
        # Feature 10: Lambda (normalized) - GOVERNING VARIABLE
        lambda_val = live_params.get('lambda', {}).get('value', 1.0)
        lambda_min, lambda_max = ranges.get('lambda', (0.5, 1.5))
        param_features[10] = self._normalize_value(lambda_val, lambda_min, lambda_max)

        # Feature 11-21: Parameter anomaly detection
        # Calculate how far each parameter is from expected range
        for i, (param_name, (param_min, param_max)) in enumerate(ranges.items()):
            if i >= 11:  # Only use first 11 parameters for anomaly features
                break
            
            param_value = live_params.get(param_name, {}).get('value', 0.0)
            
            # Calculate anomaly score (distance from center of range)
            range_center = (param_min + param_max) / 2
            # Handle zero range
            if param_max == param_min:
                divisor = 1.0
            else:
                divisor = (param_max - param_min) / 2
                
            anomaly_score = abs(param_value - range_center) / divisor
            param_features[11 + i] = min(anomaly_score, 2.0)  # Cap at 2.0

        # Apply parameters preprocessing pipeline
        return self.params_pipeline.transform([param_features])[0]

    def _extract_vehicle_features(self, session_data: Dict[str, Any]) -> np.ndarray:
        """
        Extract and preprocess vehicle context features

        Args:
            session_data: Diagnostic session data

        Returns:
            Array of vehicle features
        """
        vehicle_info = session_data.get('vehicle_context', {})
        session_data_main = session_data.get('session_data', {})
        vehicle_features = np.zeros(5)  # 5 vehicle context features

        # Feature 0: Vehicle age (normalized)
        current_year = datetime.now().year
        vehicle_year = vehicle_info.get('year', current_year)
        vehicle_age = current_year - vehicle_year
        vehicle_features[0] = min(vehicle_age, 30) / 30.0  # Normalized to 30 years max

        # Feature 1: Make encoding (simplified)
        make = vehicle_info.get('make', '').lower()
        if 'chevrolet' in make:
            vehicle_features[1] = 0.2
        elif 'toyota' in make:
            vehicle_features[1] = 0.4
        elif 'ford' in make:
            vehicle_features[1] = 0.6
        elif 'bmw' in make:
            vehicle_features[1] = 0.8
        else:
            vehicle_features[1] = 0.1  # Other makes

        # Feature 2: Engine type encoding
        engine_type = vehicle_info.get('engine_type', '').lower()
        if 'diesel' in engine_type:
            vehicle_features[2] = 0.8
        elif 'hybrid' in engine_type:
            vehicle_features[2] = 0.6
        elif 'electric' in engine_type:
            vehicle_features[2] = 0.4
        else:  # Default to gasoline
            vehicle_features[2] = 0.2

        # Feature 3: Session duration (normalized)
        duration = session_data_main.get('session_duration', 0.0)
        vehicle_features[3] = min(duration, 3600) / 3600.0  # Normalized to 1 hour max

        # Feature 4: Device type encoding
        device_type = session_data.get('device_type', '').lower()
        if 'j2534' in device_type:
            vehicle_features[4] = 0.8
        elif 'obd2' in device_type:
            vehicle_features[4] = 0.6
        elif 'mock' in device_type:
            vehicle_features[4] = 0.2
        else:
            vehicle_features[4] = 0.4

        # Apply vehicle preprocessing pipeline
        return self.vehicle_pipeline.transform([vehicle_features])[0]

    def _normalize_value(self, value: float, min_val: float, max_val: float) -> float:
        """
        Normalize value to 0-1 range with bounds checking

        Args:
            value: Value to normalize
            min_val: Minimum expected value
            max_val: Maximum expected value

        Returns:
            Normalized value between 0.0 and 1.0
        """
        if max_val == min_val:
            return 0.5  # Avoid division by zero

        # Handle edge cases
        if value < min_val:
            return 0.0
        elif value > max_val:
            return 1.0

        return (value - min_val) / (max_val - min_val)

    def create_time_series_data(self, session_data: Dict[str, Any], window_size: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create time series data from diagnostic sessions

        Args:
            session_data: Diagnostic session data
            window_size: Size of time window for sequences

        Returns:
            Tuple of (time_series_data, labels)
        """
        try:
            # This would process live data into time series format
            # For now, return placeholder data
            num_samples = len(session_data.get('live_data', []))
            if num_samples < window_size:
                return np.zeros((1, window_size, 20)), np.array([0])

            # Create synthetic time series data
            time_series = np.random.rand(num_samples, 20).astype(np.float32)
            labels = np.random.randint(0, 2, size=num_samples)

            # Reshape into time windows
            X = []
            y = []
            for i in range(num_samples - window_size + 1):
                X.append(time_series[i:i+window_size])
                y.append(labels[i+window_size-1])

            return np.array(X), np.array(y)

        except Exception as e:
            logger.error(f"Error creating time series data: {e}")
            return np.zeros((1, window_size, 20)), np.array([0])

    def preprocess_batch_data(self, batch_data: List[Dict[str, Any]], model_type: str = 'multi_input') -> Tuple[Union[Dict[str, np.ndarray], np.ndarray], np.ndarray]:
        """
        Preprocess batch of diagnostic sessions for training

        Args:
            batch_data: List of diagnostic session dictionaries
            model_type: Type of model ('simple', 'multi_input', 'time_series')

        Returns:
            Tuple of (features, labels) ready for model training
        """
        if model_type == 'multi_input':
            # Process for multi-input model
            dtc_features = []
            param_features = []
            vehicle_features = []
            labels = []

            for session in batch_data:
                inputs, label = self.preprocess_for_multi_input_model(session)
                if label.size > 0:  # Only add valid data
                    dtc_features.append(inputs['dtc_input'])
                    param_features.append(inputs['params_input'])
                    vehicle_features.append(inputs['vehicle_input'])
                    labels.append(label[0])

            return {
                'dtc_input': np.array(dtc_features),
                'params_input': np.array(param_features),
                'vehicle_input': np.array(vehicle_features)
            }, np.array(labels)

        elif model_type == 'time_series':
            # Process for time series model
            all_X = []
            all_y = []

            for session in batch_data:
                X, y = self.create_time_series_data(session)
                all_X.append(X)
                all_y.append(y)

            return np.concatenate(all_X, axis=0), np.concatenate(all_y, axis=0)

        else:
            # Process for simple feedforward model (legacy compatibility)
            features = []
            labels = []

            for session in batch_data:
                # Use legacy feature extraction
                legacy_features = self._extract_legacy_features(session)
                if legacy_features is not None:
                    features.append(legacy_features)
                    has_faults = len(session.get('dtc_codes', [])) > 0
                    labels.append(1 if has_faults else 0)

            return np.array(features), np.array(labels)

    def _extract_legacy_features(self, session_data: Dict[str, Any]) -> Optional[np.ndarray]:
        """
        Extract features using legacy method for compatibility

        Args:
            session_data: Diagnostic session data

        Returns:
            Array of legacy features or None if extraction fails
        """
        try:
            features = np.zeros(32)  # Match original feature count

            # DTC features (first 10)
            dtc_codes = session_data.get('dtc_codes', [])
            features[0] = len(dtc_codes)
            features[1] = 1.0 if any('P0' in str(code) for code in dtc_codes) else 0.0
            features[2] = 1.0 if any('P1' in str(code) for code in dtc_codes) else 0.0

            # Live parameter features (next 10)
            live_params = session_data.get('live_parameters', {})
            features[10] = live_params.get('engine_rpm', {}).get('value', 0.0) / 8000.0
            features[11] = live_params.get('coolant_temp', {}).get('value', 0.0) / 150.0
            features[12] = live_params.get('throttle_position', {}).get('value', 0.0) / 100.0

            # Vehicle context features (next 10)
            vehicle_info = session_data.get('vehicle_context', {})
            features[20] = float(vehicle_info.get('year', 2000)) / 2025.0
            features[21] = 1.0 if vehicle_info.get('make', '').lower() == 'chevrolet' else 0.0
            features[22] = 1.0 if vehicle_info.get('make', '').lower() == 'toyota' else 0.0

            # Session metadata (last 2)
            features[30] = session_data.get('session_duration', 0.0) / 3600.0
            features[31] = 1.0 if session_data.get('device_type', '').lower() == 'j2534' else 0.0

            return features

        except Exception as e:
            logger.error(f"Error extracting legacy features: {e}")
            return None

# Global data preprocessor instance
data_preprocessor = DataPreprocessor()