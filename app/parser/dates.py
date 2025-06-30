from datetime import datetime

from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def select_date_range(driver, start_datetime: datetime, end_datetime: datetime):
    wait = WebDriverWait(driver, 20)

    start_str = start_datetime.strftime("%d.%m.%Y %H:%M")
    end_str = end_datetime.strftime("%d.%m.%Y %H:%M")

    logger.info(f"Выбираем диапазон дат: {start_str} — {end_str}")

    # Ждём поля ввода дат
    start_date_field = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//span[contains(@class, 'js__date_start')]")
        )
    )
    end_date_field = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//span[contains(@class, 'js__date_finish')]")
        )
    )

    # Кликаем, чтобы открыть календарь
    start_date_field.click()
    # Выбираем input внутри спана
    input_start = start_date_field.find_element(By.TAG_NAME, "input")
    input_start.clear()
    input_start.send_keys(start_str)

    end_date_field.click()
    input_end = end_date_field.find_element(By.TAG_NAME, "input")
    input_end.clear()
    input_end.send_keys(end_str)

    logger.info("Диапазон дат введён")
