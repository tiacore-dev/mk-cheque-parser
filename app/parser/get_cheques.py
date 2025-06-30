import time

from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.parser.helpers import (
    close_modal,
    safe_click,
    safe_click_element,
    wait_modal_disappear,
)
from app.parser.pagination import go_to_next_page
from app.parser.parse_cheque import parse_cheque_modal
from app.parser.parse_to_json import build_cheque_json


def fetch_all_cheques(driver, url):
    wait = WebDriverWait(driver, timeout=30)

    logger.info("Переходим на страницу поиска чеков")
    driver.get(f"{url}/web/auth/cheques/search")

    safe_click(driver, "//a[contains(text(), 'вчера')]", "кнопка 'вчера'")
    logger.info(f"Текущий URL: {driver.current_url}")
    safe_click(driver, "//button[contains(text(), 'Применить')]", "кнопка 'Применить'")
    logger.info(f"Текущий URL: {driver.current_url}")

    logger.info("Запускаем сбор всех чеков со всех страниц")
    all_cheques = []
    page_number = 1

    while True:
        logger.info(f"Парсим страницу {page_number}")

        WebDriverWait(driver, 60).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "loader_spinner"))
        )

        table_xpath = "//table[contains(@class, 'table-cheques')]"
        wait.until(EC.presence_of_element_located((By.XPATH, table_xpath)))
        logger.info("Таблица чеков загружена")

        # ❗ Поиск rows всегда заново, после перехода
        rows = driver.find_elements(By.XPATH, f"{table_xpath}//tbody/tr")
        visible_rows = [row for row in rows if row.is_displayed()]
        logger.info(f"Найдено видимых чеков на странице: {len(visible_rows)}")

        if not visible_rows:
            logger.info("Чеки не найдены на странице, пробуем перейти на следующую")
            if not go_to_next_page(driver):
                logger.info("Следующей страницы нет, завершаем")
                break
            page_number += 1
            continue

        # Обработка чеков именно для этой страницы
        cheques = fetch_cheques(driver)
        all_cheques.extend(cheques)

        if not go_to_next_page(driver):
            logger.info("Следующей страницы нет, завершаем")
            break

        page_number += 1

    logger.info(f"Сбор чеков завершён. Всего чеков: {len(all_cheques)}")
    return all_cheques


def fetch_cheques(driver):
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, "//table[contains(@class, 'table-cheques')]//tbody")
        )
    )

    cheque_data = []

    rows = driver.find_elements(
        By.XPATH, "//table[contains(@class, 'table-cheques')]//tbody/tr"
    )
    logger.info(f"Чеков на странице: {len(rows)}")

    for index, row in enumerate(rows, start=1):
        try:
            wait_modal_disappear(driver)

            href = row.get_attribute("href")
            check_number = href.split("/")[-1].split("?")[0] if href else "Неизвестно"

            tds = row.find_elements(By.TAG_NAME, "td")
            name = tds[2].text.strip() if len(tds) > 2 else "Неизвестно"
            date = tds[3].text.strip() if len(tds) > 3 else "Неизвестно"

            # Номер ККТ
            device_elements = row.find_elements(By.CLASS_NAME, "device-name")
            kkt_number = (
                device_elements[0].text.strip() if device_elements else "Неизвестно"
            )

            # Сумма — предпоследняя колонка
            total_price = tds[-2].text.strip() if len(tds) >= 2 else "Неизвестно"

            safe_click_element(driver, row, description=f"чек {check_number}")
            time.sleep(0.5)
            items = parse_cheque_modal(driver)

            # logger.info(
            #     f"""Чек {check_number} от {date} на сумму {total_price}
            #     ({kkt_number}), items: {items}"""
            # )

            # cheque_data.append(
            #     {
            #         "check_id": check_number,
            #         "date": date,
            #         "kkm_name": kkt_number,
            #         "total": total_price,
            #         "url": href,
            #         "items": items,
            #     }
            # )
            cheque_json = build_cheque_json(
                check_number=check_number,
                name=name,
                date=date,
                total_price=total_price,
                kkm_name=kkt_number,
                items_raw=items,
            )

            logger.info(f"Собранный чек: {cheque_json}")

            close_modal(driver)

        except Exception as e:
            logger.error(f"Ошибка при обработке чека {index}: {e}")
            continue

    return cheque_data
