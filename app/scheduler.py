from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from app.parser.main_parser import main_parser
from config import Settings

# Инициализация планировщика с использованием SQLAlchemy для хранения задач
scheduler = AsyncIOScheduler(timezone="Asia/Novosibirsk")


async def start_scheduler():
    tz = scheduler.timezone

    # разовый прогон на старте
    scheduler.add_job(
        main_parser,
        trigger="date",
        run_date=datetime.now(tz) + timedelta(seconds=1),
        id="parse_job_once",
        replace_existing=True,
        args=[Settings.BASE_URL, Settings.LOGIN, Settings.PASSWORD],
        misfire_grace_time=60,
    )

    # регулярное расписание
    scheduler.add_job(
        main_parser,
        trigger="cron",
        minute="10,40",
        id="parse_job",
        replace_existing=True,
        args=[Settings.BASE_URL, Settings.LOGIN, Settings.PASSWORD],
    )

    scheduler.start()

    logger.info("Планировщик успешно запущен с задачами из базы.")
    logger.info(f"Запущенные задачи: {scheduler.get_jobs()}")
