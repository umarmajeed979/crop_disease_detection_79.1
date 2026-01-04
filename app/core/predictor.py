"""
Prediction Logic
Handles disease prediction and result processing
"""

import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime

from app.core.model import ModelManager
from app.data.disease_info import DiseaseDatabase
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DiseasePredictor:
    """Handles disease prediction logic"""
    
    def __init__(self, model_manager: ModelManager, 
                 disease_db: DiseaseDatabase):
        """
        Initialize predictor
        
        Args:
            model_manager: ModelManager instance
            disease_db: DiseaseDatabase instance
        """
        self.model_manager = model_manager
        self.disease_db = disease_db
    
    def predict(self, image_array: np.ndarray, 
                use_tflite: bool = False,
                top_k: int = 3) -> Dict:
        """
        Predict disease from image
        
        Args:
            image_array: Preprocessed image array (1, H, W, 3)
            use_tflite: Use TFLite model instead of Keras
            top_k: Number of top predictions to return
            
        Returns:
            dict: Prediction results with disease information
        """
        try:
            # Get predictions
            if use_tflite and self.model_manager.tflite_interpreter:
                logger.info("Using TFLite model for prediction")
                predictions = self.model_manager.predict_tflite(image_array)
            elif self.model_manager.keras_model:
                logger.info("Using Keras model for prediction")
                predictions = self.model_manager.predict_keras(image_array)
            else:
                raise RuntimeError("No model available for prediction")
            
            # Get top predictions
            top_predictions = self._get_top_predictions(predictions, top_k)
            
            # Get primary prediction
            primary = top_predictions[0]
            primary_class = primary['class']
            primary_confidence = primary['confidence']
            
            # Assess severity
            severity = self._assess_severity(primary_confidence)
            
            # Get disease information
            disease_info = self._get_disease_information(primary_class)
            
            # Build response
            result = {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "model_used": "tflite" if use_tflite else "keras",
                "primary_prediction": {
                    "disease": primary_class,
                    "confidence": float(primary_confidence),
                    "confidence_percentage": f"{primary_confidence * 100:.2f}%",
                    "severity": severity,
                },
                "alternative_predictions": top_predictions[1:],
                "disease_information": disease_info,
            }
            
            logger.info(f"Prediction complete: {primary_class} ({primary_confidence:.2%})")
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}", exc_info=True)
            raise
    
    def predict_batch(self, image_arrays: List[np.ndarray],
                     use_tflite: bool = False) -> List[Dict]:
        """
        Predict multiple images
        
        Args:
            image_arrays: List of preprocessed image arrays
            use_tflite: Use TFLite model
            
        Returns:
            list: List of prediction results
        """
        results = []
        
        for idx, image_array in enumerate(image_arrays):
            try:
                result = self.predict(image_array, use_tflite, top_k=1)
                result['image_index'] = idx
                results.append(result)
            except Exception as e:
                logger.error(f"Batch prediction failed for image {idx}: {e}")
                results.append({
                    "success": False,
                    "image_index": idx,
                    "error": str(e)
                })
        
        return results
    
    def _get_top_predictions(self, predictions: np.ndarray, 
                            top_k: int) -> List[Dict]:
        """
        Get top K predictions
        
        Args:
            predictions: Prediction probabilities array
            top_k: Number of top predictions
            
        Returns:
            list: Top K predictions with class names and confidences
        """
        # Ensure top_k doesn't exceed number of classes
        top_k = min(top_k, len(predictions))
        
        # Get top indices
        top_indices = np.argsort(predictions)[-top_k:][::-1]
        
        # Build results
        top_predictions = []
        for idx in top_indices:
            class_name = self.model_manager.get_class_label(int(idx))
            confidence = float(predictions[idx])
            
            top_predictions.append({
                "class": class_name,
                "class_index": int(idx),
                "confidence": confidence,
                "confidence_percentage": f"{confidence * 100:.2f}%"
            })
        
        return top_predictions
    
    def _assess_severity(self, confidence: float) -> str:
        """
        Assess prediction severity based on confidence
        
        Args:
            confidence: Prediction confidence (0-1)
            
        Returns:
            str: Severity level
        """
        if confidence < 0.5:
            return "uncertain"
        elif confidence < 0.7:
            return "mild"
        elif confidence < 0.85:
            return "moderate"
        else:
            return "severe"
    
    def _get_disease_information(self, class_name: str) -> Dict:
        """
        Get detailed disease information
        
        Args:
            class_name: Disease class name
            
        Returns:
            dict: Disease information
        """
        # Normalize class name for lookup
        disease_key = self._normalize_disease_key(class_name)
        
        # Try to get from database
        disease_info = self.disease_db.get_disease_info(disease_key)
        
        if disease_info:
            return disease_info
        
        # Return basic info if not in database
        return {
            "name": class_name,
            "crop": self._extract_crop_name(class_name),
            "type": "healthy" if "healthy" in class_name.lower() else "disease",
            "message": "Detailed information not available in database",
            "recommendation": "Consult with agricultural expert for detailed diagnosis"
        }
    
    def _normalize_disease_key(self, class_name: str) -> str:
        """
        Normalize class name to disease key
        
        Examples:
            "Tomato_Early_blight" -> "tomato_early_blight"
            "Pepper__bell___healthy" -> "pepper_bell_healthy"
        """
        # Remove multiple underscores and convert to lowercase
        normalized = class_name.lower()
        while "__" in normalized:
            normalized = normalized.replace("__", "_")
        return normalized.strip("_")
    
    def _extract_crop_name(self, class_name: str) -> str:
        """
        Extract crop name from class name
        
        Args:
            class_name: Full class name
            
        Returns:
            str: Crop name
        """
        # Common patterns: "Tomato_Disease", "Pepper__bell___Disease"
        parts = class_name.split("_")
        if parts:
            return parts[0].capitalize()
        return "Unknown"