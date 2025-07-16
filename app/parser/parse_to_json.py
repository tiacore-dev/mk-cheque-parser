import re
from datetime import datetime

import pytz
from loguru import logger

from app.database.models import Cheque, Item

# Часовой пояс Новосибирска
nsk_tz = pytz.timezone("Asia/Novosibirsk")


def parse_kkt_number(kkm_string):
    """Вытаскиваем номер ККТ из строки типа (Весенняя, 16 №00307401940391)"""
    match = re.search(r"№(\d+)", kkm_string)
    return match.group(1) if match else None


def parse_date(date_str: str):
    for fmt in ("%d.%m.%Y %H:%M", "%d.%m.%Y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


async def put_to_db(cheque):
    cheque_obj, created = await Cheque.get_or_create(
        id=cheque["cheque_id"],
        defaults={
            "name": cheque["name"],
            "date": parse_date(cheque["date"]),
            "total_price": cheque["total"],
            "kkt_number": cheque["kkt_number"],
        },
    )

    if not created:
        return

    items = cheque["items"]
    logger.info(f"Чек успешно создан в базе: {cheque_obj.id}")
    for idx, item in enumerate(items, start=1):
        try:
            price_per_unit = item["price_per_unit"]
            quantity = float(item["quantity"])
            await Item.create(
                id=f"{cheque_obj.id}_{idx}",
                name=item["name"],
                cheque=cheque_obj,
                quantity=item["quantity"],
                price_per_unit=price_per_unit,
                total=round(quantity * price_per_unit, 2),
            )

        except Exception as e:
            logger.error(f"Ошибка парсинга позиции: {e}, item={item}")

    return
