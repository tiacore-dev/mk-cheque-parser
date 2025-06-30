from loguru import logger
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.parser.helpers import wait_modal_disappear


def go_to_next_page(driver):
    wait_modal_disappear(driver)
    try:
        pagination = driver.find_element(By.CLASS_NAME, "pagination")
        current_page = pagination.find_element(By.CLASS_NAME, "active")

        next_li = current_page.find_element(By.XPATH, "./following-sibling::li[1]")

        classes = next_li.get_attribute("class")
        if "disabled" in classes:
            logger.info("Следующей страницы нет, заканчиваем парсинг")
            return False

        next_link = next_li.find_element(By.TAG_NAME, "a")
        logger.info("Переходим на следующую страницу чеков")
        # Ждём исчезновение модалки (если есть)
        try:
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.ID, "common-modal-content"))
            )
        except Exception:
            pass

        # Ждём исчезновение затемняющего фона
        try:
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "modal-backdrop"))
            )
        except Exception:
            pass

        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", next_link
        )
        next_link.click()

        # Ждём исчезновение лоадера и появления таблицы
        WebDriverWait(driver, 30).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "loader_spinner"))
        )
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, "//table[contains(@class, 'table-cheques')]")
            )
        )

        return True

    except NoSuchElementException:
        logger.info("Пагинации не найдено, парсинг закончен")
        return False

    except Exception as e:
        logger.error(f"Ошибка при переходе на следующую страницу: {e}")
        return False
