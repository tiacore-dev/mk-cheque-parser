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


async def build_cheque_json(check_number, name, date, total_price, kkm_name, items_raw):
    cheque_id = check_number
    kkt_number = parse_kkt_number(kkm_name)
    total = total_price
    try:
        date_obj = datetime.strptime(date, "%d.%m.%Y %H:%M")
    except ValueError:
        try:
            date_obj = datetime.strptime(date, "%d.%m.%Y")
        except ValueError:
            date_obj = None  # или подставить datetime.now()
    cheque, created = await Cheque.get_or_create(
        id=check_number,
        defaults={
            "name": name,
            "date": date_obj,
            "total_price": total,
            "kkt_number": kkt_number,
        },
    )

    items = []
    if not created:
        logger.info(f"Чек {cheque.id} уже есть в базе, пропускаем парсинг items.")
        cheque_with_items = await Cheque.get(id=cheque.id).prefetch_related("items")
        items = [
            {
                "item_id": item.id,
                "name": item.name,
                "quantity": item.quantity,
                "price_per_unit": float(item.price_per_unit),
                "total": float(item.total),
            }
            for item in cheque_with_items.items
        ]
        local_date = cheque_with_items.date.astimezone(nsk_tz)

        return {
            "cheque_id": cheque_with_items.id,
            "name": cheque_with_items.name,
            "kkt_number": cheque_with_items.kkt_number,
            "date": local_date.strftime("%d.%m.%Y %H:%M"),
            "total": float(cheque_with_items.total_price),
            "items": items,
        }

    logger.info(f"Чек успешно создан в базе: {cheque.id}")
    for idx, item in enumerate(items_raw, start=1):
        try:
            quantity = (
                int(item["quantity"].replace(",", ".").split()[0])
                if item["quantity"]
                else 0
            )
            price_per_unit = item["price_per_unit"]
            item_obj = await Item.create(
                id=f"{cheque_id}_{idx}",
                name=item["name"],
                cheque=cheque,
                quantity=quantity,
                price_per_unit=price_per_unit,
                total=round(quantity * price_per_unit, 2),
            )
            items.append(
                {
                    "item_id": item_obj.id,
                    "name": item_obj.name,
                    "quantity": item_obj.quantity,
                    "price_per_unit": float(item_obj.price_per_unit),
                    "total": float(item_obj.total),
                }
            )

        except Exception as e:
            logger.error(f"Ошибка парсинга позиции: {e}, item={item}")

    cheque = {
        "cheque_id": cheque_id,
        "name": name,  # если фиксировано
        "kkt_number": kkt_number,
        "date": date_obj,  # или под свой формат
        "total": total,
        "items": items,
    }

    return cheque
