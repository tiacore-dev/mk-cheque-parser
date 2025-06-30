from loguru import logger
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.parser.decorators import retry_on_stale


@retry_on_stale()
def parse_cheque_modal(driver):
    wait = WebDriverWait(driver, 20)

    try:
        wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[contains(@class, 'cheque-preview__body')]//table//tbody",
                )
            )
        )
    except Exception:
        logger.warning("Не удалось найти модалку с деталями чека")
        return []

    items = []

    try:
        rows = wait.until(
            EC.presence_of_all_elements_located(
                (
                    By.XPATH,
                    "//div[contains(@class, 'cheque-preview__body')]//table//tbody//tr",
                )
            )
        )
    except Exception:
        logger.info("Нет строк с товарами в чеке")
        return []

    logger.info(f"Найдено строк в модалке: {len(rows)}")

    for index in range(1, len(rows) + 1):
        try:
            # Всегда берём строку заново, чтобы избежать stale
            row_xpath = (
                f"(//div[contains(@class, 'cheque-preview__body')]"
                f"//table//tbody//tr)[{index}]"
            )
            row = driver.find_element(By.XPATH, row_xpath)

            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) < 4:
                logger.warning(f"Недостаточно ячеек в строке {index}")
                continue

            name = cells[0].text.strip()
            quantity = cells[1].text.strip()
            price_per_unit = cells[2].text.strip()
            total = cells[3].text.strip()

            items.append(
                {
                    "name": name,
                    "quantity": quantity,
                    "price_per_unit": price_per_unit,
                    "total": total,
                }
            )

        except StaleElementReferenceException as e:
            logger.error(f"StaleElementReference в строке {index}: {e}")
            continue
        except Exception as e:
            logger.error(f"Ошибка при парсинге строки {index}: {e}")
            continue

    logger.info(f"Найдено позиций в чеке: {len(items)}")
    return items
