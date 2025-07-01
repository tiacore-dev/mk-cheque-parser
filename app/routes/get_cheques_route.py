from fastapi import APIRouter, Depends
from tortoise.expressions import Q

from app.database.models import Cheque
from app.handlers.auth_handler import check_api_key
from app.pydantic_models.cheque_models import (
    ChequeFilterSchema,
    ChequeListResponseSchema,
    ChequeSchema,
)

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
