import logging

logger = logging.getLogger(__name__)

class ModelConfig:
    def __init__(self, threshold: float = 0.5):
        self.threshold = float