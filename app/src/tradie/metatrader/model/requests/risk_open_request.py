from tradie.metatrader.model.requests.open_request import OpenRequest


class RiskOpenRequest(OpenRequest):
    risk_multiplier: float
    stop_loss: float
