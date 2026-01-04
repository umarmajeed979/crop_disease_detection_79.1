"""
Image Processing Utilities
Handles image preprocessing and validation
"""

import base64
import io
import numpy as np
from PIL import Image
from typing import Union, Tuple

from app.utils.logger import get_logger

logger = get_logger(__name__)


class ImageProcessor:
    """Image preprocessing and validation"""
    
    def __init__(self, target_size: Tuple[int, int] = (224, 224),
                 max_size_mb: int = 10):
        """
        Initialize image processor
        
        Args:
            target_size: Target image size (height, width)
            max_size_mb: Maximum allowed image size in MB
        """
        self.target_size = target_size
        self.max_size_bytes = max_size_mb * 1024 * 1024
    
    def preprocess_image(self, image_data: Union[str, bytes],
                        normalize: bool = True) -> np.ndarray:
        """
        Preprocess image for model prediction
        
        Args:
            image_data: Base64 string or bytes
            normalize: Whether to normalize pixel values to [0, 1]
            
        Returns:
            np.ndarray: Preprocessed image array (1, H, W, 3)
        """
        try:
            # Decode if base64
            if isinstance(image_data, str):
                # Remove data URI prefix if present
                if ',' in image_data:
                    image_data = image_data.split(',', 1)[1]
                image_data = base64.b64decode(image_data)
            
            # Validate size
            if len(image_data) > self.max_size_bytes:
                raise ValueError(
                    f"Image size ({len(image_data) / 1024 / 1024:.2f} MB) "
                    f"exceeds maximum allowed ({self.max_size_bytes / 1024 / 1024} MB)"
                )
            
            # Open image
            img = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                logger.debug(f"Converting image from {img.mode} to RGB")
                img = img.convert('RGB')
            
            # Resize
            img = img.resize(self.target_size, Image.LANCZOS)
            
            # Convert to array
            img_array = np.array(img, dtype=np.float32)
            
            # Normalize
            if normalize:
                img_array = img_array / 255.0
            
            # Add batch dimension
            img_array = np.expand_dims(img_array, axis=0)
            
            logger.debug(f"Image preprocessed: shape={img_array.shape}")
            return img_array
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            raise ValueError(f"Failed to process image: {str(e)}")
    
    def validate_image(self, image_data: Union[str, bytes]) -> bool:
        """
        Validate image format and size
        
        Args:
            image_data: Image data to validate
            
        Returns:
            bool: True if valid
        """
        try:
            # Decode if base64
            if isinstance(image_data, str):
                if ',' in image_data:
                    image_data = image_data.split(',', 1)[1]
                image_data = base64.b64decode(image_data)
            
            # Check size
            if len(image_data) > self.max_size_bytes:
                return False
            
            # Try to open
            img = Image.open(io.BytesIO(image_data))
            img.verify()
            
            return True
            
        except Exception as e:
            logger.error(f"Image validation failed: {e}")
            return False
    
    def get_image_info(self, image_data: Union[str, bytes]) -> dict:
        """
        Get image information
        
        Args:
            image_data: Image data
            
        Returns:
            dict: Image information (size, format, dimensions)
        """
        try:
            if isinstance(image_data, str):
                if ',' in image_data:
                    image_data = image_data.split(',', 1)[1]
                image_data = base64.b64decode(image_data)
            
            img = Image.open(io.BytesIO(image_data))
            
            return {
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "width": img.width,
                "height": img.height,
                "size_kb": len(image_data) / 1024
            }
            
        except Exception as e:
            logger.error(f"Failed to get image info: {e}")
            return {}