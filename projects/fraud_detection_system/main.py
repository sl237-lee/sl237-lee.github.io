"""
FastAPI service for real-time fraud detection
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import numpy as np
import time
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Fraud Detection API")

# Load model and artifacts
MODEL_PATH = os.getenv('MODEL_PATH', 'models/fraud_detector.pkl')

class PredictionRequest(BaseModel):
    transaction_id: str
    amount: float
    category: str
    hour: int
    day_of_week: int
    latitude: float
    longitude: float

class PredictionResponse(BaseModel):
    transaction_id: str
    fraud_probability: float
    is_fraud: bool
    inference_time_ms: float
    timestamp: str

class ModelLoader:
    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.features = None
        self.load_artifacts()
    
    def load_artifacts(self):
        """Load model and preprocessing artifacts"""
        try:
            # Load model
            with open(MODEL_PATH, 'rb') as f:
                self.model = pickle.load(f)
            
            # Load label encoder
            with open('models/label_encoder.pkl', 'rb') as f:
                self.label_encoder = pickle.load(f)
            
            # Load feature names
            with open('models/features.pkl', 'rb') as f:
                self.features = pickle.load(f)
            
            print("✅ Model artifacts loaded successfully")
        except FileNotFoundError as e:
            print(f"⚠️  Model not found. Please train the model first using the notebook.")
            print(f"   Run: notebooks/train_model.ipynb")
    
    def predict(self, features):
        """Make prediction"""
        if self.model is None:
            raise ValueError("Model not loaded")
        
        start_time = time.time()
        prediction_proba = self.model.predict_proba(features)[0][1]
        is_fraud = bool(prediction_proba > 0.5)
        inference_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return prediction_proba, is_fraud, inference_time

# Initialize model
model_loader = ModelLoader()

@app.get("/")
def root():
    return {
        "service": "Fraud Detection API",
        "status": "running",
        "model_loaded": model_loader.model is not None
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_status": "loaded" if model_loader.model is not None else "not_loaded",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/predict", response_model=PredictionResponse)
def predict_fraud(request: PredictionRequest):
    """Predict if transaction is fraudulent"""
    if model_loader.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Encode category
        category_encoded = model_loader.label_encoder.transform([request.category])[0]
        
        # Feature engineering
        is_night = (request.hour >= 22) or (request.hour <= 5)
        is_weekend = request.day_of_week in [5, 6]
        amount_log = np.log1p(request.amount)
        
        # Create feature array
        features = np.array([[
            request.amount,
            amount_log,
            category_encoded,
            request.hour,
            request.day_of_week,
            is_night,
            is_weekend,
            request.latitude,
            request.longitude
        ]])
        
        # Make prediction
        fraud_prob, is_fraud, inference_time = model_loader.predict(features)
        
        return PredictionResponse(
            transaction_id=request.transaction_id,
            fraud_probability=float(fraud_prob),
            is_fraud=is_fraud,
            inference_time_ms=float(inference_time),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/metrics")
def get_metrics():
    """Get model performance metrics"""
    # This would typically pull from a monitoring database
    return {
        "total_predictions": 0,
        "fraud_detected": 0,
        "average_latency_ms": 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
