# 🌱 Agricultural Crop Disease Detection - Backend

Production-ready backend for crop disease detection using deep learning. Supports tomato, potato, and pepper disease classification.

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Dataset Setup](#dataset-setup)
- [Training](#training)
- [Running the API](#running-the-api)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## ✨ Features

- **15 Disease Classes**: Detects 15 different crop diseases across tomato, potato, and pepper
- **Transfer Learning**: Uses MobileNetV2 for efficient and accurate predictions
- **Dual Models**: Supports both full Keras model and optimized TFLite model
- **RESTful API**: Clean, well-documented API endpoints
- **Production Ready**: Includes logging, error handling, and configuration management
- **Modular Architecture**: Easy to extend and maintain
- **CORS Support**: Ready for frontend integration

## 📁 Project Structure

```
crop-disease-backend/
├── app/                          # Main application
│   ├── __init__.py              # App factory
│   ├── config.py                # Configuration
│   ├── api/                     # API layer
│   │   ├── routes.py           # API endpoints
│   │   └── schemas.py          # Request/response schemas
│   ├── core/                    # Core logic
│   │   ├── model.py            # Model management
│   │   └── predictor.py        # Prediction logic
│   ├── data/                    # Data layer
│   │   └── disease_info.py     # Disease database
│   └── utils/                   # Utilities
│       ├── logger.py           # Logging
│       └── image_utils.py      # Image processing
├── scripts/                     # Standalone scripts
│   ├── prepare_data.py         # Data preparation
│   └── train_model.py          # Model training
├── data/                        # Data directory
│   ├── raw/                    # Raw dataset
│   ├── processed/              # Processed data
│   └── models/                 # Trained models
├── logs/                        # Application logs
├── tests/                       # Test suite
├── .env.example                # Example environment file
├── requirements.txt            # Python dependencies
├── run.py                      # Development server
├── wsgi.py                     # Production WSGI
└── README.md                   # This file
```

## 🔧 Requirements

- Python 3.8+
- 4GB+ RAM (8GB recommended for training)
- TensorFlow-compatible system
- (Optional) CUDA GPU for faster training

## 📦 Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd crop-disease-backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

## ⚙️ Configuration

Edit `.env` file to configure:

```bash
FLASK_ENV=development
DEBUG=True
HOST=0.0.0.0
PORT=5000
CORS_ORIGINS=*
MAX_IMAGE_SIZE_MB=10
BATCH_SIZE=32
EPOCHS=50
```

## 📊 Dataset Setup

### 1. Download PlantVillage Dataset

Download from [PlantVillage Dataset](https://www.kaggle.com/datasets/emmarex/plantdisease) or similar source.

### 2. Extract Dataset

```bash
mkdir -p data/raw
# Extract PlantVillage dataset to data/raw/PlantVillage/
```

Expected structure:
```
data/raw/PlantVillage/
├── Pepper__bell___Bacterial_spot/
├── Pepper__bell___healthy/
├── Potato___Early_blight/
├── Potato___Late_blight/
├── Potato___healthy/
├── Tomato_Bacterial_spot/
├── Tomato_Early_blight/
├── Tomato_Late_blight/
├── Tomato_Leaf_Mold/
├── Tomato_Septoria_leaf_spot/
├── Tomato_Spider_mites_Two_spotted_spider_mite/
├── Tomato__Target_Spot/
├── Tomato__Tomato_YellowLeaf__Curl_Virus/
├── Tomato__Tomato_mosaic_virus/
└── Tomato_healthy/
```

### 3. Prepare Data

```bash
python scripts/prepare_data.py
```

This will:
- Split data into train/validation/test (70/15/15)
- Organize into proper directory structure
- Save dataset statistics

## 🎓 Training

### Train the Model

```bash
python scripts/train_model.py
```

Training includes:
1. **Initial Training**: Transfer learning with frozen base (50 epochs)
2. **Fine-tuning**: Unfreezing top layers (20 epochs)
3. **Model Export**: Saves Keras (.h5) and TFLite (.tflite) models

Training outputs:
- `data/models/crop_disease_final.h5` - Full Keras model
- `data/models/crop_disease_mobile.tflite` - Mobile-optimized model
- `data/models/class_labels.json` - Class labels
- `logs/training.log` - Training logs

### Monitor Training

```bash
tail -f logs/training.log
```

## 🚀 Running the API

### Development Server

```bash
python run.py
```

The API will be available at `http://localhost:5000`

### Production Server (Gunicorn)

```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 wsgi:app
```

## 📖 API Documentation

### Base URL

```
http://localhost:5000
```

### Endpoints

#### 1. Health Check

```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "keras_model_loaded": true,
  "tflite_model_loaded": true,
  "num_classes": 15,
  "timestamp": "2024-01-01T12:00:00"
}
```

#### 2. Predict Disease

```http
POST /api/predict
Content-Type: application/json
```

**Request Body:**
```json
{
  "image": "base64_encoded_image_string",
  "use_tflite": false,
  "top_k": 3
}
```

**Response:**
```json
{
  "success": true,
  "timestamp": "2024-01-01T12:00:00",
  "model_used": "keras",
  "primary_prediction": {
    "disease": "Tomato_Early_blight",
    "confidence": 0.95,
    "confidence_percentage": "95.00%",
    "severity": "severe"
  },
  "alternative_predictions": [
    {
      "class": "Tomato_Late_blight",
      "confidence": 0.03,
      "confidence_percentage": "3.00%"
    }
  ],
  "disease_information": {
    "name": "Tomato Early Blight",
    "crop": "Tomato",
    "pathogen": "Alternaria solani (Fungus)",
    "symptoms": [...],
    "treatment": {...},
    "prevention": [...]
  }
}
```

#### 3. Batch Prediction

```http
POST /api/predict/batch
Content-Type: application/json
```

**Request Body:**
```json
{
  "images": [
    "base64_image_1",
    "base64_image_2"
  ],
  "use_tflite": false
}
```

#### 4. Model Information

```http
GET /api/model/info
```

#### 5. Get Classes

```http
GET /api/classes
```

### Error Responses

All errors return:
```json
{
  "success": false,
  "error": "Error message",
  "error_type": "validation_error|server_error",
  "timestamp": "2024-01-01T12:00:00"
}
```

## 🌐 Deployment

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "wsgi:app"]
```

Build and run:
```bash
docker build -t crop-disease-api .
docker run -p 5000:5000 crop-disease-api
```

### Cloud Deployment (AWS/GCP/Azure)

1. Use the provided `wsgi.py` entry point
2. Configure environment variables
3. Set up proper security groups/firewall rules
4. Use a reverse proxy (Nginx) for production
5. Enable HTTPS with SSL certificates

### Environment Variables for Production

```bash
FLASK_ENV=production
DEBUG=False
CORS_ORIGINS=https://your-frontend-domain.com
API_KEY=your_secret_key
```

## 🧪 Testing

### Manual Testing

```bash
# Test health endpoint
curl http://localhost:5000/api/health

# Test prediction (with image file)
python tests/test_api.py path/to/test/image.jpg
```

### Unit Tests

```bash
pytest tests/
```

## 🔍 Troubleshooting

### Issue: Models not loading

**Solution:**
```bash
# Ensure models exist
ls -la data/models/

# Retrain if needed
python scripts/train_model.py
```

### Issue: Memory errors during training

**Solution:**
- Reduce batch size in `.env`:
  ```bash
  BATCH_SIZE=16
  ```
- Use TFLite model for inference
- Close other applications

### Issue: CORS errors

**Solution:**
- Update `.env`:
  ```bash
  CORS_ORIGINS=http://localhost:3000,https://your-domain.com
  ```

### Issue: Slow predictions

**Solution:**
- Use TFLite model: `"use_tflite": true`
- Reduce image size before sending
- Use batch predictions for multiple images

## 📞 Support

For issues and questions:
1. Check [Troubleshooting](#troubleshooting)
2. Review logs in `logs/` directory
3. Open an issue on GitHub

## 📄 License

[Your License Here]

## 🤝 Contributing

Contributions welcome! Please follow the project structure and coding standards.

---

**Version**: 1.0.0  
**Last Updated**: 2024