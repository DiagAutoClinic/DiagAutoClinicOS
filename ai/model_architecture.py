#!/usr/bin/env python3
"""
AI Model Architecture Module
Advanced machine learning model designs for automotive diagnostics
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

# Import ML libraries
try:
    import tensorflow as tf
    from tensorflow.keras.layers import Input, Dense, Dropout, BatchNormalization, Concatenate
    from tensorflow.keras.models import Model
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
    from tensorflow.keras.regularizers import l2
    import numpy as np
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logging.warning("ML libraries not available, advanced model architecture will be limited")

logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Enumeration of available model types"""
    SIMPLE_FEEDFORWARD = "simple_feedforward"
    MULTI_INPUT = "multi_input"
    TIME_SERIES = "time_series"
    ENSEMBLE = "ensemble"

class ModelArchitecture:
    """
    Advanced model architecture for automotive diagnostics AI
    """

    def __init__(self, input_shape: Tuple[int, ...] = (32,), num_classes: int = 1):
        """
        Initialize model architecture

        Args:
            input_shape: Shape of input data
            num_classes: Number of output classes
        """
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.model = None
        self.history = None
        self.model_type = None

    def build_simple_feedforward_model(self) -> Model:
        """
        Build enhanced feedforward neural network

        Returns:
            Compiled TensorFlow Keras model
        """
        if not ML_AVAILABLE:
            raise ImportError("ML libraries not available")

        # Input layer
        input_layer = Input(shape=self.input_shape, name='input_layer')

        # Feature extraction layers
        x = Dense(128, activation='relu', kernel_regularizer=l2(0.01))(input_layer)
        x = BatchNormalization()(x)
        x = Dropout(0.3)(x)

        x = Dense(64, activation='relu', kernel_regularizer=l2(0.01))(x)
        x = BatchNormalization()(x)
        x = Dropout(0.2)(x)

        x = Dense(32, activation='relu')(x)
        x = BatchNormalization()(x)

        # Output layer
        activation = 'sigmoid' if self.num_classes == 1 else 'softmax'
        output_layer = Dense(self.num_classes, activation=activation, name='output_layer')(x)

        # Create model
        model = Model(inputs=input_layer, outputs=output_layer)

        # Compile with enhanced optimizer
        optimizer = Adam(learning_rate=0.001, clipnorm=1.0)
        
        loss = 'binary_crossentropy' if self.num_classes == 1 else 'sparse_categorical_crossentropy'
        
        metrics = ['accuracy']
        if self.num_classes == 1:
            metrics.extend([
                tf.keras.metrics.AUC(name='auc'),
                tf.keras.metrics.Precision(name='precision'),
                tf.keras.metrics.Recall(name='recall')
            ])
            
        model.compile(
            optimizer=optimizer,
            loss=loss,
            metrics=metrics
        )

        self.model_type = ModelType.SIMPLE_FEEDFORWARD
        return model

    def build_multi_input_model(self, dtc_input_shape: Tuple[int] = (10,),
                              params_input_shape: Tuple[int] = (22,),
                              vehicle_input_shape: Tuple[int] = (5,)) -> Model:
        """
        Build multi-input model for handling different data types separately

        Args:
            dtc_input_shape: Shape for DTC-related features
            params_input_shape: Shape for live parameter features
            vehicle_input_shape: Shape for vehicle context features

        Returns:
            Compiled multi-input TensorFlow Keras model
        """
        if not ML_AVAILABLE:
            raise ImportError("ML libraries not available")

        # DTC input branch
        dtc_input = Input(shape=dtc_input_shape, name='dtc_input')
        dtc_x = Dense(32, activation='relu')(dtc_input)
        dtc_x = BatchNormalization()(dtc_x)
        dtc_x = Dropout(0.2)(dtc_x)
        dtc_x = Dense(16, activation='relu')(dtc_x)

        # Live parameters branch
        params_input = Input(shape=params_input_shape, name='params_input')
        params_x = Dense(64, activation='relu')(params_input)
        params_x = BatchNormalization()(params_x)
        params_x = Dropout(0.3)(params_x)
        params_x = Dense(32, activation='relu')(params_x)
        params_x = BatchNormalization()(params_x)

        # Vehicle context branch
        vehicle_input = Input(shape=vehicle_input_shape, name='vehicle_input')
        vehicle_x = Dense(16, activation='relu')(vehicle_input)
        vehicle_x = BatchNormalization()(vehicle_x)
        vehicle_x = Dropout(0.1)(vehicle_x)

        # Concatenate all branches
        concatenated = Concatenate()([dtc_x, params_x, vehicle_x])

        # Combined processing
        x = Dense(64, activation='relu')(concatenated)
        x = BatchNormalization()(x)
        x = Dropout(0.2)(x)
        x = Dense(32, activation='relu')(x)

        # Output layer
        activation = 'sigmoid' if self.num_classes == 1 else 'softmax'
        output_layer = Dense(self.num_classes, activation=activation, name='output_layer')(x)

        # Create model
        model = Model(
            inputs=[dtc_input, params_input, vehicle_input],
            outputs=output_layer
        )

        # Compile with enhanced optimizer
        optimizer = Adam(learning_rate=0.0005, clipnorm=1.0)
        
        loss = 'binary_crossentropy' if self.num_classes == 1 else 'sparse_categorical_crossentropy'
        
        metrics = ['accuracy']
        if self.num_classes == 1:
            metrics.extend([
                tf.keras.metrics.AUC(name='auc'),
                tf.keras.metrics.Precision(name='precision'),
                tf.keras.metrics.Recall(name='recall')
            ])

        model.compile(
            optimizer=optimizer,
            loss=loss,
            metrics=metrics
        )

        self.model_type = ModelType.MULTI_INPUT
        return model

    def build_time_series_model(self, timesteps: int = 10, features: int = 20) -> Model:
        """
        Build LSTM-based time series model for sequential diagnostic data

        Args:
            timesteps: Number of timesteps in sequence
            features: Number of features per timestep

        Returns:
            Compiled LSTM TensorFlow Keras model
        """
        if not ML_AVAILABLE:
            raise ImportError("ML libraries not available")

        from tensorflow.keras.layers import LSTM, TimeDistributed

        # Input layer for time series
        input_layer = Input(shape=(timesteps, features), name='time_series_input')

        # LSTM layers
        x = LSTM(64, return_sequences=True, kernel_regularizer=l2(0.01))(input_layer)
        x = BatchNormalization()(x)
        x = Dropout(0.2)(x)

        x = LSTM(32, return_sequences=False)(x)
        x = BatchNormalization()(x)
        x = Dropout(0.2)(x)

        # Dense layers
        x = Dense(32, activation='relu')(x)
        x = BatchNormalization()(x)

        # Output layer
        activation = 'sigmoid' if self.num_classes == 1 else 'softmax'
        output_layer = Dense(self.num_classes, activation=activation, name='output_layer')(x)

        # Create model
        model = Model(inputs=input_layer, outputs=output_layer)

        # Compile with enhanced optimizer
        optimizer = Adam(learning_rate=0.0008, clipnorm=1.0)
        
        loss = 'binary_crossentropy' if self.num_classes == 1 else 'sparse_categorical_crossentropy'
        
        metrics = ['accuracy']
        if self.num_classes == 1:
            metrics.extend([
                tf.keras.metrics.AUC(name='auc'),
                tf.keras.metrics.Precision(name='precision'),
                tf.keras.metrics.Recall(name='recall')
            ])

        model.compile(
            optimizer=optimizer,
            loss=loss,
            metrics=metrics
        )

        self.model_type = ModelType.TIME_SERIES
        return model

    def get_model_summary(self) -> Dict[str, Any]:
        """
        Get model architecture summary

        Returns:
            Dictionary containing model summary information
        """
        if not self.model:
            return {"status": "no_model_loaded"}

        return {
            "model_type": self.model_type.value if self.model_type else "unknown",
            "input_shape": self.input_shape,
            "output_shape": self.num_classes,
            "total_params": self.model.count_params(),
            "layers": len(self.model.layers),
            "summary": self.model.summary()
        }

    def get_training_callbacks(self, model_path: str = "best_model.h5") -> List[Any]:
        """
        Get standard training callbacks for model training

        Args:
            model_path: Path to save best model

        Returns:
            List of training callbacks
        """
        # Determine monitor metric
        monitor_metric = 'val_auc' if self.num_classes == 1 else 'val_accuracy'
        mode = 'max'
        
        return [
            EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True,
                verbose=1
            ),
            ModelCheckpoint(
                model_path,
                monitor=monitor_metric,
                save_best_only=True,
                mode=mode,
                verbose=1
            )
        ]

    def evaluate_model_performance(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """
        Comprehensive model evaluation

        Args:
            X_test: Test features
            y_test: Test labels

        Returns:
            Dictionary of performance metrics
        """
        if not ML_AVAILABLE or not self.model:
            return {"status": "evaluation_failed"}

        try:
            # Make predictions
            y_pred = self.model.predict(X_test)
            
            if self.num_classes == 1:
                y_pred_binary = (y_pred > 0.5).astype(int)

                # Calculate metrics
                metrics = {
                    "accuracy": float(tf.keras.metrics.binary_accuracy(y_test, y_pred).numpy()),
                    "precision": float(precision_score(y_test, y_pred_binary)),
                    "recall": float(recall_score(y_test, y_pred_binary)),
                    "f1_score": float(f1_score(y_test, y_pred_binary)),
                    "roc_auc": float(roc_auc_score(y_test, y_pred)),
                    "loss": float(tf.keras.losses.binary_crossentropy(y_test, y_pred).numpy())
                }
            else:
                # Multi-class evaluation
                y_pred_classes = np.argmax(y_pred, axis=1)
                
                # Handle sparse vs one-hot targets
                if len(y_test.shape) > 1 and y_test.shape[1] > 1:
                    y_test_classes = np.argmax(y_test, axis=1)
                    loss_val = tf.keras.losses.categorical_crossentropy(y_test, y_pred).numpy()
                else:
                    y_test_classes = y_test.flatten() if hasattr(y_test, 'flatten') else y_test
                    loss_val = tf.keras.losses.sparse_categorical_crossentropy(y_test, y_pred).numpy()
                
                metrics = {
                    "accuracy": float(np.mean(y_pred_classes == y_test_classes)),
                    "precision": float(precision_score(y_test_classes, y_pred_classes, average='macro', zero_division=0)),
                    "recall": float(recall_score(y_test_classes, y_pred_classes, average='macro', zero_division=0)),
                    "f1_score": float(f1_score(y_test_classes, y_pred_classes, average='macro', zero_division=0)),
                    "loss": float(np.mean(loss_val))
                }
            
            return metrics

            return metrics

        except Exception as e:
            logger.error(f"Error evaluating model: {e}")
            return {"status": "error", "error": str(e)}

# Global model architecture instance
model_architecture = ModelArchitecture()