#!/usr/bin/env python3
"""
AI Model Training Module
Comprehensive model training infrastructure for automotive diagnostics
"""

import logging
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union
import numpy as np

# Import ML libraries
try:
    import tensorflow as tf
    from tensorflow.keras.callbacks import CSVLogger, ReduceLROnPlateau
    from tensorflow.keras.utils import to_categorical
    from sklearn.model_selection import KFold
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logging.warning("ML libraries not available, model training will be limited")

from ai.model_architecture import ModelArchitecture, ModelType
from ai.data_preprocessing import DataPreprocessor
from ai.data_processor import DataProcessor

logger = logging.getLogger(__name__)

class ModelTrainer:
    """
    Comprehensive model training infrastructure for automotive diagnostics AI
    """

    def __init__(self, data_processor: Optional[DataProcessor] = None,
                 data_preprocessor: Optional[DataPreprocessor] = None):
        """
        Initialize model trainer

        Args:
            data_processor: Data processor instance
            data_preprocessor: Data preprocessor instance
        """
        self.data_processor = data_processor or DataProcessor()
        self.data_preprocessor = data_preprocessor or DataPreprocessor()
        self.model_architecture = ModelArchitecture()
        self.training_history = []
        self.current_model = None
        self.model_type = None

    def train_model(self, model_type: str = 'multi_input',
                   training_data_limit: int = 1000,
                   epochs: int = 100,
                   batch_size: int = 32,
                   use_cross_validation: bool = False,
                   validation_split: float = 0.2) -> Dict[str, Any]:
        """
        Train AI model with specified architecture

        Args:
            model_type: Type of model to train ('simple', 'multi_input', 'time_series')
            training_data_limit: Maximum number of sessions to use for training
            epochs: Number of training epochs
            batch_size: Batch size for training
            use_cross_validation: Whether to use cross-validation
            validation_split: Fraction of data to use for validation

        Returns:
            Dictionary containing training results and metrics
        """
        if not ML_AVAILABLE:
            logger.warning("Cannot train model - ML libraries not available")
            return {"status": "failed", "reason": "ml_libraries_unavailable"}

        start_time = time.time()
        training_results = {
            "status": "started",
            "model_type": model_type,
            "timestamp": datetime.now().isoformat(),
            "training_params": {
                "epochs": epochs,
                "batch_size": batch_size,
                "validation_split": validation_split,
                "use_cross_validation": use_cross_validation
            },
            "metrics": {},
            "history": {}
        }

        try:
            # Load training data
            logger.info(f"Loading training data (limit: {training_data_limit})")
            raw_training_data = self.data_processor.get_training_data(training_data_limit)

            if not raw_training_data:
                logger.warning("No training data available")
                training_results["status"] = "failed"
                training_results["reason"] = "no_training_data"
                return training_results

            # Preprocess data based on model type
            logger.info(f"Preprocessing data for {model_type} model")
            X, y = self.data_preprocessor.preprocess_batch_data(raw_training_data, model_type)

            if X is None or y is None or len(X) == 0 or len(y) == 0:
                logger.warning("No valid preprocessed data available")
                training_results["status"] = "failed"
                training_results["reason"] = "invalid_preprocessed_data"
                return training_results

            # Split data into training and validation sets
            if use_cross_validation:
                logger.info("Using cross-validation for model training")
                cv_results = self._cross_validate_model(X, y, model_type, epochs, batch_size)
                training_results.update(cv_results)
            else:
                logger.info(f"Splitting data with validation split: {validation_split}")
                X_train, X_val, y_train, y_val = self._split_data(X, y, validation_split)

                # Build model
                logger.info(f"Building {model_type} model architecture")
                model = self._build_model_for_type(model_type)

                if model is None:
                    training_results["status"] = "failed"
                    training_results["reason"] = "model_building_failed"
                    return training_results

                # Train model
                logger.info("Starting model training")
                history = self._train_model_with_data(
                    model, X_train, y_train, X_val, y_val,
                    epochs, batch_size
                )

                training_results["history"] = self._convert_history_to_dict(history.history)
                training_results["metrics"] = self._evaluate_model(model, X_val, y_val)

            # Save training results
            self.training_history.append(training_results)
            training_results["status"] = "completed"
            training_results["training_duration"] = time.time() - start_time

            logger.info(f"Model training completed successfully in {training_results['training_duration']:.2f} seconds")
            return training_results

        except Exception as e:
            logger.error(f"Error during model training: {e}")
            training_results["status"] = "failed"
            training_results["reason"] = str(e)
            training_results["error_details"] = str(e)
            return training_results

    def _build_model_for_type(self, model_type: str) -> Optional[tf.keras.Model]:
        """
        Build model based on specified type

        Args:
            model_type: Type of model to build

        Returns:
            Compiled TensorFlow model or None if failed
        """
        try:
            if model_type == 'multi_input':
                self.model_type = ModelType.MULTI_INPUT
                return self.model_architecture.build_multi_input_model()
            elif model_type == 'time_series':
                self.model_type = ModelType.TIME_SERIES
                return self.model_architecture.build_time_series_model()
            else:  # Default to enhanced feedforward
                self.model_type = ModelType.SIMPLE_FEEDFORWARD
                return self.model_architecture.build_simple_feedforward_model()

        except Exception as e:
            logger.error(f"Error building model: {e}")
            return None

    def _train_model_with_data(self, model: tf.keras.Model,
                              X_train: Union[Dict[str, np.ndarray], np.ndarray],
                              y_train: np.ndarray,
                              X_val: Union[Dict[str, np.ndarray], np.ndarray],
                              y_val: np.ndarray,
                              epochs: int, batch_size: int) -> tf.keras.callbacks.History:
        """
        Train model with given data

        Args:
            model: Model to train
            X_train: Training features
            y_train: Training labels
            X_val: Validation features
            y_val: Validation labels
            epochs: Number of epochs
            batch_size: Batch size

        Returns:
            Training history
        """
        # Create callbacks
        callbacks = self.model_architecture.get_training_callbacks()

        # Add additional callbacks
        callbacks.extend([
            CSVLogger('training_log.csv'),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.1,
                patience=5,
                verbose=1,
                min_lr=1e-6
            )
        ])

        # Train model
        if isinstance(X_train, dict):  # Multi-input model
            history = model.fit(
                X_train,
                y_train,
                validation_data=(X_val, y_val),
                epochs=epochs,
                batch_size=batch_size,
                callbacks=callbacks,
                verbose=1
            )
        else:  # Single-input model
            history = model.fit(
                X_train,
                y_train,
                validation_data=(X_val, y_val),
                epochs=epochs,
                batch_size=batch_size,
                callbacks=callbacks,
                verbose=1
            )

        self.current_model = model
        return history

    def _split_data(self, X: Union[Dict[str, np.ndarray], np.ndarray],
                   y: np.ndarray, validation_split: float = 0.2) -> Tuple:
        """
        Split data into training and validation sets

        Args:
            X: Features
            y: Labels
            validation_split: Fraction of data to use for validation

        Returns:
            Tuple of (X_train, X_val, y_train, y_val)
        """
        if isinstance(X, dict):
            # Multi-input case - split each input separately
            indices = np.arange(len(y))
            np.random.shuffle(indices)

            split_idx = int(len(indices) * (1 - validation_split))

            train_indices = indices[:split_idx]
            val_indices = indices[split_idx:]

            X_train = {k: v[train_indices] for k, v in X.items()}
            X_val = {k: v[val_indices] for k, v in X.items()}
            y_train, y_val = y[train_indices], y[val_indices]

            return X_train, X_val, y_train, y_val
        else:
            # Single-input case
            return train_test_split(X, y, test_size=validation_split, random_state=42)

    def _cross_validate_model(self, X: Union[Dict[str, np.ndarray], np.ndarray],
                              y: np.ndarray, model_type: str,
                              epochs: int, batch_size: int) -> Dict[str, Any]:
        """
        Perform cross-validation on model

        Args:
            X: Features
            y: Labels
            model_type: Type of model
            epochs: Number of epochs per fold
            batch_size: Batch size

        Returns:
            Dictionary of cross-validation results
        """
        logger.info("Starting cross-validation")

        # For simplicity, use 3-fold cross-validation
        kfold = KFold(n_splits=3, shuffle=True, random_state=42)

        fold_results = []
        fold_metrics = []

        for fold, (train_idx, val_idx) in enumerate(kfold.split(X, y)):
            logger.info(f"Training fold {fold + 1}/3")

            if isinstance(X, dict):
                X_train = {k: v[train_idx] for k, v in X.items()}
                X_val = {k: v[val_idx] for k, v in X.items()}
            else:
                X_train, X_val = X[train_idx], X[val_idx]

            y_train, y_val = y[train_idx], y[val_idx]

            # Build fresh model for each fold
            model = self._build_model_for_type(model_type)
            if model is None:
                continue

            # Train model
            history = self._train_model_with_data(
                model, X_train, y_train, X_val, y_val, epochs, batch_size
            )

            # Evaluate model
            metrics = self._evaluate_model(model, X_val, y_val)
            fold_metrics.append(metrics)

            # Store fold history
            fold_results.append({
                "fold": fold + 1,
                "history": self._convert_history_to_dict(history.history),
                "metrics": metrics
            })

        # Calculate average metrics across folds
        avg_metrics = self._calculate_average_metrics(fold_metrics)

        return {
            "cross_validation_results": fold_results,
            "average_metrics": avg_metrics,
            "num_folds": 3
        }

    def _evaluate_model(self, model: tf.keras.Model,
                        X_test: Union[Dict[str, np.ndarray], np.ndarray],
                        y_test: np.ndarray) -> Dict[str, float]:
        """
        Evaluate model performance on test data

        Args:
            model: Model to evaluate
            X_test: Test features
            y_test: Test labels

        Returns:
            Dictionary of performance metrics
        """
        if isinstance(X_test, dict):
            evaluation = model.evaluate(X_test, y_test, verbose=0)
        else:
            evaluation = model.evaluate(X_test, y_test, verbose=0)

        # Get detailed metrics from model architecture
        detailed_metrics = self.model_architecture.evaluate_model_performance(X_test, y_test)

        # Combine metrics
        metrics = {
            "loss": float(evaluation[0]),
            "accuracy": float(evaluation[1]),
            "auc": float(evaluation[2]) if len(evaluation) > 2 else 0.0,
            "precision": detailed_metrics.get("precision", 0.0),
            "recall": detailed_metrics.get("recall", 0.0),
            "f1_score": detailed_metrics.get("f1_score", 0.0),
            "roc_auc": detailed_metrics.get("roc_auc", 0.0)
        }

        return metrics

    def _calculate_average_metrics(self, fold_metrics: List[Dict[str, float]]) -> Dict[str, float]:
        """
        Calculate average metrics across cross-validation folds

        Args:
            fold_metrics: List of metrics from each fold

        Returns:
            Dictionary of average metrics
        """
        if not fold_metrics:
            return {}

        avg_metrics = {}
        for metric_name in fold_metrics[0].keys():
            values = [fold[metric_name] for fold in fold_metrics]
            avg_metrics[metric_name] = float(np.mean(values))

        return avg_metrics

    def _convert_history_to_dict(self, history: Dict[str, List[float]]) -> Dict[str, List[float]]:
        """
        Convert training history to serializable dictionary

        Args:
            history: Training history from Keras

        Returns:
            Dictionary with converted history data
        """
        return {k: [float(x) for x in v] for k, v in history.items()}

    def save_trained_model(self, model_path: str = "trained_model") -> bool:
        """
        Save trained model to disk

        Args:
            model_path: Path to save model (without extension)

        Returns:
            True if save successful, False otherwise
        """
        if not self.current_model:
            logger.warning("No trained model available to save")
            return False

        try:
            # Save model architecture and weights
            model_arch_path = f"{model_path}_architecture.json"
            model_weights_path = f"{model_path}_weights.h5"

            # Save architecture
            model_json = self.current_model.to_json()
            with open(model_arch_path, "w") as json_file:
                json_file.write(model_json)

            # Save weights
            self.current_model.save_weights(model_weights_path)

            # Save additional metadata
            metadata = {
                "model_type": self.model_type.value if self.model_type else "unknown",
                "training_timestamp": datetime.now().isoformat(),
                "input_shape": self.model_architecture.input_shape,
                "output_shape": self.model_architecture.num_classes,
                "total_params": self.current_model.count_params()
            }

            with open(f"{model_path}_metadata.json", "w") as meta_file:
                json.dump(metadata, meta_file, indent=2)

            logger.info(f"Model saved successfully to {model_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False

    def load_trained_model(self, model_path: str = "trained_model") -> bool:
        """
        Load trained model from disk

        Args:
            model_path: Path to load model from (without extension)

        Returns:
            True if load successful, False otherwise
        """
        if not ML_AVAILABLE:
            logger.warning("Cannot load model - ML libraries not available")
            return False

        try:
            model_arch_path = f"{model_path}_architecture.json"
            model_weights_path = f"{model_path}_weights.h5"

            # Load model architecture
            with open(model_arch_path, "r") as json_file:
                loaded_model_json = json_file.read()

            # Recreate model
            self.current_model = tf.keras.models.model_from_json(loaded_model_json)

            # Load weights
            self.current_model.load_weights(model_weights_path)

            # Load metadata
            with open(f"{model_path}_metadata.json", "r") as meta_file:
                metadata = json.load(meta_file)
                self.model_type = ModelType(metadata.get("model_type", "simple_feedforward"))

            logger.info(f"Model loaded successfully from {model_path}")
            return True

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False

    def train_with_historical_data(self, model_type: str = 'multi_input',
                                  epochs: int = 50) -> Dict[str, Any]:
        """
        Train model using historical diagnostic data from database

        Args:
            model_type: Type of model to train
            epochs: Number of training epochs

        Returns:
            Dictionary containing training results
        """
        # Get all available historical data
        all_data = self.data_processor.get_training_data(limit=5000)

        if not all_data:
            return {"status": "failed", "reason": "no_historical_data"}

        # Preprocess data
        X, y = self.data_preprocessor.preprocess_batch_data(all_data, model_type)

        if len(X) == 0 or len(y) == 0:
            return {"status": "failed", "reason": "invalid_historical_data"}

        # Use 80/20 split
        X_train, X_val, y_train, y_val = self._split_data(X, y, 0.2)

        # Build and train model
        model = self._build_model_for_type(model_type)
        if model is None:
            return {"status": "failed", "reason": "model_building_failed"}

        history = self._train_model_with_data(model, X_train, y_train, X_val, y_val, epochs, 32)

        # Evaluate and return results
        metrics = self._evaluate_model(model, X_val, y_val)

        return {
            "status": "completed",
            "model_type": model_type,
            "training_data_size": len(X),
            "positive_samples": int(np.sum(y)),
            "negative_samples": int(len(y) - np.sum(y)),
            "history": self._convert_history_to_dict(history.history),
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }

    def get_training_summary(self) -> Dict[str, Any]:
        """
        Get summary of all training sessions

        Returns:
            Dictionary containing training history summary
        """
        return {
            "total_training_sessions": len(self.training_history),
            "training_sessions": self.training_history,
            "current_model_type": self.model_type.value if self.model_type else None,
            "current_model_params": self.current_model.count_params() if self.current_model else 0
        }

# Global model trainer instance
model_trainer = ModelTrainer()