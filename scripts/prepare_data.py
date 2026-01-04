"""
Data Preparation Script
Organizes raw dataset into train/validation/test splits
"""

import os
import shutil
import random
import json
from pathlib import Path
from typing import Tuple

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_config
from app.utils.logger import setup_logger, get_logger

# Setup logging
setup_logger("data_prep", log_file="logs/data_prep.log")
logger = get_logger(__name__)

# Load config
config = get_config()


class DataPreparation:
    """Handles dataset preparation"""
    
    def __init__(self, source_dir: Path, output_dir: Path,
                 train_ratio: float = 0.7,
                 val_ratio: float = 0.15,
                 test_ratio: float = 0.15,
                 seed: int = 42):
        """
        Initialize data preparation
        
        Args:
            source_dir: Source directory with raw data
            output_dir: Output directory for processed data
            train_ratio: Training set ratio
            val_ratio: Validation set ratio
            test_ratio: Test set ratio
            seed: Random seed for reproducibility
        """
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
        self.seed = seed
        
        # Set random seed
        random.seed(seed)
        
        # Validate ratios
        if abs(train_ratio + val_ratio + test_ratio - 1.0) > 0.001:
            raise ValueError("Ratios must sum to 1.0")
    
    def create_directory_structure(self):
        """Create output directory structure"""
        dirs = [
            self.output_dir / 'train',
            self.output_dir / 'validation',
            self.output_dir / 'test'
        ]
        
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
        
        logger.info("✓ Directory structure created")
    
    def get_class_directories(self) -> list:
        """Get all class directories from source"""
        if not self.source_dir.exists():
            raise FileNotFoundError(f"Source directory not found: {self.source_dir}")
        
        # Get all directories (exclude hidden and PlantVillage root)
        class_dirs = [
            d for d in self.source_dir.iterdir()
            if d.is_dir() and not d.name.startswith('.') and d.name != 'PlantVillage'
        ]
        
        if not class_dirs:
            raise ValueError(f"No class directories found in {self.source_dir}")
        
        logger.info(f"Found {len(class_dirs)} disease classes")
        return sorted(class_dirs, key=lambda x: x.name)
    
    def split_and_copy_images(self, class_dir: Path, class_name: str) -> Tuple[int, int, int]:
        """
        Split and copy images for a class
        
        Returns:
            tuple: (train_count, val_count, test_count)
        """
        # Get all images
        image_extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
        images = [
            f for f in class_dir.iterdir()
            if f.suffix in image_extensions
        ]
        
        if not images:
            logger.warning(f"No images found in {class_dir}")
            return 0, 0, 0
        
        # Shuffle
        random.shuffle(images)
        
        # Calculate split indices
        n_total = len(images)
        n_train = int(n_total * self.train_ratio)
        n_val = int(n_total * self.val_ratio)
        
        # Split
        train_images = images[:n_train]
        val_images = images[n_train:n_train + n_val]
        test_images = images[n_train + n_val:]
        
        # Create class directories in splits
        for split in ['train', 'validation', 'test']:
            (self.output_dir / split / class_name).mkdir(parents=True, exist_ok=True)
        
        # Copy images
        for img in train_images:
            shutil.copy2(img, self.output_dir / 'train' / class_name / img.name)
        
        for img in val_images:
            shutil.copy2(img, self.output_dir / 'validation' / class_name / img.name)
        
        for img in test_images:
            shutil.copy2(img, self.output_dir / 'test' / class_name / img.name)
        
        return len(train_images), len(val_images), len(test_images)
    
    def prepare(self):
        """Main preparation method"""
        logger.info("="*70)
        logger.info("STARTING DATA PREPARATION")
        logger.info("="*70)
        
        # Create structure
        self.create_directory_structure()
        
        # Get classes
        class_dirs = self.get_class_directories()
        
        # Process each class
        stats = {
            'train': 0,
            'validation': 0,
            'test': 0
        }
        
        class_names = []
        
        for class_dir in class_dirs:
            class_name = class_dir.name
            class_names.append(class_name)
            
            logger.info(f"\nProcessing: {class_name}")
            
            train_count, val_count, test_count = self.split_and_copy_images(
                class_dir, class_name
            )
            
            logger.info(
                f"  Total: {train_count + val_count + test_count} | "
                f"Train: {train_count} | Val: {val_count} | Test: {test_count}"
            )
            
            stats['train'] += train_count
            stats['validation'] += val_count
            stats['test'] += test_count
        
        # Save statistics
        dataset_stats = {
            'num_classes': len(class_names),
            'class_names': sorted(class_names),
            'splits': stats,
            'ratios': {
                'train': self.train_ratio,
                'validation': self.val_ratio,
                'test': self.test_ratio
            },
            'seed': self.seed
        }
        
        stats_file = self.output_dir.parent / 'dataset_stats.json'
        with open(stats_file, 'w') as f:
            json.dump(dataset_stats, f, indent=2)
        
        logger.info("\n" + "="*70)
        logger.info("DATA PREPARATION COMPLETE!")
        logger.info("="*70)
        logger.info(f"Classes: {len(class_names)}")
        logger.info(f"Train: {stats['train']}")
        logger.info(f"Validation: {stats['validation']}")
        logger.info(f"Test: {stats['test']}")
        logger.info(f"Total: {sum(stats.values())}")
        logger.info(f"Statistics saved: {stats_file}")
        logger.info("="*70)
        
        return dataset_stats


def main():
    """Main execution"""
    print("="*70)
    print("AGRICULTURAL CROP DISEASE DETECTION")
    print("DATA PREPARATION SCRIPT")
    print("="*70 + "\n")
    
    # Check source directory
    source_dir = config.RAW_DATA_DIR / "PlantVillage"
    
    if not source_dir.exists():
        logger.error(f"Source directory not found: {source_dir}")
        print("\n❌ ERROR: Source directory not found!")
        print(f"\nExpected location: {source_dir}")
        print("\nPlease follow these steps:")
        print("1. Download the PlantVillage dataset")
        print(f"2. Extract it to: {source_dir}")
        print("3. Run this script again")
        print("\nExpected structure:")
        print(f"  {source_dir}/")
        print("    ├── Tomato_Early_blight/")
        print("    ├── Tomato_Late_blight/")
        print("    ├── Tomato_healthy/")
        print("    └── ... (other disease classes)")
        return
    
    try:
        # Initialize and run
        prep = DataPreparation(
            source_dir=source_dir,
            output_dir=config.PROCESSED_DATA_DIR,
            train_ratio=config.TRAIN_RATIO,
            val_ratio=config.VAL_RATIO,
            test_ratio=config.TEST_RATIO
        )
        
        stats = prep.prepare()
        
        print("\n✅ Data preparation successful!")
        print(f"Next step: Run 'python scripts/train_model.py' to train the model")
        
    except Exception as e:
        logger.error(f"Data preparation failed: {e}", exc_info=True)
        print(f"\n❌ Data preparation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()