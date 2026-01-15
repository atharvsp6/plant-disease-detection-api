# 🚀 Deployment Guide: Plant Disease Detection API on Render

This guide walks you through deploying the Plant Disease Detection API to **Render.com**.

## Prerequisites

- GitHub account (free)
- Render account (free) connected to GitHub
- This repository already pushed to GitHub

## Step-by-Step Deployment

### 1. Verify Repository is on GitHub

The repo should already be at: `https://github.com/atharvsp6/plant-disease-detection-api`

Confirm it includes:
- `app.py`
- `requirements.txt`
- `runs/classify/runs/classify/plant_disease/weights/best.pt`
- `templates/index.html`
- `render.yaml`

### 2. Go to Render.com

1. Navigate to [render.com](https://render.com)
2. Click **Sign Up**
3. Choose **Continue with GitHub**
4. Authorize Render to access your GitHub repositories
5. Click **Continue** after authorization

### 3. Create a New Web Service

1. Once logged in to Render, click the **New +** button (top-right)
2. Select **Web Service**
3. Look for `plant-disease-detection-api` in the repo list
4. Click **Connect** next to it

### 4. Configure the Service

Fill in the following settings:

| Setting | Value |
|---------|-------|
| **Name** | `plant-disease-api` (or customize) |
| **Environment** | `Python` |
| **Runtime** | `3.10` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app:app --host 0.0.0.0 --port $PORT` |
| **Plan** | `Free` |
| **Region** | `Oregon` or your closest region |

### 5. Deploy

1. Click **Create Web Service**
2. Wait for deployment to complete (2-5 minutes on first deploy)
3. You'll see a live URL like: `https://plant-disease-api.onrender.com`

### 6. Verify Deployment

Test your API is running:

**A. Health Check**
```bash
curl https://plant-disease-api.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "num_classes": 24
}
```

**B. API Documentation**
Visit: `https://plant-disease-api.onrender.com/docs`

**C. Web Interface**
Visit: `https://plant-disease-api.onrender.com/`

**D. Test Prediction**
```bash
curl -X POST "https://plant-disease-api.onrender.com/predict" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@leaf_image.jpg"
```

## Integration with YieldWise

To use this API from your YieldWise backend:

### Python Example

```python
import requests

DISEASE_API = "https://plant-disease-api.onrender.com/predict"

def detect_plant_disease(image_path):
    """Send image to disease detection API"""
    with open(image_path, "rb") as image_file:
        files = {"file": image_file}
        response = requests.post(DISEASE_API, files=files, timeout=60)
    
    if response.status_code == 200:
        result = response.json()
        prediction = result["prediction"]
        return {
            "crop": prediction["crop"],
            "disease": prediction["disease"],
            "confidence": prediction["confidence"],
            "all_predictions": result["top_3_predictions"]
        }
    else:
        raise Exception(f"Disease API error: {response.status_code}")

# Usage
result = detect_plant_disease("corn_leaf.jpg")
print(f"Crop: {result['crop']}")
print(f"Disease: {result['disease']}")
print(f"Confidence: {result['confidence']}%")
```

### JavaScript/Node.js Example

```javascript
async function detectPlantDisease(imageFile) {
    const formData = new FormData();
    formData.append('file', imageFile);
    
    const response = await fetch(
        'https://plant-disease-api.onrender.com/predict',
        { method: 'POST', body: formData }
    );
    
    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }
    
    const result = await response.json();
    const prediction = result.prediction;
    
    return {
        crop: prediction.crop,
        disease: prediction.disease,
        confidence: prediction.confidence,
        allPredictions: result.top_3_predictions
    };
}

// Usage
const imageFile = document.getElementById('imageInput').files[0];
const result = await detectPlantDisease(imageFile);
console.log(`Detected: ${result.crop} - ${result.disease} (${result.confidence}%)`);
```

## API Endpoints Reference

### Health Check
```
GET /health
```
Returns: `{ "status": "healthy", "model_loaded": true, "num_classes": 24 }`

### Predict Disease
```
POST /predict
Content-Type: multipart/form-data
Body: file = <image file>
```
Returns: Disease prediction with top-3 confidence scores

### Get All Supported Classes
```
GET /classes
```
Returns: List of all 24 plant disease classes

## Important Notes

### Model Loading Time
- First prediction after deployment may take 30-60 seconds as the YOLOv8 model loads
- Subsequent requests are much faster (~2-5 seconds per image on free tier)

### Render Free Tier Limitations
- Service goes to sleep after 15 minutes of inactivity
- First request after sleep takes longer (~30-60 seconds)
- Limited to 750 free dyno-hours per month

### Performance
- Free tier uses shared resources; consider upgrading for production use
- Image processing is CPU-intensive; each prediction takes 2-10 seconds
- Keep image size under 10MB (validated in API)

## Troubleshooting

### Service won't start
1. Check the Render logs: Dashboard → Your Service → Logs
2. Common issues:
   - Missing `best.pt` in repo
   - Wrong Python version
   - Dependency installation failed

**Solution**: Check logs, fix issue, push to GitHub. Render auto-redeploys.

### Model not loading
```
FileNotFoundError: Model file not found at ...
```
Ensure the model file `runs/classify/runs/classify/plant_disease/weights/best.pt` is committed to Git.

### Timeout errors
The free tier may timeout on large images. Try reducing image size or upgrading plan.

### CORS errors
CORS is already enabled in the API for all origins. If issues persist, contact support.

## Updating the API

After making changes locally:

1. Commit and push to GitHub:
```bash
git add .
git commit -m "Update: description of changes"
git push origin main
```

2. Render automatically redeploys on push (you can disable auto-deploy in settings)

## Upgrading from Free Tier

For production use with YieldWise:

1. Go to your Render dashboard
2. Select your service
3. Click **Settings** → **Plan**
4. Upgrade to **Starter** ($7/month) or higher

Benefits:
- Service never sleeps
- Better performance (dedicated resources)
- Better uptime SLA

## Support

- **Render Docs**: https://render.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **YOLOv8 Docs**: https://docs.ultralytics.com/

---

**Deployment successful! Your Plant Disease Detection API is now live and ready to serve predictions to YieldWise.** 🎉
