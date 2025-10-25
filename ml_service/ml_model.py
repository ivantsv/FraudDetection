import logging
import random
from typing import Dict
from model_config import ModelConfig

logger = logging.getLogger(__name__)

class FraudDetectionModel:
    """ML-модель для gRPC сервиса"""

    def __init__(self, model_config: ModelConfig):
        """Загрузка конфига модели из БД"""
        self.model_config = model_config

    async def predict(self, transaction: Dict) -> Dict:
        """Получение результата работы модели"""
        probability = random.random()
        return {
            "correlation_id": transaction["correlation_id"],
            "is_fraud": True if probability >= self.model_config.threshold else False
        }
    
    async def get_model_info(self) -> Dict:
        """Информация о модели"""
        return {
            "threshold": self.model_config.threshold,
        }
