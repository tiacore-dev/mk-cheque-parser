import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")

    BASE_URL = os.getenv("BASE_URL")
    LOGIN = os.getenv("LOGIN")
    PASSWORD = os.getenv("PASSWORD")
    DB_URL = os.getenv("DATABASE_URL")
    API_KEY = os.getenv("API_KEY")
    SEND_URL = os.getenv("SEND_URL", "")
