from tradie.metatrader.model.requests.processed_open_request import ProcessedOpenRequest
from tradie.metatrader.model.requests.risk_open_request import RiskOpenRequest


class ProcessedRiskOpenRequest(RiskOpenRequest, ProcessedOpenRequest): ...
