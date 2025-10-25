import os
from pathlib import Path
from decimal import Decimal
import logging

from sqlalchemy import TIMESTAMP, CheckConstraint, Double, Index, String, DECIMAL, text, desc
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost:5432/transactions"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False
)

Base = declarative_base()

class TransactionHistory(Base):
    """Таблица истории транзакций"""
    __tablename__ = "transactions_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    transaction_id: Mapped[str] = mapped_column(String(255), nullable=False)
    timestamp: Mapped[str] = mapped_column(TIMESTAMP, nullable=False)

    sender_account: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    receiver_account: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    amount: Mapped[float] = mapped_column(Double, nullable=False)

    transaction_type: Mapped[str] = mapped_column(String(100), nullable=False)
    merchant_category: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    device_used: Mapped[str] = mapped_column(String(100), nullable=False)
    payment_channel: Mapped[str] = mapped_column(String(100), nullable=False)
    ip_address: Mapped[str] = mapped_column(INET, nullable=False)
    device_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(255), nullable=False)

    __table_args__ = (
        CheckConstraint("char_length(sender_account) >= 5", name="chk_sender_account_len"),
        CheckConstraint("char_length(receiver_account) >= 5", name="chk_receiver_account_len"),
        CheckConstraint("amount > 0", name="chk_amount_positive"),
        CheckConstraint("char_length(device_hash) >= 8", name="chk_device_hash_len"),

        Index("idx_transactions_transaction_id", "transaction_id", unique=True),
        Index("idx_transactions_sender", "sender_account"),
        Index("idx_transactions_receiver", "receiver_account"),
        Index("idx_transactions_correlation", "correlation_id"),
        Index("idx_transactions_timestamp", desc("timestamp")),
    )

async def apply_migrations():
    """Применяет SQL миграции из папки migrations/"""
    migrations_path = Path(__file__).parent / "migrations"
    
    if not migrations_path.exists():
        logger.warning("Папка migrations не найдена")
        return
    
    async with engine.begin() as conn:
        for sql_file in sorted(migrations_path.glob("*.sql")):
            logger.info(f"Applying migration: {sql_file.name}")
            sql = sql_file.read_text()
            statements = [stmt.strip() for stmt in sql.split(";") if stmt.strip()]

            for stmt in statements:
                await conn.execute(text(stmt))
    
    logger.info("Migrations applied")

async def init_db():
    """Инициализация БД"""
    await apply_migrations()
    
    async with async_session_maker() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM transactions_history"))
        count = result.scalar()
        

    logger.info(f"Database ready, row count: {count}")
