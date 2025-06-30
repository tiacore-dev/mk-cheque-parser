import re
from datetime import datetime

from loguru import logger


def parse_kkt_number(kkm_string):
    """Вытаскиваем номер ККТ из строки типа (Весенняя, 16 №00307401940391)"""
    match = re.search(r"№(\d+)", kkm_string)
    return match.group(1) if match else None


def parse_price(price_str):
    """Парсим строку '50 ₽' → 50.0"""
    return (
        float(price_str.replace("₽", "").replace(",", ".").strip())
        if price_str
        else 0.0
    )


def build_cheque_json(check_number, name, date, total_price, kkm_name, items_raw):
    cheque_id = check_number
    kkt_number = parse_kkt_number(kkm_name)
    total = parse_price(total_price)

    items = []
    for idx, item in enumerate(items_raw, start=1):
        try:
            quantity = (
                int(item["quantity"].replace(",", ".").split()[0])
                if item["quantity"]
                else 0
            )
            price_per_unit = parse_price(item["price_per_unit"])

            items.append(
                {
                    "item_id": f"{cheque_id}_{idx}",
                    "name": item["name"],
                    "quantity": quantity,
                    "price_per_unit": price_per_unit,
                    "total": round(quantity * price_per_unit, 2),
                }
            )
        except Exception as e:
            logger.error(f"Ошибка парсинга позиции: {e}, item={item}")
    try:
        date_obj = datetime.strptime(date, "%d.%m.%Y %H:%M")
    except ValueError:
        try:
            date_obj = datetime.strptime(date, "%d.%m.%Y")
        except ValueError:
            date_obj = None  # или подставить datetime.now()

    cheque = {
        "cheque_id": cheque_id,
        "name": name,  # если фиксировано
        "kkt_number": kkt_number,
        "date": date_obj,  # или под свой формат
        "total": total,
        "items": items,
    }

    return cheque
