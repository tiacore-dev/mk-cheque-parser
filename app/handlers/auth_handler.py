from fastapi import Header, HTTPException

from config import Settings


async def check_api_key(x_api_key: str = Header(...)):
    if str(x_api_key) == str(Settings.API_KEY):
        return "ok"
    else:
        raise HTTPException(status_code=401, detail="Неверный апи ключ")
