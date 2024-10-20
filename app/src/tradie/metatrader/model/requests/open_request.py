from typing import Optional
from pydantic import BaseModel
from abc import ABC

from tradie.metatrader.model.mt5.order_type import OrderType


class OpenRequest(BaseModel, ABC):
    type: OrderType
    symbol: str
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
