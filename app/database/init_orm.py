from loguru import logger
from tortoise import Tortoise

from config import Settings

DATABASE_URL = Settings.DATABASE_URL
print(DATABASE_URL)


async def init_db():
    logger.info("🔌 Инициализация Tortoise ORM без FastAPI")
    await Tortoise.init(
        db_url=DATABASE_URL, modules={"models": ["app.database.models"]}
    )

    logger.info("✅ База данных готова")
