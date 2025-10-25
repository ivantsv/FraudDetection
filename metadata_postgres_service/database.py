import os
from pathlib import Path
from decimal import Decimal
import logging

from sqlalchemy import text, DECIMAL
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost:5432/metadata"
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


class MLConfig(Base):
    """Таблица ml_configs"""
    __tablename__ = "ml_configs"

    id: Mapped[int] = mapped_column(primary_key=True)
    threshold: Mapped[Decimal] = mapped_column(
        DECIMAL(5, 3), 
        nullable=False, 
        default=Decimal("0.5")
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
            await conn.execute(text(sql))
    
    logger.info("Migrations applied")


async def init_db():
    """Инициализация БД"""
    await apply_migrations()
    
    async with async_session_maker() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM ml_configs"))
        count = result.scalar()
        
        if count == 0:
            await session.execute(
                text("INSERT INTO ml_configs (threshold) VALUES (0.5)")
            )
            await session.commit()
            logger.info("Created default config (threshold=0.5)")
    
    logger.info("Database ready")
