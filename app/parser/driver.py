from contextlib import contextmanager

from app.parser.helpers import create_chrome_driver


@contextmanager
def selenium_driver():
    driver = create_chrome_driver()
    try:
        yield driver
    finally:
        driver.quit()
