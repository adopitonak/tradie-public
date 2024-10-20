from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class NormalizedOrder(BaseModel):
    action: int
    type: Optional[int] = None
    type_filling: Optional[int] = None
    type_time: Optional[int] = None
    symbol: Optional[str] = None
    volume: Optional[float] = None
    tp: Optional[float] = None
    sl: Optional[float] = None
    stoplimit: Optional[float] = None
    price: Optional[float] = None
    order: Optional[int] = None
    position: Optional[int] = None
    position_by: Optional[int] = None
    expiration_time: Optional[datetime] = None
    deviation: Optional[float] = None
    comment: Optional[str] = None
    magic: Optional[int] = None
