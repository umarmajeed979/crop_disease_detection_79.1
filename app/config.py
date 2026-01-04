"""
Configuration Management
Centralized configuration for all environments
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Base configuration"""
    
    # Application
    APP_NAME = "Crop Disease Detection API"
    VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    TESTING = False
    
    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))
    
    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Model Configuration
    MODEL_DIR = BASE_DIR / "data" / "models"
    MODEL_PATH = MODEL_DIR / "crop_disease_final.h5"
    TFLITE_MODEL_PATH = MODEL_DIR / "crop_disease_mobile.tflite"
    CLASS_LABELS_PATH = MODEL_DIR / "class_labels.json"
    
    # Image Processing
    IMG_SIZE = (224, 224)
    MAX_IMAGE_SIZE_MB = int(os.getenv("MAX_IMAGE_SIZE_MB", 10))
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
    
    # Data Directories
    DATA_DIR = BASE_DIR / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"
    TRAIN_DIR = PROCESSED_DATA_DIR / "train"
    VAL_DIR = PROCESSED_DATA_DIR / "validation"
    TEST_DIR = PROCESSED_DATA_DIR / "test"
    
    # Logging
    LOG_DIR = BASE_DIR / "logs"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Training Configuration
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", 32))
    EPOCHS = int(os.getenv("EPOCHS", 50))
    FINE_TUNE_EPOCHS = int(os.getenv("FINE_TUNE_EPOCHS", 20))
    LEARNING_RATE = float(os.getenv("LEARNING_RATE", 0.001))
    FINE_TUNE_LR = float(os.getenv("FINE_TUNE_LR", 0.0001))
    
    # Data Split Ratios
    TRAIN_RATIO = float(os.getenv("TRAIN_RATIO", 0.7))
    VAL_RATIO = float(os.getenv("VAL_RATIO", 0.15))
    TEST_RATIO = float(os.getenv("TEST_RATIO", 0.15))
    
    # API Configuration
    MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", 10))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))
    
    # Security
    API_KEY = os.getenv("API_KEY")  # Optional API key
    RATE_LIMIT = os.getenv("RATE_LIMIT", "100 per hour")
    
    @classmethod
    def init_app(cls):
        """Initialize application directories"""
        dirs = [
            cls.MODEL_DIR,
            cls.LOG_DIR,
            cls.PROCESSED_DATA_DIR,
            cls.TRAIN_DIR,
            cls.VAL_DIR,
            cls.TEST_DIR,
        ]
        for directory in dirs:
            directory.mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = "WARNING"
    
    # Production-specific settings
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = "DEBUG"


# Configuration mapping
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config():
    """Get configuration based on environment"""
    env = os.getenv("FLASK_ENV", "development")
    return config.get(env, config["default"])