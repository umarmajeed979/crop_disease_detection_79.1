"""
Flask Application Factory
Creates and configures the Flask application
"""

from flask import Flask
from flask_cors import CORS

from app.config import get_config
from app.core.model import ModelManager
from app.core.predictor import DiseasePredictor
from app.data.disease_info import DiseaseDatabase
from app.utils.image_utils import ImageProcessor
from app.utils.logger import setup_logger, get_logger
from app.api import routes


def create_app(config_name=None):
    """
    Application factory
    
    Args:
        config_name: Configuration name (development, production, testing)
        
    Returns:
        Flask: Configured Flask application
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    config = get_config()
    if config_name:
        from app.config import config as config_dict
        config = config_dict.get(config_name, config)
    
    app.config.from_object(config)
    
    # Initialize directories
    config.init_app()
    
    # Setup logging
    log_file = config.LOG_DIR / "app.log"
    setup_logger(
        "app",
        log_file=log_file,
        level=config.LOG_LEVEL
    )
    
    logger = get_logger(__name__)
    logger.info(f"Starting {config.APP_NAME} v{config.VERSION}")
    logger.info(f"Environment: {app.config.get('ENV', 'development')}")
    
    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": config.CORS_ORIGINS,
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    logger.info(f"CORS enabled for origins: {config.CORS_ORIGINS}")
    
    # Initialize components
    try:
        # Model Manager
        logger.info("Initializing Model Manager...")
        model_manager = ModelManager(
            model_path=config.MODEL_PATH,
            class_labels_path=config.CLASS_LABELS_PATH,
            tflite_path=config.TFLITE_MODEL_PATH
        )
        
        if not model_manager.is_ready():
            logger.error("Model Manager initialization failed")
            raise RuntimeError("Models not loaded correctly")
        
        logger.info("✓ Model Manager initialized")
        
        # Disease Database
        logger.info("Loading Disease Database...")
        disease_db = DiseaseDatabase()
        logger.info("✓ Disease Database loaded")
        
        # Disease Predictor
        logger.info("Initializing Predictor...")
        predictor = DiseasePredictor(
            model_manager=model_manager,
            disease_db=disease_db
        )
        logger.info("✓ Predictor initialized")
        
        # Image Processor
        logger.info("Initializing Image Processor...")
        image_processor = ImageProcessor(
            target_size=config.IMG_SIZE,
            max_size_mb=config.MAX_IMAGE_SIZE_MB
        )
        logger.info("✓ Image Processor initialized")
        
        # Initialize routes with dependencies
        routes.init_routes(
            mm=model_manager,
            pred=predictor,
            img_proc=image_processor,
            cfg=config
        )
        
        # Register blueprints
        app.register_blueprint(routes.api)
        logger.info("✓ API routes registered")
        
        # Store components in app context
        app.model_manager = model_manager
        app.predictor = predictor
        app.disease_db = disease_db
        app.image_processor = image_processor
        
        logger.info("="*70)
        logger.info("APPLICATION READY")
        logger.info("="*70)
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}", exc_info=True)
        raise
    
    # Health check route (root)
    @app.route('/', methods=['GET'])
    def index():
        return {
            "app": config.APP_NAME,
            "version": config.VERSION,
            "status": "running",
            "endpoints": {
                "health": "/api/health",
                "predict": "/api/predict",
                "batch_predict": "/api/predict/batch",
                "model_info": "/api/model/info",
                "classes": "/api/classes"
            }
        }, 200
    
    return app