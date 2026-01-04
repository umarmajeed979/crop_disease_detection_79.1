"""
Model Management
Handles model loading and lifecycle
"""

import json
import tensorflow as tf
from pathlib import Path
from typing import Optional, List

from app.utils.logger import get_logger

logger = get_logger(__name__)


class ModelManager:
    """Manages ML model loading and metadata"""
    
    def __init__(self, model_path: Path, class_labels_path: Path, 
                 tflite_path: Optional[Path] = None):
        """
        Initialize model manager
        
        Args:
            model_path: Path to Keras model (.h5)
            class_labels_path: Path to class labels JSON
            tflite_path: Optional path to TFLite model
        """
        self.model_path = model_path
        self.class_labels_path = class_labels_path
        self.tflite_path = tflite_path
        
        self.keras_model = None
        self.tflite_interpreter = None
        self.tflite_input_details = None
        self.tflite_output_details = None
        self.class_labels = []
        self.num_classes = 0
        
        self._load_models()
        self._load_class_labels()
    
    def _load_models(self):
        """Load Keras and TFLite models"""
        # Load Keras model
        try:
            if self.model_path.exists():
                logger.info(f"Loading Keras model from {self.model_path}")
                self.keras_model = tf.keras.models.load_model(str(self.model_path))
                logger.info("✓ Keras model loaded successfully")
            else:
                logger.warning(f"Keras model not found at {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load Keras model: {e}")
            self.keras_model = None
        
        # Load TFLite model
        if self.tflite_path and self.tflite_path.exists():
            try:
                logger.info(f"Loading TFLite model from {self.tflite_path}")
                self.tflite_interpreter = tf.lite.Interpreter(
                    model_path=str(self.tflite_path)
                )
                self.tflite_interpreter.allocate_tensors()
                self.tflite_input_details = self.tflite_interpreter.get_input_details()
                self.tflite_output_details = self.tflite_interpreter.get_output_details()
                logger.info("✓ TFLite model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load TFLite model: {e}")
                self.tflite_interpreter = None
    
    def _load_class_labels(self):
        """Load class labels from JSON"""
        try:
            if self.class_labels_path.exists():
                with open(self.class_labels_path, 'r') as f:
                    self.class_labels = json.load(f)
                self.num_classes = len(self.class_labels)
                logger.info(f"✓ Loaded {self.num_classes} class labels")
            else:
                logger.error(f"Class labels not found at {self.class_labels_path}")
                raise FileNotFoundError(f"Class labels file not found")
        except Exception as e:
            logger.error(f"Failed to load class labels: {e}")
            raise
    
    def is_ready(self) -> bool:
        """Check if at least one model is loaded"""
        return (self.keras_model is not None or 
                self.tflite_interpreter is not None) and \
               len(self.class_labels) > 0
    
    def get_model_info(self) -> dict:
        """Get model information"""
        info = {
            "num_classes": self.num_classes,
            "class_labels": self.class_labels,
            "keras_available": self.keras_model is not None,
            "tflite_available": self.tflite_interpreter is not None,
        }
        
        if self.keras_model:
            info.update({
                "keras_input_shape": self.keras_model.input_shape,
                "keras_output_shape": self.keras_model.output_shape,
                "keras_params": self.keras_model.count_params(),
            })
        
        return info
    
    def get_class_label(self, index: int) -> str:
        """Get class label by index"""
        if 0 <= index < len(self.class_labels):
            return self.class_labels[index]
        return f"unknown_class_{index}"
    
    def predict_keras(self, image_array):
        """
        Predict using Keras model
        
        Args:
            image_array: Preprocessed image array
            
        Returns:
            np.ndarray: Prediction probabilities
        """
        if self.keras_model is None:
            raise RuntimeError("Keras model not loaded")
        
        predictions = self.keras_model.predict(image_array, verbose=0)
        return predictions[0]
    
    def predict_tflite(self, image_array):
        """
        Predict using TFLite model
        
        Args:
            image_array: Preprocessed image array
            
        Returns:
            np.ndarray: Prediction probabilities
        """
        if self.tflite_interpreter is None:
            raise RuntimeError("TFLite model not loaded")
        
        self.tflite_interpreter.set_tensor(
            self.tflite_input_details[0]['index'],
            image_array.astype('float32')
        )
        self.tflite_interpreter.invoke()
        predictions = self.tflite_interpreter.get_tensor(
            self.tflite_output_details[0]['index']
        )
        return predictions[0]