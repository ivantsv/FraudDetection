from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from contextlib import asynccontextmanager
import logging
from ml_model import FraudDetectionModel
from model_config import ModelConfig
import core.config
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ml_model: Optional[FraudDetectionModel] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Загружаем модель при старте"""
    global ml_model
    
    logger.info("Starting ML Service...")
    
    try:
        config = ModelConfig(
            model_path=config.MODEL_PATH,
            feature_list_path=config.FEATURE_LIST_PATH,
            threshold=config.DEFAULT_THRESHOLD,
            model_version=config.MODEL_VERSION
        )
        
        ml_model = FraudDetectionModel(config)
        
        logger.info("ML Service ready!")
        
    except Exception as e:
        logger.error(f"Failed to start: {e}")
        raise
    
    yield
    
    logger.info("Shutting down...")

app = FastAPI(
    title="Fraud Detection ML Service",
    description="Real-time fraud detection with LightGBM",
    lifespan=lifespan
)


class PredictionRequest(BaseModel):
    """Запрос на предсказание"""
    pass

class PredictionResponse(BaseModel):
    """Ответ с предсказанием"""
    transaction_id: str
    fraud_probability: float
    is_fraud: bool
    threshold: float
    confidence: str
    model_version: str
    features_used: int
    prediction_time: str

class ThresholdUpdateRequest(BaseModel):
    """Обновление порога"""
    threshold: float = Field(..., ge=0.0, le=1.0)


@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "ML Fraud Detection",
        "status": "running",
        "model_loaded": ml_model is not None
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Предсказание для одной транзакции
    
    **Пример запроса:**
    ```json
    {
      "transaction_id": "tx-12345",
      "features": {
        "amount": 15000.0,
        "hour": 3,
        "is_night": 1,
        ...
      }
    }
    ```
    """
    if ml_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        transaction_data = {
            "transaction_id": request.transaction_id,
            **request.features
        }
        
        result = ml_model.predict(transaction_data)
        
        result["transaction_id"] = request.transaction_id
        
        logger.info(
            f"Prediction: {request.transaction_id} -> "
            f"prob={result['fraud_probability']:.4f}, "
            f"fraud={result['is_fraud']}"
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
@app.put("/config/threshold")
async def update_threshold(request: ThresholdUpdateRequest):
    """
    Обновляет порог классификации без перезагрузки модели
    """
    if ml_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        ml_model.update_threshold(request.threshold)
        
        return {
            "message": "Threshold updated successfully",
            "new_threshold": request.threshold,
            "model_version": ml_model.config.model_version
        }
        
    except Exception as e:
        logger.error(f"Threshold update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))