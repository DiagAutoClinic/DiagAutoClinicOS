#!/usr/bin/env python3
"""
AI Model Evaluation Module
Comprehensive model evaluation and validation system
"""

import logging
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import matplotlib.pyplot as plt

# Import ML libraries
try:
    import tensorflow as tf
    from tensorflow.keras.models import load_model
    from sklearn.metrics import (confusion_matrix, classification_report,
                                precision_recall_curve, roc_curve,
                                average_precision_score)
    from sklearn.model_selection import learning_curve
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logging.warning("ML libraries not available, model evaluation will be limited")

logger = logging.getLogger(__name__)

class ModelEvaluator:
    """
    Comprehensive model evaluation and validation system
    """

    def __init__(self):
        """
        Initialize model evaluator
        """
        self.evaluation_history = []
        self.current_model = None
        self.current_evaluation = None

    def evaluate_model(self, model: tf.keras.Model,
                       X_test: Dict[str, np.ndarray],
                       y_test: np.ndarray,
                       evaluation_name: str = "default_evaluation") -> Dict[str, Any]:
        """
        Comprehensive model evaluation

        Args:
            model: Model to evaluate
            X_test: Test features
            y_test: Test labels
            evaluation_name: Name for this evaluation

        Returns:
            Dictionary containing comprehensive evaluation results
        """
        if not ML_AVAILABLE:
            logger.warning("Cannot evaluate model - ML libraries not available")
            return {"status": "failed", "reason": "ml_libraries_unavailable"}

        start_time = time.time()
        evaluation_results = {
            "status": "started",
            "evaluation_name": evaluation_name,
            "timestamp": datetime.now().isoformat(),
            "metrics": {},
            "confusion_matrix": {},
            "roc_curve": {},
            "precision_recall_curve": {},
            "classification_report": ""
        }

        try:
            # Basic metrics
            evaluation_results["metrics"] = self._calculate_basic_metrics(model, X_test, y_test)

            # Confusion matrix
            evaluation_results["confusion_matrix"] = self._calculate_confusion_matrix(model, X_test, y_test)

            # ROC curve data
            evaluation_results["roc_curve"] = self._calculate_roc_curve(model, X_test, y_test)

            # Precision-recall curve
            evaluation_results["precision_recall_curve"] = self._calculate_precision_recall_curve(model, X_test, y_test)

            # Classification report
            evaluation_results["classification_report"] = self._generate_classification_report(model, X_test, y_test)

            # Feature importance (if applicable)
            if hasattr(model, 'layers') and len(model.layers) > 0:
                evaluation_results["feature_importance"] = self._calculate_feature_importance(model)

            evaluation_results["status"] = "completed"
            evaluation_results["evaluation_duration"] = time.time() - start_time

            # Store evaluation
            self.current_evaluation = evaluation_results
            self.evaluation_history.append(evaluation_results)

            logger.info(f"Model evaluation completed in {evaluation_results['evaluation_duration']:.2f} seconds")
            return evaluation_results

        except Exception as e:
            logger.error(f"Error during model evaluation: {e}")
            evaluation_results["status"] = "failed"
            evaluation_results["reason"] = str(e)
            return evaluation_results

    def _calculate_basic_metrics(self, model: tf.keras.Model,
                               X_test: Dict[str, np.ndarray],
                               y_test: np.ndarray) -> Dict[str, float]:
        """
        Calculate basic evaluation metrics

        Args:
            model: Model to evaluate
            X_test: Test features
            y_test: Test labels

        Returns:
            Dictionary of basic metrics
        """
        # Make predictions
        y_pred = model.predict(X_test)
        y_pred_binary = (y_pred > 0.5).astype(int).flatten()
        y_test_binary = y_test.flatten()

        # Calculate metrics
        metrics = {
            "accuracy": float(tf.keras.metrics.binary_accuracy(y_test, y_pred).numpy()),
            "precision": float(tf.keras.metrics.Precision()(y_test, y_pred).numpy()),
            "recall": float(tf.keras.metrics.Recall()(y_test, y_pred).numpy()),
            "f1_score": float(tf.keras.metrics.AUC()(y_test, y_pred).numpy()),
            "auc": float(tf.keras.metrics.AUC()(y_test, y_pred).numpy()),
            "loss": float(tf.keras.losses.binary_crossentropy(y_test, y_pred).numpy()),
            "average_precision": float(average_precision_score(y_test_binary, y_pred_binary))
        }

        return metrics

    def _calculate_confusion_matrix(self, model: tf.keras.Model,
                                  X_test: Dict[str, np.ndarray],
                                  y_test: np.ndarray) -> Dict[str, Any]:
        """
        Calculate confusion matrix

        Args:
            model: Model to evaluate
            X_test: Test features
            y_test: Test labels

        Returns:
            Dictionary containing confusion matrix data
        """
        y_pred = model.predict(X_test)
        y_pred_binary = (y_pred > 0.5).astype(int).flatten()
        y_test_binary = y_test.flatten()

        # Calculate confusion matrix
        tn, fp, fn, tp = confusion_matrix(y_test_binary, y_pred_binary).ravel()

        return {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp),
            "matrix": confusion_matrix(y_test_binary, y_pred_binary).tolist()
        }

    def _calculate_roc_curve(self, model: tf.keras.Model,
                           X_test: Dict[str, np.ndarray],
                           y_test: np.ndarray) -> Dict[str, Any]:
        """
        Calculate ROC curve data

        Args:
            model: Model to evaluate
            X_test: Test features
            y_test: Test labels

        Returns:
            Dictionary containing ROC curve data
        """
        y_pred = model.predict(X_test).flatten()
        y_test_binary = y_test.flatten()

        fpr, tpr, thresholds = roc_curve(y_test_binary, y_pred)
        auc_score = float(tf.keras.metrics.AUC()(y_test, y_pred).numpy())

        return {
            "fpr": fpr.tolist(),
            "tpr": tpr.tolist(),
            "thresholds": thresholds.tolist(),
            "auc": auc_score
        }

    def _calculate_precision_recall_curve(self, model: tf.keras.Model,
                                         X_test: Dict[str, np.ndarray],
                                         y_test: np.ndarray) -> Dict[str, Any]:
        """
        Calculate precision-recall curve data

        Args:
            model: Model to evaluate
            X_test: Test features
            y_test: Test labels

        Returns:
            Dictionary containing precision-recall curve data
        """
        y_pred = model.predict(X_test).flatten()
        y_test_binary = y_test.flatten()

        precision, recall, thresholds = precision_recall_curve(y_test_binary, y_pred)
        avg_precision = float(average_precision_score(y_test_binary, y_pred))

        return {
            "precision": precision.tolist(),
            "recall": recall.tolist(),
            "thresholds": thresholds.tolist(),
            "average_precision": avg_precision
        }

    def _generate_classification_report(self, model: tf.keras.Model,
                                      X_test: Dict[str, np.ndarray],
                                      y_test: np.ndarray) -> str:
        """
        Generate classification report

        Args:
            model: Model to evaluate
            X_test: Test features
            y_test: Test labels

        Returns:
            String containing classification report
        """
        y_pred = model.predict(X_test)
        y_pred_binary = (y_pred > 0.5).astype(int).flatten()
        y_test_binary = y_test.flatten()

        return classification_report(y_test_binary, y_pred_binary)

    def _calculate_feature_importance(self, model: tf.keras.Model) -> Dict[str, Any]:
        """
        Calculate feature importance (for interpretable models)

        Args:
            model: Model to analyze

        Returns:
            Dictionary containing feature importance data
        """
        # This is a simplified approach - real implementation would use more sophisticated methods
        feature_importance = {}

        # Try to extract weights from first dense layer
        for i, layer in enumerate(model.layers):
            if hasattr(layer, 'get_weights') and len(layer.get_weights()) > 0:
                weights = layer.get_weights()[0]
                if len(weights.shape) == 2 and weights.shape[1] > 1:
                    # Calculate average absolute weight for each input feature
                    avg_weights = np.mean(np.abs(weights), axis=1)
                    normalized_weights = avg_weights / np.max(avg_weights) if np.max(avg_weights) > 0 else avg_weights

                    feature_importance[f"layer_{i}"] = {
                        "weights": normalized_weights.tolist(),
                        "num_features": len(normalized_weights),
                        "max_weight": float(np.max(avg_weights)),
                        "min_weight": float(np.min(avg_weights))
                    }

        return feature_importance

    def generate_evaluation_visualizations(self, evaluation_results: Dict[str, Any],
                                         output_dir: str = "evaluation_plots") -> Dict[str, str]:
        """
        Generate visualizations from evaluation results

        Args:
            evaluation_results: Evaluation results to visualize
            output_dir: Directory to save plots

        Returns:
            Dictionary of file paths for generated plots
        """
        if not ML_AVAILABLE:
            logger.warning("Cannot generate visualizations - ML libraries not available")
            return {}

        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)

            plot_paths = {}

            # ROC Curve
            if "roc_curve" in evaluation_results:
                roc_path = os.path.join(output_dir, f"roc_curve_{evaluation_results['timestamp']}.png")
                self._plot_roc_curve(evaluation_results["roc_curve"], roc_path)
                plot_paths["roc_curve"] = roc_path

            # Precision-Recall Curve
            if "precision_recall_curve" in evaluation_results:
                pr_path = os.path.join(output_dir, f"precision_recall_{evaluation_results['timestamp']}.png")
                self._plot_precision_recall_curve(evaluation_results["precision_recall_curve"], pr_path)
                plot_paths["precision_recall_curve"] = pr_path

            # Confusion Matrix
            if "confusion_matrix" in evaluation_results:
                cm_path = os.path.join(output_dir, f"confusion_matrix_{evaluation_results['timestamp']}.png")
                self._plot_confusion_matrix(evaluation_results["confusion_matrix"], cm_path)
                plot_paths["confusion_matrix"] = cm_path

            return plot_paths

        except Exception as e:
            logger.error(f"Error generating visualizations: {e}")
            return {}

    def _plot_roc_curve(self, roc_data: Dict[str, Any], file_path: str):
        """
        Plot ROC curve

        Args:
            roc_data: ROC curve data
            file_path: Path to save plot
        """
        plt.figure(figsize=(8, 6))
        plt.plot(roc_data["fpr"], roc_data["tpr"], label=f'ROC curve (AUC = {roc_data["auc"]:.2f})')
        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic (ROC) Curve')
        plt.legend(loc="lower right")
        plt.grid(True)
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_precision_recall_curve(self, pr_data: Dict[str, Any], file_path: str):
        """
        Plot precision-recall curve

        Args:
            pr_data: Precision-recall curve data
            file_path: Path to save plot
        """
        plt.figure(figsize=(8, 6))
        plt.plot(pr_data["recall"], pr_data["precision"],
                label=f'Precision-Recall curve (AP = {pr_data["average_precision"]:.2f})')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Precision-Recall Curve')
        plt.legend(loc="upper right")
        plt.grid(True)
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_confusion_matrix(self, cm_data: Dict[str, Any], file_path: str):
        """
        Plot confusion matrix

        Args:
            cm_data: Confusion matrix data
            file_path: Path to save plot
        """
        cm = np.array(cm_data["matrix"])

        plt.figure(figsize=(6, 6))
        plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
        plt.title('Confusion Matrix')
        plt.colorbar()

        classes = ['No Fault', 'Fault']
        tick_marks = np.arange(len(classes))
        plt.xticks(tick_marks, classes, rotation=45)
        plt.yticks(tick_marks, classes)

        thresh = cm.max() / 2.
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                plt.text(j, i, str(cm[i, j]),
                        ha="center", va="center",
                        color="white" if cm[i, j] > thresh else "black")

        plt.ylabel('True label')
        plt.xlabel('Predicted label')
        plt.tight_layout()
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
        plt.close()

    def validate_model_performance(self, model: tf.keras.Model,
                                  validation_data: List[Dict[str, Any]],
                                  threshold: float = 0.5) -> Dict[str, Any]:
        """
        Validate model performance on real-world validation data

        Args:
            model: Model to validate
            validation_data: List of validation diagnostic sessions
            threshold: Decision threshold for predictions

        Returns:
            Dictionary containing validation results
        """
        if not validation_data:
            return {"status": "failed", "reason": "no_validation_data"}

        try:
            # Preprocess validation data
            preprocessor = DataPreprocessor()
            X_val, y_val = preprocessor.preprocess_batch_data(validation_data, 'multi_input')

            if len(X_val) == 0 or len(y_val) == 0:
                return {"status": "failed", "reason": "invalid_validation_data"}

            # Evaluate model
            evaluation = self.evaluate_model(model, X_val, y_val, "validation_run")

            # Add real-world performance metrics
            y_pred = model.predict(X_val).flatten()
            y_pred_binary = (y_pred > threshold).astype(int)
            y_val_binary = y_val.flatten()

            real_world_metrics = {
                "false_positive_rate": float(np.sum((y_pred_binary == 1) & (y_val_binary == 0)) / np.sum(y_val_binary == 0)) if np.sum(y_val_binary == 0) > 0 else 0.0,
                "false_negative_rate": float(np.sum((y_pred_binary == 0) & (y_val_binary == 1)) / np.sum(y_val_binary == 1)) if np.sum(y_val_binary == 1) > 0 else 0.0,
                "critical_fault_detection_rate": self._calculate_critical_fault_detection(validation_data, y_pred_binary)
            }

            evaluation["real_world_metrics"] = real_world_metrics
            return evaluation

        except Exception as e:
            logger.error(f"Error during model validation: {e}")
            return {"status": "failed", "reason": str(e)}

    def _calculate_critical_fault_detection(self, validation_data: List[Dict[str, Any]],
                                           predictions: np.ndarray) -> Dict[str, float]:
        """
        Calculate critical fault detection metrics

        Args:
            validation_data: Validation diagnostic sessions
            predictions: Model predictions

        Returns:
            Dictionary of critical fault detection metrics
        """
        critical_faults = 0
        detected_critical = 0

        for i, session in enumerate(validation_data):
            dtc_codes = session.get('dtc_codes', [])
            has_critical = any(self._is_critical_fault(code) for code in dtc_codes)

            if has_critical:
                critical_faults += 1
                if predictions[i] == 1:  # Model predicted fault
                    detected_critical += 1

        return {
            "critical_fault_count": critical_faults,
            "detected_critical_faults": detected_critical,
            "critical_fault_detection_rate": float(detected_critical / critical_faults) if critical_faults > 0 else 0.0
        }

    def _is_critical_fault(self, dtc_code: str) -> bool:
        """
        Determine if DTC code represents a critical fault

        Args:
            dtc_code: DTC code to check

        Returns:
            True if critical fault, False otherwise
        """
        critical_patterns = ['P03', 'P05', 'P07', 'P01', 'P02', 'P04', 'P06']
        return any(pattern in str(dtc_code) for pattern in critical_patterns)

    def compare_models(self, model1: tf.keras.Model, model2: tf.keras.Model,
                      test_data: List[Dict[str, Any]],
                      comparison_name: str = "model_comparison") -> Dict[str, Any]:
        """
        Compare performance of two models

        Args:
            model1: First model to compare
            model2: Second model to compare
            test_data: Test data for comparison
            comparison_name: Name for this comparison

        Returns:
            Dictionary containing comparison results
        """
        try:
            # Preprocess test data
            preprocessor = DataPreprocessor()
            X_test, y_test = preprocessor.preprocess_batch_data(test_data, 'multi_input')

            if len(X_test) == 0 or len(y_test) == 0:
                return {"status": "failed", "reason": "invalid_test_data"}

            # Evaluate both models
            eval1 = self.evaluate_model(model1, X_test, y_test, f"{comparison_name}_model1")
            eval2 = self.evaluate_model(model2, X_test, y_test, f"{comparison_name}_model2")

            # Calculate performance differences
            comparison = {
                "status": "completed",
                "comparison_name": comparison_name,
                "timestamp": datetime.now().isoformat(),
                "model1_metrics": eval1["metrics"],
                "model2_metrics": eval2["metrics"],
                "performance_differences": {},
                "winner": None
            }

            # Calculate differences
            for metric in eval1["metrics"].keys():
                if metric in eval2["metrics"]:
                    diff = eval2["metrics"][metric] - eval1["metrics"][metric]
                    comparison["performance_differences"][metric] = diff

            # Determine winner
            if eval2["metrics"]["accuracy"] > eval1["metrics"]["accuracy"]:
                comparison["winner"] = "model2"
            elif eval1["metrics"]["accuracy"] > eval2["metrics"]["accuracy"]:
                comparison["winner"] = "model1"
            else:
                comparison["winner"] = "tie"

            return comparison

        except Exception as e:
            logger.error(f"Error during model comparison: {e}")
            return {"status": "failed", "reason": str(e)}

    def generate_evaluation_report(self, evaluation_results: Dict[str, Any],
                                   report_path: str = "evaluation_report.json") -> bool:
        """
        Generate comprehensive evaluation report

        Args:
            evaluation_results: Evaluation results to include
            report_path: Path to save report

        Returns:
            True if report generation successful, False otherwise
        """
        try:
            report = {
                "evaluation_summary": {
                    "status": evaluation_results["status"],
                    "model_type": evaluation_results.get("model_type", "unknown"),
                    "timestamp": evaluation_results["timestamp"],
                    "evaluation_duration": evaluation_results.get("evaluation_duration", 0)
                },
                "performance_metrics": evaluation_results["metrics"],
                "confusion_matrix": evaluation_results.get("confusion_matrix", {}),
                "roc_curve_analysis": {
                    "auc_score": evaluation_results.get("roc_curve", {}).get("auc", 0),
                    "description": "Area Under Curve represents model's ability to distinguish between classes"
                },
                "precision_recall_analysis": {
                    "average_precision": evaluation_results.get("precision_recall_curve", {}).get("average_precision", 0),
                    "description": "Average Precision summarizes precision-recall curve as weighted mean of precisions"
                },
                "classification_report": evaluation_results.get("classification_report", ""),
                "feature_importance": evaluation_results.get("feature_importance", {}),
                "recommendations": self._generate_recommendations(evaluation_results)
            }

            # Save report
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)

            logger.info(f"Evaluation report generated at {report_path}")
            return True

        except Exception as e:
            logger.error(f"Error generating evaluation report: {e}")
            return False

    def _generate_recommendations(self, evaluation_results: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on evaluation results

        Args:
            evaluation_results: Evaluation results to analyze

        Returns:
            List of recommendations
        """
        recommendations = []
        metrics = evaluation_results["metrics"]

        # Accuracy-based recommendations
        if metrics["accuracy"] < 0.8:
            recommendations.append("Model accuracy is below 80%. Consider increasing model complexity or adding more training data.")
        elif metrics["accuracy"] < 0.9:
            recommendations.append("Model accuracy is good but could be improved. Consider fine-tuning hyperparameters or adding more diverse training examples.")

        # Precision/recall balance
        precision_recall_ratio = metrics["precision"] / metrics["recall"] if metrics["recall"] > 0 else 1.0
        if precision_recall_ratio > 1.5:
            recommendations.append("Model has higher precision than recall. Consider adjusting decision threshold or adding more positive examples to training data.")
        elif precision_recall_ratio < 0.7:
            recommendations.append("Model has higher recall than precision. Consider adjusting decision threshold or improving feature selection.")

        # AUC recommendations
        if metrics["auc"] < 0.85:
            recommendations.append("AUC score indicates room for improvement in model discrimination ability. Consider feature engineering or more sophisticated model architectures.")

        # Add general recommendations
        recommendations.append("Regularly retrain model with new diagnostic data to maintain performance.")
        recommendations.append("Monitor model performance in production and collect feedback for continuous improvement.")

        return recommendations

# Global model evaluator instance
model_evaluator = ModelEvaluator()