from tradie.core.settings.tradie_settings import TradieSettings
from tradie.metatrader.brokers.open_request_broker import OpenRequestBroker
from tradie.metatrader.calculator.position_trade_calculator import (
    PositionTradeCalculator,
)
from tradie.metatrader.calculator.risk_trade_calculator import RiskTradeCalculator
from tradie.metatrader.model.mt5.account_info import AccountInfo
from tradie.metatrader.model.mt5.symbol_info import SymbolInfo
from tradie.metatrader.model.requests.processed_risk_open_request import (
    ProcessedRiskOpenRequest,
)
from tradie.utils.log import get_logger

logger = get_logger(__name__)


class RiskOpenRequestBroker(OpenRequestBroker):
    def __init__(
        self,
        request: ProcessedRiskOpenRequest,
        symbol_info: SymbolInfo,
        account_info: AccountInfo,
        tradie_settings: TradieSettings
    ):
        self._rtc = RiskTradeCalculator(
            symbol_info,
            account_info,
            risk_multiplier=request.risk_multiplier,
            risk_amount=tradie_settings.risk_amount,
            risk_factor=tradie_settings.risk_factor,
        )
        self._ptc = PositionTradeCalculator(
            symbol_info,
            account_info,
            self._rtc.get_position_size_lots(request.stop_loss, request.entry_price),
        )
        self._request = request
        self._symbol_info = symbol_info

    @property
    def request(self):
        return self._request

    @property
    def symbol_info(self):
        return self._symbol_info

    def get_est_margin_initial(self):
        return self._ptc.get_est_margin_initial(self._request.entry_price)

    def get_margin_initial(self):
        return self._ptc.get_margin_initial(self._request.entry_price)

    def get_margin_maintenance(self):
        return self._ptc.get_margin_maintenance(self._request.entry_price)

    def get_risk_amount(self) -> float:
        return self._rtc.risk_amount * self.request.risk_multiplier

    def get_position_size_lots(self) -> float:
        return self._ptc.position_size_lots

    def get_position_size(self) -> float:
        return self._ptc.get_position_size_native(self._request.entry_price)
