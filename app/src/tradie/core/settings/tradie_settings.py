from typing import Optional
from pydantic import BaseModel


class TradieSettings(BaseModel):
    risk_factor: Optional[float]
    risk_amount: Optional[float]
    max_tweak: Optional[float] = 0
    profit_compromise_threshold: Optional[float] = 0
    profit_comporomise_always_attempt: Optional[bool] = False
