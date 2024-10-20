from tradie.metatrader.model.requests.open_request import OpenRequest


class ProcessedOpenRequest(OpenRequest):
    entry_price: float
