# FILE 2: app/api/schemas.py
# LOCATION: app/api/schemas.py
# PURPOSE: Request/response validation schemas
# ============================================================================

"""
API Request/Response Schemas
Defines data structures for API
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class PredictionRequest:
    """Single image prediction request"""
    image: str  # Base64 encoded image
    use_tflite: bool = False
    top_k: int = 3


@dataclass
class BatchPredictionRequest:
    """Batch prediction request"""
    images: List[str]  # List of base64 encoded images
    use_tflite: bool = False


@dataclass
class PredictionResponse:
    """Prediction response"""
    success: bool
    timestamp: str
    model_used: str
    primary_prediction: Dict[str, Any]
    alternative_predictions: List[Dict[str, Any]]
    disease_information: Dict[str, Any]
    error: Optional[str] = None


@dataclass
class HealthResponse:
    """Health check response"""
    status: str
    version: str
    keras_model_loaded: bool
    tflite_model_loaded: bool
    num_classes: int
    timestamp: str


@dataclass
class ErrorResponse:
    """Error response"""
    success: bool = False
    error: str = ""
    error_type: str = ""
    timestamp: str = ""


def validate_prediction_request(data: dict) -> tuple:
    """
    Validate prediction request
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not data:
        return False, "No data provided"
    
    if 'image' not in data:
        return False, "Missing 'image' field"
    
    if not data['image']:
        return False, "Image data is empty"
    
    # Optional fields validation
    if 'top_k' in data:
        try:
            top_k = int(data['top_k'])
            if top_k < 1 or top_k > 10:
                return False, "top_k must be between 1 and 10"
        except (ValueError, TypeError):
            return False, "top_k must be an integer"
    
    return True, None


def validate_batch_request(data: dict, max_batch_size: int = 10) -> tuple:
    """
    Validate batch prediction request
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not data:
        return False, "No data provided"
    
    if 'images' not in data:
        return False, "Missing 'images' field"
    
    images = data['images']
    
    if not isinstance(images, list):
        return False, "'images' must be a list"
    
    if len(images) == 0:
        return False, "'images' list is empty"
    
    if len(images) > max_batch_size:
        return False, f"Batch size exceeds maximum of {max_batch_size}"
    
    # Check each image
    for idx, img in enumerate(images):
        if not img:
            return False, f"Image at index {idx} is empty"
    
    return True, None
