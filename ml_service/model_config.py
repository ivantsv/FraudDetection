import grpc
import logging
import os

from generated import metadata_pb2_grpc, metadata_pb2

logger = logging.getLogger(__name__)

class ModelConfig:
    def __init__(self, threshold: float = 0.5):
        self.metadata_url = os.getenv(
            "METADATA_SERVICE_URL",
            "metadata-service:50052"
        )
    
    @property
    def threshold(self):
        return self._threshold
    
    async def fetch_threshold(self):
        """Получить threshold из Metadata Service"""
        try:
            async with grpc.aio.insecure_channel(self.metadata_url) as channel:
                stub = metadata_pb2_grpc.MetadataDBStub(channel)
                
                response = await stub.GetMLConfig(
                    metadata_pb2.GetMLConfigRequest(),
                    timeout=5.0
                )
                
                self._threshold = response.threshold
                logger.info(f"Threshold from metadata: {self._threshold}")
                
                return self._threshold
                
        except grpc.aio.AioRpcError as e:
            logger.error(f"Failed to fetch threshold: {e.code()}")
            return self._threshold
        except Exception as e:
            logger.error(f"Error: {e}")
            return self._threshold