from dotenv import load_dotenv

from config import Settings

load_dotenv()


DATABASE_URL = Settings.DATABASE_URL

TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            # Укажите только модуль
            "models": ["app.database.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
