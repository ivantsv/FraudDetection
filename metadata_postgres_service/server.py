import asyncio
import grpc
import logging
import os
import sys
from pathlib import Path
from sqlalchemy import select
from grpc_reflection.v1alpha import reflection

from generated_proto import metadata_pb2, metadata_pb2_grpc
from database import async_session_maker, init_db, MLConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

GRPC_PORT = os.getenv("GRPC_PORT", "50052")

class MetadataDBServicer(metadata_pb2_grpc.MetadataDBServicer):
    """Async реализация MetadataDB сервиса"""
    
    async def GetMLConfig(self, request, context):
        """Получить ML конфиг (threshold)"""
        async with async_session_maker() as db:
            try:
                result = await db.execute(select(MLConfig))
                config = result.scalars().first()
                
                if config:
                    threshold = float(config.threshold)
                else:
                    threshold = 0.5
                
                logger.info(f"GetMLConfig: threshold={threshold}")
                
                return metadata_pb2.MLConfigResponse(threshold=threshold)
                
            except Exception as e:
                logger.error(f"GetMLConfig failed: {e}")
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(e))
                return metadata_pb2.MLConfigResponse(threshold=0.5)
    
    async def HealthCheck(self, request, context):
        """Health check"""
        async with async_session_maker() as db:
            try:
                await db.execute(select(1))
                return metadata_pb2.HealthCheckResponse(status="healthy")
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                context.set_code(grpc.StatusCode.UNAVAILABLE)
                return metadata_pb2.HealthCheckResponse(status="unhealthy")
            
async def serve():
    """Запуск async gRPC сервера"""
    logger.info("Initializing database...")
    await init_db()
    
    server = grpc.aio.server()

    SERVICE_NAMES = (
        metadata_pb2.DESCRIPTOR.services_by_name['MetadataDB'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    
    metadata_pb2_grpc.add_MetadataDBServicer_to_server(
        MetadataDBServicer(), 
        server
    )
    
    server.add_insecure_port(f'[::]:{GRPC_PORT}')
    
    logger.info(f"MetadataDB Service starting on port {GRPC_PORT}")
    
    await server.start()
    logger.info("Server started!")
    
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await server.stop(0)


if __name__ == '__main__':
    asyncio.run(serve())
