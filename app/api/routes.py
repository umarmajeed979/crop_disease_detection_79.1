"""
API Routes
Defines all API endpoints
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from typing import Dict

from app.api.schemas import validate_prediction_request, validate_batch_request
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Create blueprint
api = Blueprint('api', __name__, url_prefix='/api')

# These will be injected by the app factory
model_manager = None
predictor = None
image_processor = None
config = None


def init_routes(mm, pred, img_proc, cfg):
    """Initialize routes with dependencies"""
    global model_manager, predictor, image_processor, config
    model_manager = mm
    predictor = pred
    image_processor = img_proc
    config = cfg


@api.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    
    Returns:
        JSON: Service health status
    """
    try:
        model_info = model_manager.get_model_info()
        
        return jsonify({
            "status": "healthy",
            "version": config.VERSION,
            "app_name": config.APP_NAME,
            "keras_model_loaded": model_info['keras_available'],
            "tflite_model_loaded": model_info['tflite_available'],
            "num_classes": model_info['num_classes'],
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@api.route('/predict', methods=['POST'])
def predict():
    """
    Single image prediction endpoint
    
    Request Body:
        {
            "image": "base64_encoded_image",
            "use_tflite": false (optional),
            "top_k": 3 (optional)
        }
    
    Returns:
        JSON: Prediction results
    """
    try:
        # Get request data
        data = request.get_json()
        
        # Validate request
        is_valid, error_msg = validate_prediction_request(data)
        if not is_valid:
            logger.warning(f"Invalid request: {error_msg}")
            return jsonify({
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }), 400
        
        # Extract parameters
        image_data = data.get('image')
        use_tflite = data.get('use_tflite', False)
        top_k = data.get('top_k', 3)
        
        # Validate image
        if not image_processor.validate_image(image_data):
            return jsonify({
                "success": False,
                "error": "Invalid image format or size",
                "timestamp": datetime.now().isoformat()
            }), 400
        
        # Preprocess image
        logger.info("Preprocessing image...")
        image_array = image_processor.preprocess_image(image_data)
        
        # Predict
        logger.info("Making prediction...")
        result = predictor.predict(
            image_array,
            use_tflite=use_tflite,
            top_k=top_k
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "error_type": "validation_error",
            "timestamp": datetime.now().isoformat()
        }), 400
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal server error during prediction",
            "error_type": "server_error",
            "timestamp": datetime.now().isoformat()
        }), 500


@api.route('/predict/batch', methods=['POST'])
def predict_batch():
    """
    Batch prediction endpoint
    
    Request Body:
        {
            "images": ["base64_image1", "base64_image2", ...],
            "use_tflite": false (optional)
        }
    
    Returns:
        JSON: Batch prediction results
    """
    try:
        # Get request data
        data = request.get_json()
        
        # Validate request
        is_valid, error_msg = validate_batch_request(
            data, 
            max_batch_size=config.MAX_BATCH_SIZE
        )
        if not is_valid:
            logger.warning(f"Invalid batch request: {error_msg}")
            return jsonify({
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }), 400
        
        # Extract parameters
        images = data.get('images', [])
        use_tflite = data.get('use_tflite', False)
        
        # Preprocess images
        logger.info(f"Processing batch of {len(images)} images...")
        image_arrays = []
        
        for idx, img_data in enumerate(images):
            try:
                img_array = image_processor.preprocess_image(img_data)
                image_arrays.append(img_array)
            except Exception as e:
                logger.error(f"Failed to process image {idx}: {e}")
                # Continue with other images
        
        if not image_arrays:
            return jsonify({
                "success": False,
                "error": "No valid images in batch",
                "timestamp": datetime.now().isoformat()
            }), 400
        
        # Predict batch
        logger.info(f"Making predictions for {len(image_arrays)} images...")
        results = predictor.predict_batch(image_arrays, use_tflite=use_tflite)
        
        return jsonify({
            "success": True,
            "results": results,
            "total_processed": len(results),
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Batch prediction failed: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal server error during batch prediction",
            "timestamp": datetime.now().isoformat()
        }), 500


@api.route('/model/info', methods=['GET'])
def model_info():
    """
    Get model information
    
    Returns:
        JSON: Model metadata
    """
    try:
        info = model_manager.get_model_info()
        
        return jsonify({
            "success": True,
            "model_info": info,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@api.route('/classes', methods=['GET'])
def get_classes():
    """
    Get all disease classes
    
    Returns:
        JSON: List of disease classes
    """
    try:
        return jsonify({
            "success": True,
            "classes": model_manager.class_labels,
            "num_classes": model_manager.num_classes,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get classes: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@api.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "timestamp": datetime.now().isoformat()
    }), 404


@api.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({
        "success": False,
        "error": "Method not allowed",
        "timestamp": datetime.now().isoformat()
    }), 405


@api.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "timestamp": datetime.now().isoformat()
    }), 500