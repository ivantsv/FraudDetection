import lightgbm as lgb
import numpy as np
import pandas as pd
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
from functools import partial
from model_config import ModelConfig

logger = logging.getLogger(__name__)


class FraudDetectionModel:
    """
    Асинхронная обёртка над LightGBM моделью
    
    Загружает модель из файла и параметры из БД/конфига
    """
    def __init__(self, model_config: ModelConfig):
        """
        Синхронная загрузка модели
        """
        try:
            logger.info(f"Loading model")

            self.model = lgb.Booster(model_file=str(model_config.model_path))

            with open(model_config.feature_list_path, 'r') as f:
                data = json.load(f)
            self.feature_names = data["feature_names"]

            logger.info(f"Model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    async def predict(self, transaction: Dict) -> Dict:
        """
        Предсказание для одной транзакции

        Args:version={model_version}, 
            transaction: Словарь с признаками транзакции
            
        Returns:
            {
                "fraud_probability": 0.87,
                "is_fraud": True,
                "threshold": 0.5,
                "model_version": "1.0",
                "features_used": 88
            }
        """

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            partial(self._predict_sync, transaction)
        )

        return result
    
    def _predict_sync(self, transaction: Dict) -> Dict:
        """
        Синхронное предсказание (внутренний метод)
        """
        try:
            features = self._extract_features(transaction)
            X = np.array([features])

            probability = self.model.predict(X)[0]
            is_fraud = bool(probability >= self.threshold)
            confidence = self._calculate_confidence(probability)

            result = {
                "fraud_probability": round(float(probability), 4),
                "is_fraud": is_fraud,
                "threshold": self.threshold,
                "confidence": confidence,
                "model_version": self.model_version,
                "features_used": len(features),
                "prediction_time": datetime.now().isoformat()
            }
            
            logger.debug(f"Prediction: {result}")
            
            return result

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise

    def _extract_features(self, transaction: Dict) -> List[float]:
        """
        Извлекает признаки из транзакции в правильном порядке
        """
        features = []
        
        for feature_name in self.feature_names:
            value = transaction.get(feature_name)
            
            if value is None:
                if any(x in feature_name for x in ['amount', 'score', 'rate', 'count', 'frequency']):
                    value = 0.0
                else:
                    value = 0
            
            features.append(float(value))
        
        return features
    
    def _calculate_confidence(self, probability: float) -> str:
        """
        Определяет уровень уверенности модели
        """
        if probability >= 0.9 or probability <= 0.1:
            return "high"
        elif probability >= 0.7 or probability <= 0.3:
            return "medium"
        else:
            return "low"