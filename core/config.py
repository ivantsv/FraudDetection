import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
MODEL_PATH = os.getenv("MODEL_PATH", "/app/models/fraud_detection_model.txt")
FEATURE_LIST_PATH = os.getenv("FEATURE_LIST_PATH", "/app/models/feature_names.json")
DEFAULT_THRESHOLD = float(os.getenv("DEFAULT_THRESHOLD", "0.5"))