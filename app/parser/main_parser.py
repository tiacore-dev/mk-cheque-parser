from concurrent.futures import ThreadPoolExecutor

from loguru import logger

from app.database.models import ParseMethod
from app.parser.driver import selenium_driver
from app.parser.get_cheques import fetch_all_cheques
from app.parser.login import login_to_platform

executor = ThreadPoolExecutor()


async def main_parser(url, username, password):
    logger.info("Парсер запущен")
    with selenium_driver() as driver:
        login_to_platform(url, username, password, driver)
        checks = await fetch_all_cheques(driver, url, ParseMethod.STANDARD)
        return checks
