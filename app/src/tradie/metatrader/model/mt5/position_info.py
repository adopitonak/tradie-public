from pydantic import BaseModel


class PositionInfo(BaseModel):
    risk_amount: str
    position_size: str
    est_initial_margin: str
    initial_margin: str
    maintenance_margin: str
