import os

from dotenv import load_dotenv

load_dotenv()


db_url = os.getenv("DATABASE_URL")

TORTOISE_ORM = {
    "connections": {"default": db_url},
    "apps": {
        "models": {
            # Укажите только модуль
            "models": ["app.database.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
