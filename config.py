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

    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", str(5432))
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
