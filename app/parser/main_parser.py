from app.parser.driver import selenium_driver
from app.parser.get_cheques import fetch_all_cheques
from app.parser.login import login_to_platform


def main_parser(url, username, password):
    with selenium_driver() as driver:
        login_to_platform(url, username, password, driver)
        checks = fetch_all_cheques(driver, url)
        return checks
