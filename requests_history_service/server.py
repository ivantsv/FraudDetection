import asyncio
import grpc
import logging
import os
import sys
from pathlib import Path
from sqlalchemy import insert, select
from grpc_reflection.v1alpha import reflection
from datetime import datetime

from generated_proto import transactions_pb2, transactions_pb2_grpc
from database import async_session_maker, init_db, TransactionHistory

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

GRPC_PORT = os.getenv("GRPC_PORT", "50053")

class TransactionsDBServicer(transactions_pb2_grpc.TransactionsDBServicer):
    """Async реализация TransactionsDB сервиса"""
    
    async def InsertTransaction(self, request, context):
        """Добавить транзакцию в историю"""
        async with async_session_maker() as db:
            try:
                ts = datetime.strptime(request.timestamp, "%Y-%m-%dT%H:%M:%S.%f")

                stmt = insert(TransactionHistory).values(
                    transaction_id=request.transaction_id,
                    timestamp=ts,
                    sender_account=request.sender_account,
                    receiver_account=request.receiver_account,
                    amount=request.amount,
                    transaction_type=request.transaction_type,
                    merchant_category=request.merchant_category,
                    location=request.location,
                    device_used=request.device_used,
                    payment_channel=request.payment_channel,
                    ip_address=request.ip_address,
                    device_hash=request.device_hash,
                    correlation_id=request.correlation_id,
                )
                
                await db.execute(stmt)
                await db.commit()

                logger.info(f"Transaction inserted: {request.correlation_id}")
                
                return transactions_pb2.InsertTransactionResponse(
                    status="success",
                )
                
            except Exception as e:
                logger.error(f"Transaction inserte failed: {e}, correlation_id: {request.correlation_id}")
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(e))
                return transactions_pb2.InsertTransactionResponse(status="failure")
    
    async def HealthCheck(self, request, context):
        """Health check"""
        async with async_session_maker() as db:
            try:
                await db.execute(select(1))
                return transactions_pb2.HealthCheckResponse(status="healthy")
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                context.set_code(grpc.StatusCode.UNAVAILABLE)
                return transactions_pb2.HealthCheckResponse(status="unhealthy")
            
async def serve():
    """Запуск async gRPC сервера"""
    logger.info("Initializing database...")
    await init_db()
    
    server = grpc.aio.server()

    SERVICE_NAMES = (
        transactions_pb2.DESCRIPTOR.services_by_name['TransactionsDB'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    
    transactions_pb2_grpc.add_TransactionsDBServicer_to_server(
        TransactionsDBServicer(), 
        server
    )
    
    server.add_insecure_port(f'[::]:{GRPC_PORT}')
    
    logger.info(f"TransactionsDB Service starting on port {GRPC_PORT}")
    
    await server.start()
    logger.info("Server started!")
    
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await server.stop(0)


if __name__ == '__main__':
    asyncio.run(serve())