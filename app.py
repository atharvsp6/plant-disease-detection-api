"""
Plant Disease Detection API
===========================
A FastAPI application for detecting plant diseases using YOLOv8 classification model.

Author: College Project
Description: This app loads a trained YOLOv8 model and provides both REST API and web interface
             for plant disease prediction from leaf images.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
from PIL import Image
import io
import os
import numpy as np
from pathlib import Path
from typing import Dict, List
import logging
import torch
from contextlib import asynccontextmanager

# Patch torch.load to use weights_only=False for PyTorch 2.6+
# This is necessary to load our trained YOLOv8 model (safe for our own trained models)
_original_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return _original_torch_load(*args, **kwargs)
torch.load = _patched_torch_load

# ============================================================================
# CONFIGURATION & SETUP
# ============================================================================

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# MODEL LOADING
# ============================================================================

# Global variable to store the model (loaded once at startup)
model = None
class_names = []

# Base project directory and model path (env override supported for deployments)
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = Path(
    os.getenv(
        "MODEL_PATH",
        BASE_DIR / "runs/classify/runs/classify/plant_disease/weights/best.pt",
    )
)


def load_model():
    """
    Load the YOLOv8 classification model at application startup.
    This ensures the model is loaded only once, improving performance.
    """
    global model, class_names
    
    try:
        logger.info(f"Loading model from {MODEL_PATH}...")

        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

        model = YOLO(str(MODEL_PATH))
        
        # Extract class names from the model
        class_names = model.names
        logger.info(f"Model loaded successfully! {len(class_names)} classes detected.")
        logger.info(f"Classes: {class_names}")
        
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise RuntimeError(f"Could not load model: {str(e)}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    Loads the YOLOv8 model into memory on startup.
    """
    # Startup: Load model
    load_model()
    yield
    # Shutdown: Cleanup if needed
    logger.info("Application shutting down...")


# Initialize FastAPI app with lifespan event handler
app = FastAPI(
    title="Plant Disease Detection API",
    description="API for detecting plant diseases using YOLOv8 classification",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for cross-origin requests (e.g., from YieldWise app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates directory for Jinja2
templates = Jinja2Templates(directory="templates")

# Create static directory if it doesn't exist
Path("static").mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_class_name(class_label: str) -> Dict[str, str]:
    """
    Parse the class label to extract crop and disease information.
    
    Format: "Crop___Disease" or "Crop,_variety___Disease"
    Examples:
        - "Tomato___Early_blight" -> {crop: "Tomato", disease: "Early blight"}
        - "Pepper,_bell___Bacterial_spot" -> {crop: "Pepper, bell", disease: "Bacterial spot"}
    
    Args:
        class_label: The class name from the model
        
    Returns:
        Dictionary with 'crop' and 'disease' keys
    """
    try:
        # Split on '___' to separate crop and disease
        parts = class_label.split('___')
        
        if len(parts) >= 2:
            crop = parts[0].replace('_', ' ')
            disease = parts[1].replace('_', ' ')
        else:
            # Fallback if format is unexpected
            crop = "Unknown"
            disease = class_label.replace('_', ' ')
        
        return {
            "crop": crop.strip(),
            "disease": disease.strip()
        }
    except Exception as e:
        logger.error(f"Error parsing class name '{class_label}': {str(e)}")
        return {"crop": "Unknown", "disease": class_label}


def validate_image(file: UploadFile) -> None:
    """
    Validate the uploaded image file.
    
    Args:
        file: The uploaded file
        
    Raises:
        HTTPException: If validation fails
    """
    # Check file extension
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Check file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if hasattr(file, 'size') and file.size > max_size:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 10MB limit"
        )


async def process_image(file: UploadFile) -> Image.Image:
    """
    Read and process the uploaded image file.
    
    Args:
        file: The uploaded file
        
    Returns:
        PIL Image object
        
    Raises:
        HTTPException: If image processing fails
    """
    try:
        # Read file contents
        contents = await file.read()
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(contents))
        
        # Convert to RGB if necessary (handles RGBA, grayscale, etc.)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to process image: {str(e)}"
        )


def predict_disease(image: Image.Image) -> Dict:
    """
    Run the YOLOv8 model on the image and return predictions.
    
    Args:
        image: PIL Image object
        
    Returns:
        Dictionary containing prediction results
        
    Raises:
        HTTPException: If prediction fails
    """
    try:
        # Run inference
        results = model.predict(image, verbose=False)
        result = results[0]
        
        # Get probabilities
        probs = result.probs.data.cpu().numpy()
        
        # Get top 3 predictions
        top_3_indices = probs.argsort()[-3:][::-1]
        
        predictions = []
        for idx in top_3_indices:
            class_label = class_names[idx]
            confidence = float(probs[idx])
            parsed = parse_class_name(class_label)
            
            predictions.append({
                "class": class_label,
                "crop": parsed["crop"],
                "disease": parsed["disease"],
                "confidence": round(confidence * 100, 2)
            })
        
        # Get the top prediction
        top_prediction = predictions[0]
        
        return {
            "success": True,
            "prediction": {
                "crop": top_prediction["crop"],
                "disease": top_prediction["disease"],
                "confidence": top_prediction["confidence"],
                "class": top_prediction["class"]
            },
            "top_3_predictions": predictions
        }
        
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Home page with image upload interface.
    
    Returns:
        HTML page for uploading images and viewing predictions
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Predict plant disease from an uploaded image.
    
    This endpoint accepts an image file, runs the YOLOv8 model,
    and returns the prediction results in JSON format.
    
    Args:
        file: The uploaded image file
        
    Returns:
        JSON response with prediction results:
        {
            "success": true,
            "prediction": {
                "crop": "Tomato",
                "disease": "Early blight",
                "confidence": 95.67,
                "class": "Tomato___Early_blight"
            },
            "top_3_predictions": [...]
        }
        
    Raises:
        HTTPException: If validation or prediction fails
    """
    # Check if model is loaded
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please try again later."
        )
    
    # Validate the uploaded file
    validate_image(file)
    
    # Process the image
    image = await process_image(file)
    
    # Run prediction
    result = predict_disease(image)
    
    return JSONResponse(content=result)


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running and model is loaded.
    
    Returns:
        JSON response with status information
    """
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "num_classes": len(class_names) if class_names else 0
    }


@app.get("/classes")
async def get_classes():
    """
    Get list of all plant disease classes the model can detect.
    
    Returns:
        JSON response with all class names
    """
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )
    
    # Parse all class names
    parsed_classes = []
    for class_label in class_names:
        parsed = parse_class_name(class_label)
        parsed_classes.append({
            "class": class_label,
            "crop": parsed["crop"],
            "disease": parsed["disease"]
        })
    
    return {
        "total_classes": len(class_names),
        "classes": parsed_classes
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 Not Found errors"""
    return JSONResponse(
        status_code=404,
        content={"success": False, "error": "Endpoint not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 Internal Server errors"""
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error"}
    )


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║   Plant Disease Detection API                                ║
    ║   FastAPI + YOLOv8 Classification                            ║
    ╚══════════════════════════════════════════════════════════════╝
    
    Starting server...
    
    📡 API Endpoints:
       - Web Interface:  http://localhost:8000/
       - Predict API:    http://localhost:8000/predict
       - Health Check:   http://localhost:8000/health
       - Get Classes:    http://localhost:8000/classes
    
    📖 API Documentation:
       - Swagger UI:     http://localhost:8000/docs
       - ReDoc:          http://localhost:8000/redoc
    
    Press Ctrl+C to stop the server
    """)
    
    # Run the FastAPI application
    uvicorn.run(
        app,
        host="0.0.0.0",  # Listen on all network interfaces
        port=int(os.getenv("PORT", "8000")),  # Render/railway style PORT support
        log_level="info"
    )
