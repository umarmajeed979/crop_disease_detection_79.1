"""
Model Training Script
Trains the crop disease detection model
"""

import os
import json
from pathlib import Path
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_config
from app.utils.logger import setup_logger, get_logger

# Setup logging
setup_logger("training", log_file="logs/training.log")
logger = get_logger(__name__)

# Load config
config = get_config()


class ModelTrainer:
    """Handles model training"""
    
    def __init__(self, num_classes: int):
        """
        Initialize trainer
        
        Args:
            num_classes: Number of disease classes
        """
        self.num_classes = num_classes
        self.model = None
        self.history = None
        
        logger.info(f"Trainer initialized for {num_classes} classes")
    
    def build_model(self):
        """Build transfer learning model"""
        logger.info("Building model architecture...")
        
        # Base model
        base_model = MobileNetV2(
            input_shape=(*config.IMG_SIZE, 3),
            include_top=False,
            weights='imagenet'
        )
        
        # Freeze base
        base_model.trainable = False
        
        # Build model
        self.model = keras.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(512, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.4),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(self.num_classes, activation='softmax')
        ])
        
        # Compile
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=config.LEARNING_RATE),
            loss='categorical_crossentropy',
            metrics=[
                'accuracy',
                keras.metrics.TopKCategoricalAccuracy(
                    k=min(3, self.num_classes),
                    name='top_3_accuracy'
                )
            ]
        )
        
        logger.info("✓ Model built successfully")
        return self.model
    
    def create_data_generators(self):
        """Create data generators with augmentation"""
        logger.info("Creating data generators...")
        
        # Training augmentation
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=30,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            vertical_flip=True,
            fill_mode='nearest',
            brightness_range=[0.8, 1.2]
        )
        
        # Validation (no augmentation)
        val_datagen = ImageDataGenerator(rescale=1./255)
        
        # Generators
        train_gen = train_datagen.flow_from_directory(
            config.TRAIN_DIR,
            target_size=config.IMG_SIZE,
            batch_size=config.BATCH_SIZE,
            class_mode='categorical',
            shuffle=True
        )
        
        val_gen = val_datagen.flow_from_directory(
            config.VAL_DIR,
            target_size=config.IMG_SIZE,
            batch_size=config.BATCH_SIZE,
            class_mode='categorical',
            shuffle=False
        )
        
        logger.info(f"✓ Train samples: {train_gen.samples}")
        logger.info(f"✓ Validation samples: {val_gen.samples}")
        
        return train_gen, val_gen
    
    def train(self, train_gen, val_gen, epochs: int):
        """Train model"""
        logger.info(f"Starting training for {epochs} epochs...")
        
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True,
                verbose=1
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7,
                verbose=1
            ),
            keras.callbacks.ModelCheckpoint(
                str(config.MODEL_DIR / 'best_model.h5'),
                monitor='val_accuracy',
                save_best_only=True,
                mode='max',
                verbose=1
            ),
            keras.callbacks.CSVLogger(
                str(config.LOG_DIR / 'training_history.csv')
            )
        ]
        
        self.history = self.model.fit(
            train_gen,
            validation_data=val_gen,
            epochs=epochs,
            callbacks=callbacks,
            verbose=1
        )
        
        logger.info("✓ Training complete")
        return self.history
    
    def fine_tune(self, train_gen, val_gen, epochs: int):
        """Fine-tune model"""
        logger.info(f"Starting fine-tuning for {epochs} epochs...")
        
        # Unfreeze base model
        base_model = self.model.layers[0]
        base_model.trainable = True
        
        # Freeze early layers
        for layer in base_model.layers[:100]:
            layer.trainable = False
        
        # Recompile with lower learning rate
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=config.FINE_TUNE_LR),
            loss='categorical_crossentropy',
            metrics=[
                'accuracy',
                keras.metrics.TopKCategoricalAccuracy(
                    k=min(3, self.num_classes),
                    name='top_3_accuracy'
                )
            ]
        )
        
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=7,
                restore_best_weights=True,
                verbose=1
            ),
            keras.callbacks.ModelCheckpoint(
                str(config.MODEL_DIR / 'best_model_finetuned.h5'),
                monitor='val_accuracy',
                save_best_only=True,
                mode='max',
                verbose=1
            )
        ]
        
        history = self.model.fit(
            train_gen,
            validation_data=val_gen,
            epochs=epochs,
            callbacks=callbacks,
            verbose=1
        )
        
        logger.info("✓ Fine-tuning complete")
        return history
    
    def save_model(self):
        """Save final model"""
        logger.info("Saving models...")
        
        # Save Keras model
        model_path = config.MODEL_PATH
        self.model.save(str(model_path))
        logger.info(f"✓ Keras model saved: {model_path}")
        
        # Convert to TFLite
        converter = tf.lite.TFLiteConverter.from_keras_model(self.model)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.target_spec.supported_types = [tf.float16]
        
        tflite_model = converter.convert()
        
        tflite_path = config.TFLITE_MODEL_PATH
        with open(tflite_path, 'wb') as f:
            f.write(tflite_model)
        
        size_kb = len(tflite_model) / 1024
        logger.info(f"✓ TFLite model saved: {tflite_path} ({size_kb:.2f} KB)")


def main():
    """Main training function"""
    print("="*70)
    print("AGRICULTURAL CROP DISEASE DETECTION")
    print("MODEL TRAINING")
    print("="*70 + "\n")
    
    # Check data directories
    if not config.TRAIN_DIR.exists():
        logger.error(f"Training directory not found: {config.TRAIN_DIR}")
        print("\n❌ Training data not found!")
        print("Please run 'python scripts/prepare_data.py' first!")
        return
    
    if not config.VAL_DIR.exists():
        logger.error(f"Validation directory not found: {config.VAL_DIR}")
        print("\n❌ Validation data not found!")
        print("Please run 'python scripts/prepare_data.py' first!")
        return
    
    try:
        # Get number of classes
        class_folders = [
            d for d in config.TRAIN_DIR.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ]
        num_classes = len(class_folders)
        
        if num_classes == 0:
            raise ValueError("No classes found in training directory")
        
        logger.info(f"Detected {num_classes} classes")
        class_names = sorted([d.name for d in class_folders])
        
        # Save class labels
        labels_path = config.CLASS_LABELS_PATH
        with open(labels_path, 'w') as f:
            json.dump(class_names, f, indent=2)
        logger.info(f"✓ Class labels saved: {labels_path}")
        
        # Initialize trainer
        trainer = ModelTrainer(num_classes=num_classes)
        
        # Build model
        logger.info("\n" + "="*70)
        logger.info("BUILDING MODEL")
        logger.info("="*70)
        trainer.build_model()
        trainer.model.summary(print_fn=logger.info)
        
        # Create data generators
        logger.info("\n" + "="*70)
        logger.info("PREPARING DATA")
        logger.info("="*70)
        train_gen, val_gen = trainer.create_data_generators()
        
        # Phase 1: Initial training
        logger.info("\n" + "="*70)
        logger.info("PHASE 1: INITIAL TRAINING")
        logger.info("="*70)
        trainer.train(train_gen, val_gen, epochs=config.EPOCHS)
        
        # Phase 2: Fine-tuning
        logger.info("\n" + "="*70)
        logger.info("PHASE 2: FINE-TUNING")
        logger.info("="*70)
        trainer.fine_tune(train_gen, val_gen, epochs=config.FINE_TUNE_EPOCHS)
        
        # Save models
        logger.info("\n" + "="*70)
        logger.info("SAVING MODELS")
        logger.info("="*70)
        trainer.save_model()
        
        # Summary
        logger.info("\n" + "="*70)
        logger.info("TRAINING COMPLETE!")
        logger.info("="*70)
        logger.info(f"Classes: {num_classes}")
        logger.info(f"Model: {config.MODEL_PATH}")
        logger.info(f"TFLite: {config.TFLITE_MODEL_PATH}")
        logger.info(f"Labels: {labels_path}")
        logger.info("="*70)
        
        print("\n✅ Training successful!")
        print(f"Next step: Run 'python run.py' to start the API server")
        
    except KeyboardInterrupt:
        logger.warning("Training interrupted by user")
        print("\n⚠️ Training interrupted")
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        print(f"\n❌ Training failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()