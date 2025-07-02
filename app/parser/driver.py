from contextlib import contextmanager

from app.parser.helpers import create_firefox_driver


@contextmanager
def selenium_driver():
    driver = create_firefox_driver()
    try:
        yield driver
    finally:
        driver.quit()
