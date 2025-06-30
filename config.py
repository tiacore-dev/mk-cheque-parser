import os

from dotenv import load_dotenv

load_dotenv()

url = os.getenv("BASE_URL")
login = os.getenv("LOGIN")
password = os.getenv("PASSWORD")
