# utils/helpers.py

import re

from loguru import logger
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.parser.decorators import retry_on_stale


def clean_html(html):
    """
    Удаляет лишние </div> внутри <td>, учитывая пробельные символы и переносы строк.
    """
    cleaned_html = re.sub(r"</div>\s*</td>", "</td>", html, flags=re.IGNORECASE)
    return cleaned_html


def create_firefox_driver():
    logger.info("🚗 Попытка запуска Firefox драйвера")
    try:
        options = Options()
        options.add_argument("-headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Firefox(options=options)
        logger.info("✅ Firefox драйвер успешно запущен")
        return driver
    except Exception as e:
        logger.error(f"❌Ошибка при создании драйвера Firefox: {e}")
        raise


def safe_click(driver, xpath, description="элемент"):
    wait = WebDriverWait(driver, 20)
    for attempt in range(5):
        try:
            logger.info(f"Кликаем по {description} (попытка {attempt + 1})")
            element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))

            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
                element,
            )

            element.click()
            return

        except (StaleElementReferenceException, ElementClickInterceptedException) as e:
            logger.warning(
                f"{description} неактуален или перекрыт, пробуем ещё раз: {e}"
            )
            continue

        except ElementNotInteractableException as e:
            logger.warning(
                f"{description} неинтерактивен (возможно скрыт), пытаемся через JS: {e}"
            )
            try:
                driver.execute_script("arguments[0].click();", element)
                return
            except Exception as js_e:
                logger.error(
                    f"Не получилось кликнуть по {description} даже через JS: {js_e}"
                )
                continue

    raise Exception(f"Не удалось кликнуть по {description} после 5 попыток")


@retry_on_stale()
def safe_click_element(driver, element_or_xpath, description="элемент"):
    wait = WebDriverWait(driver, 20)

    try:
        if isinstance(element_or_xpath, str):
            element = wait.until(
                EC.presence_of_element_located((By.XPATH, element_or_xpath))
            )
        else:
            element = element_or_xpath

        driver.execute_script("arguments[0].click();", element)
        logger.info(f"Клик по {description} выполнен через JS")
        return

    except Exception as e:
        logger.error(f"Не удалось кликнуть по {description} через JS: {e}")
        raise


@retry_on_stale()
def close_modal(driver):
    xpath = (
        "//div[@id='common-modal-content']"
        "//button[contains(@class, 'close') and @type='button']"
    )

    try:
        safe_click_element(driver, xpath, description="кнопка закрытия модалки")

        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "common-modal-content"))
        )
        # logger.info("Модальное окно успешно закрыто")

    except Exception as e:
        logger.error(f"Не удалось закрыть модалку: {e}")
        raise


def wait_modal_disappear(driver):
    for desc, locator in [
        ("модалки", (By.ID, "common-modal-content")),
        ("затемняющего фона", (By.CLASS_NAME, "modal-backdrop")),
    ]:
        try:
            WebDriverWait(driver, 10).until(EC.invisibility_of_element_located(locator))
        except TimeoutException:
            logger.info(f"{desc.capitalize()} не обнаружено или уже скрыто")
