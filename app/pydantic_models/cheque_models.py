from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class ORMModel(BaseModel):
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        populate_by_name = True


class ChequeFilterSchema(ORMModel):
    date_from: datetime = Field(...)
    date_to: datetime = Field(...)
    device_id: Optional[str] = Field(None)


class ItemSchema(ORMModel):
    id: str = Field(..., alias="item_id")
    cheque_id: str
    name: str
    quantity: int

    price_per_unit: Decimal
    total: Decimal

    created_at: datetime


class ChequeSchema(ORMModel):
    id: str = Field(..., alias="cheque_id")
    name: str
    date: datetime
    kkt_number: str
    total_price: Decimal
    created_at: datetime

    items: List[ItemSchema]


class ChequeListResponseSchema(ORMModel):
    total: int
    cheques: List[ChequeSchema]
