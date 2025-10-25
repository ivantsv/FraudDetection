import asyncio
import grpc
from concurrent import futures
import logging
import os
import sys
from pathlib import Path
from grpc_reflection.v1alpha import reflection

sys.path.insert(0, str(Path(__file__).parent / "generated"))

from generated import ml_pb2, ml_pb2_grpc
from ml_model import FraudDetectionModel
from model_config import ModelConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MODEL_VERSION = os.getenv("MODEL_VERSION", "1.0")
GRPC_PORT = os.getenv("GRPC_PORT", "50051")
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "10"))

class MLServiceServicer(ml_pb2_grpc.MLServiceServicer):
    """Реализация gRPC сервиса"""
    
    def __init__(self):
        logger.info("Initializing ML Service...")
        
        try:
            self.model_config = ModelConfig()
            self.model = FraudDetectionModel(self.model_config)
            logger.info("ML Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    async def Predict(self, request, context):
        """Предсказание для одной транзакции"""
        try:
            logger.info(f"Predict request: {request.correlation_id}")
            
            transaction = self._proto_to_dict(request)
            
            result = await self.model.predict(transaction)
            
            response = ml_pb2.PredictResponse(
                correlation_id=result["correlation_id"],
                is_fraud=result["is_fraud"]
            )
            
            logger.info(
                f"Prediction: {request.correlation_id} -> "
                f"is_fraud={result['is_fraud']}"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Prediction error: {str(e)}")
            return ml_pb2.PredictResponse()
        
    async def HealthCheck(self, request, context):
        """Health check"""
        try:
            info = await self.model.get_model_info()
            
            return ml_pb2.HealthCheckResponse(
                status="healthy"
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            return ml_pb2.HealthCheckResponse(status="unhealthy")
        
    def _proto_to_dict(self, proto_request) -> dict:
        """Конвертирует proto request в Python dict"""
        return {
            "transaction_id": proto_request.transaction_id,
            "timestamp": proto_request.timestamp,
            "sender_account": proto_request.sender_account,
            "receiver_account": proto_request.receiver_account,
            "amount": proto_request.amount,
            "transaction_type": proto_request.transaction_type,
            "merchant_category": proto_request.merchant_category,
            "location": proto_request.location,
            "device_used": proto_request.device_used,
            "payment_channel": proto_request.payment_channel,
            "ip_address": proto_request.ip_address,
            "device_hash": proto_request.device_hash,
            "time_since_last_transaction": proto_request.time_since_last_transaction,
            "spending_deviation_score": proto_request.spending_deviation_score,
            "velocity_score": proto_request.velocity_score,
            "geo_anomaly_score": proto_request.geo_anomaly_score,
            "correlation_id": proto_request.correlation_id
        }
    
async def serve():
    """Запуск gRPC сервера"""
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=MAX_WORKERS),
        options=[
            ('grpc.max_send_message_length', 50 * 1024 * 1024),
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),
        ]
    )
    
    SERVICE_NAMES = (
        ml_pb2.DESCRIPTOR.services_by_name['MLService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    service = MLServiceServicer()
    await service.model_config.fetch_threshold()

    ml_pb2_grpc.add_MLServiceServicer_to_server(service, server)
    
    server.add_insecure_port(f'[::]:{GRPC_PORT}')
    
    logger.info(f"gRPC Server starting on port {GRPC_PORT}")
    logger.info(f"Workers: {MAX_WORKERS}")
    
    await server.start()
    logger.info("Server started successfully!")
    
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await server.stop(0)


if __name__ == '__main__':
    asyncio.run(serve())