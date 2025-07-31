from datetime import datetime
from urllib.parse import urlencode, urljoin

DATE_FMT = "%d.%m.%Y %H:%M"


def build_cheques_search_url(
    base_url: str,
    start_dt: datetime,
    end_dt: datetime,
    device_id: str = "Все терминалы",
    extra_params: dict | None = None,
) -> str:
    """
    Собирает URL вида:
    {base}/web/auth/cheques/search?start=...&end=...&deviceId=...
    """
    q = {
        "deviceId": device_id,
        "start": start_dt.strftime(DATE_FMT),
        "end": end_dt.strftime(DATE_FMT),
        "shiftNumber": "",
        "requestNumber": "",
        "sumFrom": "",
        "sumTo": "",
        "cashiers": "[]",
        "tag": "",
        "tagSearchField": "",
        "_fnsFdSentStatus": "on",
        "_paymentTypes": "on",
        "_operTypes": "on",
    }
    if extra_params:
        q.update(extra_params)

    # urlencode правильно закодирует кириллицу, пробелы, двоеточия
    query = urlencode(q, doseq=True, encoding="utf-8")
    return urljoin(base_url.rstrip("/") + "/", "web/auth/cheques/search") + "?" + query
