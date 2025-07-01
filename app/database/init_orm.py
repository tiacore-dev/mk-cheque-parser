from loguru import logger
from tortoise import Tortoise

from config import Settings

# DATABASE_URL = f"postgres://{Settings.DB_USER}:{Settings.DB_PASSWORD}@{Settings.DB_HOST}:{int(Settings.DB_PORT)}/{Settings.DB_NAME}"
DATABASE_URL = Settings.DATABASE_URL


async def init_db():
    logger.info("🔌 Инициализация Tortoise ORM без FastAPI")
    await Tortoise.init(
        db_url=DATABASE_URL, modules={"models": ["app.database.models"]}
    )

    logger.info("✅ База данных готова")
