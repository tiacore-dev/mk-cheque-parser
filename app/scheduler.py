from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger

from app.parser.main_parser import main_parser
from config import Settings

# Инициализация планировщика с использованием SQLAlchemy для хранения задач
scheduler = BackgroundScheduler()


def start_scheduler():
    scheduler.add_job(
        main_parser,
        trigger="interval",
        minutes=2,
        id="test_job",
        replace_existing=True,
        args=[Settings.BASE_URL, Settings.LOGIN, Settings.PASSWORD],
    )

    scheduler.add_job(
        main_parser,
        trigger="cron",
        minute="0,30",
        id="parse_job",
        replace_existing=True,
        args=[Settings.BASE_URL, Settings.LOGIN, Settings.PASSWORD],
    )
    scheduler.start()

    logger.info("Планировщик успешно запущен с задачами из базы.")
    logger.info(f"Запущенные задачи: {scheduler.get_jobs()}")
