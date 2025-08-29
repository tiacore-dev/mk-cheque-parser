import time
from datetime import datetime

# from datetime import datetime
import requests
from loguru import logger
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.parser.dates import build_cheques_search_url
from app.parser.helpers import (
    close_modal,
    safe_click,
    safe_click_element,
    wait_modal_disappear,
)
from app.parser.pagination import go_to_next_page
from app.parser.parse_cheque import parse_cheque_modal, parse_price
from app.parser.parse_to_json import parse_kkt_number, put_to_db
from config import Settings


async def fetch_all_cheques(driver, url):
    wait = WebDriverWait(driver, timeout=30)

    logger.info("Переходим на страницу поиска чеков")
    # 1) Строим URL с нужными датами
    start_datetime = datetime(2025, 8, 29, 7, 00)
    end_datetime = datetime(2025, 8, 29, 20, 00)
    search_url = build_cheques_search_url(url, start_datetime, end_datetime)
    logger.info(f"Переходим на страницу поиска чеков: {search_url}")
    driver.get(search_url)

    # 2) (Опционально) проверим, что в инпутах действительно нужные значения
    # try:
    #     start_val = (
    #         WebDriverWait(driver, 20)
    #         .until(EC.presence_of_element_located((By.CSS_SELECTOR, ".js__date_start input")))
    #         .get_attribute("value")
    #     )
    #     end_val = driver.find_element(By.CSS_SELECTOR, ".js__date_finish input").get_attribute("value")
    #     logger.info(f"Страница прочитала даты: start={start_val}, end={end_val}")
    # except Exception as e:
    #     logger.warning(f"Не удалось прочитать значения дат из инпуто: {e}")

    # 3) Жмём «Применить», чтобы гарантированно обновить выдачу
    apply_btn_xpath = "//button[contains(text(), 'Применить')]"
    wait.until(EC.element_to_be_clickable((By.XPATH, apply_btn_xpath))).click()
    logger.info("Нажали 'Применить'")

    # 4) Ждём, пока пропадёт спиннер
    try:
        WebDriverWait(driver, 60).until(EC.invisibility_of_element_located((By.CLASS_NAME, "loader_spinner")))
    except TimeoutException:
        logger.warning("Лоадер не исчез за 60с — продолжаем аккуратно")

    # safe_click(driver, "//a[contains(text(), '3 часа')]", "кнопка '3 часа'")
    # safe_click(driver, "//a[contains(text(), 'вчера')]", "кнопка 'вчера'")
    logger.info(f"Текущий URL: {driver.current_url}")
    logger.info(f"Заголовок страницы: {driver.title}")
    time.sleep(0.5)
    safe_click(driver, "//button[contains(text(), 'Применить')]", "кнопка 'Применить'")
    logger.info(f"Текущий URL: {driver.current_url}")
    logger.info(f"Заголовок страницы: {driver.title}")
    time.sleep(1)

    logger.info("Запускаем сбор всех чеков со всех страниц")
    all_cheques = []
    page_number = 1

    while True:
        logger.info(f"Парсим страницу {page_number}")

        WebDriverWait(driver, 60).until(EC.invisibility_of_element_located((By.CLASS_NAME, "loader_spinner")))

        table_xpath = "//table[contains(@class, 'table-cheques')]"
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, table_xpath)))
        except Exception:
            logger.info("Таблица чеков не найдена, чеков нет на странице")
            return all_cheques

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
        cheques = await fetch_cheques(driver)
        all_cheques.extend(cheques)

        if not go_to_next_page(driver):
            logger.info("Следующей страницы нет, завершаем")
            break
        logger.info(f"Чеков собрано с этой страницы: {len(cheques)}")

        page_number += 1

    logger.info(f"Сбор чеков завершён. Всего чеков: {len(all_cheques)}")
    return all_cheques


async def fetch_cheques(driver):
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//table[contains(@class, 'table-cheques')]//tbody"))
    )

    cheque_data = []

    rows = driver.find_elements(By.XPATH, "//table[contains(@class, 'table-cheques')]//tbody/tr")
    visible_rows = [row for row in rows if row.is_displayed()]
    logger.info(f"Чеков на странице: {len(visible_rows)}")

    for index, row in enumerate(visible_rows, start=1):
        try:
            wait_modal_disappear(driver)

            href = row.get_attribute("href")
            check_number = href.split("/")[-1].split("?")[0] if href else "Неизвестно"

            tds = row.find_elements(By.TAG_NAME, "td")
            name = tds[2].text.strip() if len(tds) > 2 else "Неизвестно"
            date = tds[3].text.strip() if len(tds) > 3 else "Неизвестно"

            device_elements = row.find_elements(By.CLASS_NAME, "device-name")
            kkt_number = device_elements[0].text.strip() if device_elements else "Неизвестно"

            total_price = tds[-2].text.strip() if len(tds) >= 2 else "Неизвестно"

            safe_click_element(driver, row, description=f"чек {check_number}")
            time.sleep(0.5)
            items = parse_cheque_modal(driver)

            # Фильтруем валидные товары
            valid_items = [
                item
                for item in items
                if item["name"].strip() and float(item["quantity"]) > 0 and float(item["price_per_unit"]) > 0
            ]

            # Сумма по позициям
            items_total = round(sum(float(item["quantity"]) * float(item["price_per_unit"]) for item in valid_items), 2)
            parsed_total = parse_price(total_price)

            # Проверка всех условий
            if (
                len(valid_items) != len(items) or abs(items_total - parsed_total) > 1.0  # можно ужесточить до 0.01
            ):
                logger.warning(
                    f"❌ Чек {check_number} невалиден — позиции: {len(valid_items)}/{len(items)}, "
                    f"сумма: {items_total} vs {parsed_total}"
                    f"Данные: kkt: {(parse_kkt_number(kkt_number),)}, date: {date}"
                )
                close_modal(driver)
                continue

            cheque_json = {
                "cheque_id": check_number,
                "name": name,
                "kkt_number": parse_kkt_number(kkt_number),
                "date": date,
                "total": parse_price(total_price),
                "items": items,
            }

            headers = {"content-type": "application/json"}
            response = requests.post(url=Settings.SEND_URL, json=cheque_json, headers=headers)
            if response.ok:
                logger.info(f"✅ Отправлено успешно! [{response.status_code}] — {response.text}")
                await put_to_db(cheque_json)
                cheque_data.append(cheque_json)
                logger.info(f"Чек сохранён: {cheque_json['cheque_id']}")
            else:
                logger.warning(f"⚠️ Ошибка при отправке! [{response.status_code}] — {response.text}")
                continue

            # cheque_data.append(cheque_json)

            logger.info(f"Собранный чек: {cheque_json}")

            close_modal(driver)

        except Exception as e:
            logger.error(f"Ошибка при обработке чека {index}: {e}")
            continue

    return cheque_data
