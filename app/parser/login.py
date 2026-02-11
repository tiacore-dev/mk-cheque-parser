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

    wait = WebDriverWait(driver, timeout=60)

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

    logger.info("⏳ Ожидание перехода после авторизации")
    try:
        post_login_wait = WebDriverWait(driver, timeout=120)

        def _logged_in(d):
            current_url = d.current_url or ""
            if current_url.startswith(f"{url}/web/auth/"):
                return True
            if current_url.startswith(f"{url}/web/") and "login" not in current_url:
                if "sso-login" in current_url:
                    return False
                return True
            if not d.find_elements(By.NAME, "username") and not d.find_elements(By.NAME, "password"):
                if "sso-login" in current_url:
                    return False
                return True
            return False

        post_login_wait.until(_logged_in)
        logger.info(f"✅ Успешный вход. Текущий URL: {driver.current_url}")
        logger.info(f"🪧 Заголовок страницы: {driver.title}")
    except Exception as e:
        logger.error(f"❌ Текущий URL при ошибке: {driver.current_url}")
        logger.error(f"🪧 Заголовок страницы при ошибке: {driver.title}")
        logger.exception(f"❌ Не дождались перехода на дашборд: {e}")
        raise

    return driver
