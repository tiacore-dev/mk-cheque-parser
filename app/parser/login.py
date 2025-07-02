from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def login_to_platform(url, username, password, driver):
    logger.info(f"🌐 Открываем страницу {url}")
    try:
        driver.get(url)
    except Exception as e:
        logger.exception(f"❌ Ошибка при открытии {url}: {e}")
        raise

    wait = WebDriverWait(driver, timeout=30)

    logger.info("🔗 Ожидание кнопки 'Войти'")
    try:
        login_button = wait.until(EC.element_to_be_clickable((By.ID, "login_link_id")))
        logger.info("✅ Кнопка найдена, кликаем")
        login_button.click()
    except Exception as e:
        logger.exception(f"❌ Не удалось найти или нажать кнопку входа: {e}")
        raise

    logger.info("⌨️ Ожидание полей для ввода логина и пароля")
    try:
        username_field = wait.until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_field = wait.until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        logger.info("✅ Поля найдены, вводим данные")
        username_field.send_keys(username)
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
    except Exception as e:
        logger.exception(f"❌ Ошибка при вводе логина/пароля: {e}")
        raise

    logger.info("⏳ Ожидание перехода на дашборд")
    try:
        wait.until(lambda d: d.current_url.startswith(f"{url}/web/auth/dashboard"))
        logger.info(f"✅ Успешный вход. Текущий URL: {driver.current_url}")
        logger.info(f"🪧 Заголовок страницы: {driver.title}")
    except Exception as e:
        logger.exception(f"❌ Не дождались перехода на дашборд: {e}")
        raise

    return driver
