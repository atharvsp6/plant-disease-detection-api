# 🌿 Plant Disease Detection API

A production-ready FastAPI application for detecting plant diseases using YOLOv8 classification model. This system provides both a REST API and a user-friendly web interface for plant health analysis.

## 🎯 Features

- **YOLOv8 Classification**: Advanced deep learning model for accurate disease detection
- **REST API**: Easy integration with other applications (e.g., YieldWise)
- **Web Interface**: User-friendly UI for uploading and analyzing plant images
- **CORS Enabled**: Cross-origin support for external applications
- **Real-time Predictions**: Fast inference on CPU
- **Top-3 Predictions**: Confidence scores for multiple possible diagnoses
- **Comprehensive Documentation**: Auto-generated API docs with Swagger UI

## 📋 Requirements

- Python 3.8 or higher
- 16GB RAM (recommended for YOLOv8)
- Trained YOLOv8 model (`best.pt`)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Verify Model Path

Ensure your trained model is at:
```
runs/classify/plant_disease/weights/best.pt
```

Or update the `MODEL_PATH` variable in `app.py`:
```python
MODEL_PATH = "path/to/your/model/best.pt"
```

### 3. Run the Application

```bash
python app.py
```

Or with uvicorn directly:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Access the Application

- **Web Interface**: http://localhost:8000/
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📡 API Endpoints

### 1. Home Page (Web Interface)
```
GET /
```
Returns HTML page for image upload and disease prediction.

### 2. Predict Disease
```
POST /predict
Content-Type: multipart/form-data

Body:
- file: image file (JPG, PNG, BMP, GIF, max 10MB)
```

**Response:**
```json
{
  "success": true,
  "prediction": {
    "crop": "Tomato",
    "disease": "Early blight",
    "confidence": 95.67,
    "class": "Tomato___Early_blight"
  },
  "top_3_predictions": [
    {
      "class": "Tomato___Early_blight",
      "crop": "Tomato",
      "disease": "Early blight",
      "confidence": 95.67
    },
    {
      "class": "Tomato___Late_blight",
      "crop": "Tomato",
      "disease": "Late blight",
      "confidence": 3.21
    },
    {
      "class": "Tomato___Leaf_Mold",
      "crop": "Tomato",
      "disease": "Leaf Mold",
      "confidence": 0.89
    }
  ]
}
```

### 3. Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "num_classes": 24
}
```

### 4. Get All Classes
```
GET /classes
```

**Response:**
```json
{
  "total_classes": 24,
  "classes": [
    {
      "class": "Tomato___Early_blight",
      "crop": "Tomato",
      "disease": "Early blight"
    },
    ...
  ]
}
```

## 🔌 Integration Examples

### Python (Requests)
```python
import requests

# Upload and predict
url = "http://localhost:8000/predict"
files = {"file": open("plant_image.jpg", "rb")}
response = requests.post(url, files=files)
result = response.json()

print(f"Crop: {result['prediction']['crop']}")
print(f"Disease: {result['prediction']['disease']}")
print(f"Confidence: {result['prediction']['confidence']}%")
```

### JavaScript (Fetch API)
```javascript
const formData = new FormData();
formData.append('file', imageFile);

fetch('http://localhost:8000/predict', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log('Crop:', data.prediction.crop);
    console.log('Disease:', data.prediction.disease);
    console.log('Confidence:', data.prediction.confidence);
});
```

### cURL
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@plant_image.jpg"
```

## 📁 Project Structure

```
plant_disease_prediction/
│
├── app.py                          # Main FastAPI application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── templates/
│   └── index.html                  # Web interface template
│
├── static/
│   └── style.css                   # Additional CSS (optional)
│
├── runs/classify/plant_disease/    # Model directory
│   └── weights/
│       └── best.pt                 # Trained YOLOv8 model
│
└── dataset/                        # Training dataset (optional)
    ├── train/
    ├── val/
    └── test/
```

## 🎓 College Project Documentation

### Architecture Overview

1. **Model Loading**: YOLOv8 model is loaded once at application startup for efficiency
2. **File Upload**: Images are uploaded via multipart/form-data
3. **Preprocessing**: Images are validated and converted to RGB format
4. **Inference**: YOLOv8 runs prediction on the preprocessed image
5. **Postprocessing**: Results are parsed and formatted as JSON
6. **Response**: Top-3 predictions with confidence scores are returned

### Key Technologies

- **FastAPI**: Modern, high-performance web framework
- **YOLOv8**: State-of-the-art object classification
- **Uvicorn**: Lightning-fast ASGI server
- **Jinja2**: Template engine for web pages
- **Pillow**: Python Imaging Library
- **NumPy**: Numerical computing

### Error Handling

The application includes comprehensive error handling:
- File validation (type, size)
- Image processing errors
- Model prediction errors
- 404 and 500 error handlers

### CORS Configuration

CORS is enabled to allow cross-origin requests from:
- YieldWise application
- Mobile apps
- Other web applications

**Note**: In production, specify exact allowed origins:
```python
allow_origins=["https://yieldwise.com"]
```

## 🛠️ Configuration

### Model Path
Update in `app.py`:
```python
MODEL_PATH = "runs/classify/plant_disease/weights/best.pt"
```

### Server Settings
Update in `app.py` (main block):
```python
uvicorn.run(
    app,
    host="0.0.0.0",     # Change to "127.0.0.1" for local only
    port=8000,           # Change port if needed
    log_level="info"
)
```

### File Upload Limits
Update in `app.py`:
```python
max_size = 10 * 1024 * 1024  # 10MB (change as needed)
```

## 📊 Supported Plant Diseases

The model can detect diseases in:
- **Tomato**: Early blight, Late blight, Leaf Mold, Bacterial spot, etc.
- **Potato**: Early blight, Late blight, Healthy
- **Corn**: Cercospora leaf spot, Common rust, Northern Leaf Blight, Healthy
- **Grape**: Black rot, Esca, Leaf blight, Healthy
- **Pepper**: Bacterial spot, Healthy

## 🔒 Security Considerations

For production deployment:

1. **File Size Limits**: Implemented (10MB default)
2. **File Type Validation**: Only images allowed
3. **CORS**: Configure specific origins
4. **HTTPS**: Use reverse proxy (nginx/Apache)
5. **Rate Limiting**: Add rate limiting middleware
6. **Authentication**: Add JWT/OAuth if needed

## 🐛 Troubleshooting

### Model Not Loading
- Verify model path is correct
- Check file permissions
- Ensure model is compatible with ultralytics version

### Port Already in Use
```bash
# Change port in app.py or use:
uvicorn app:app --port 8001
```

### CORS Errors
- Check `allow_origins` in CORS middleware
- Ensure frontend URL is included

### Out of Memory
- Reduce batch size in model prediction
- Use smaller image sizes
- Ensure sufficient RAM (16GB recommended)

## 📝 API Testing

### Using Swagger UI
1. Navigate to http://localhost:8000/docs
2. Click on `/predict` endpoint
3. Click "Try it out"
4. Upload an image file
5. Click "Execute"

### Using Postman
1. Create new POST request
2. URL: `http://localhost:8000/predict`
3. Body: form-data
4. Key: `file` (type: File)
5. Select image file
6. Send request

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8000
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📄 License

This project is developed for educational purposes as a college project.

## 👥 Contributors

- College Project Team 2026

## 🙏 Acknowledgments

- YOLOv8 by Ultralytics
- FastAPI framework
- Plant disease dataset contributors

---

**For questions or support, please contact the development team.**
