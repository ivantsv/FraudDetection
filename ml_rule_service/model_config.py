from pathlib import Path
import json
from jsonschema import validate, ValidationError
import logging

logger = logging.getLogger(__name__)


class InvalidProbabilityValue(Exception):
    """Исключение для невалидного порога вероятности"""
    def __init__(self, message):
        super().__init__(message)

class ModelConfig:
    """File for storage parameters for model"""
    def __init__(self, model_path: str | Path, feature_list_path: str | Path, threshold: float = 0.5):
        if not model_path.exists():
            raise FileNotFoundError
        self.model_path = Path(model_path)
        
        if not model_path.exists():
            raise FileNotFoundError
        self.feature_list_path = Path(feature_list_path)
        
        if not (0 <= threshold <= 1):
            raise InvalidProbabilityValue(f"Probability must be between 0 and 1. Given: {threshold}")
        self.threshold = threshold

        logger.info(f"ModelConfig initialized: threshold={threshold}")