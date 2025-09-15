from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, Depends, status
from loguru import logger
from tortoise.expressions import Q

from app.database.models import Cheque, ParseMethod
from app.handlers.auth_handler import check_api_key
from app.parser.driver import selenium_driver
from app.parser.get_cheques import fetch_all_cheques
from app.parser.login import login_to_platform
from app.pydantic_models.cheque_models import (
    ChequeFilterSchema,
    ChequeListResponseSchema,
    ChequeSchema,
)
from config import Settings

executor = ThreadPoolExecutor()

# Создаем роутеры
cheque_router = APIRouter()


@cheque_router.post("/cheques", response_model=ChequeListResponseSchema)
async def get_cheques(data: ChequeFilterSchema, _=Depends(check_api_key)):
    query = Q()

    query &= Q(date__gte=data.date_from)
    query &= Q(date__lte=data.date_to)

    total_count = await Cheque.filter(query).count()
    cheques = await Cheque.filter(query).order_by("-date").prefetch_related("items")
    cheques_list = [ChequeSchema.model_validate(cheque) for cheque in cheques]
    return ChequeListResponseSchema(total=total_count, cheques=cheques_list)


@cheque_router.post("/parse", status_code=status.HTTP_204_NO_CONTENT)
async def parse_cheques(data: ChequeFilterSchema, _=Depends(check_api_key)):
    logger.info("Парсер запущен")
    with selenium_driver() as driver:
        login_to_platform(Settings.BASE_URL, Settings.LOGIN, Settings.PASSWORD, driver)
        await fetch_all_cheques(driver, Settings.BASE_URL, ParseMethod.FILTERED, data)
        return
