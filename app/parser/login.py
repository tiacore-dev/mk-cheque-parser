from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def login_to_platform(url, username, password, driver):
    driver.get(url)

    wait = WebDriverWait(driver, timeout=30)
    logger.info(f"Текущий URL: {driver.current_url}")
    # Нажимаем "Войти"
    login_button = wait.until(EC.element_to_be_clickable((By.ID, "login_link_id")))
    login_button.click()

    # Ждём форму входа
    username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))

    username_field.send_keys(username)
    password_field.send_keys(password)

    password_field.send_keys(Keys.RETURN)

    # Ждём редирект на дашборд
    wait.until(lambda d: d.current_url.startswith(f"{url}/web/auth/dashboard"))

    logger.info(f"Текущий URL: {driver.current_url}")
    logger.info(f"Заголовок страницы: {driver.title}")

    return driver
