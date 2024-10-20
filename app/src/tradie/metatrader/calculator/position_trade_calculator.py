from functools import cache
from tradie.metatrader.calculator.symbol_trade_calculator import SymbolTradeCalculator
from tradie.metatrader.model.mt5.account_info import AccountInfo
from tradie.metatrader.model.mt5.symbol_info import SymbolInfo
from tradie.utils.log import get_logger

logger = get_logger(__name__)


class PositionTradeCalculator(SymbolTradeCalculator):
    def __init__(
        self,
        symbol_info: SymbolInfo,
        account_info: AccountInfo,
        position_size_lots: float,
    ):
        super().__init__(symbol_info)
        self.account_info: AccountInfo = account_info
        self.position_size_lots = position_size_lots

    @cache
    def get_position_size_native(self, entry_price: float) -> float:
        # TODO: Missing for indicies, check: https://www.metatrader5.com/en/terminal/help/trading_advanced/margin_forex
        print
        return (
            self.position_size_lots * self.symbol_info.trade_contract_size * entry_price
        )

    @cache
    def get_est_margin_initial(self, entry_price: float) -> float:
        return (
            self.get_position_size_native(entry_price)
            / self.account_info.leverage
        )

    @cache
    def get_margin_initial(self, entry_price: float) -> float:
        return (
            self.symbol_info.margin_initial
            * entry_price
            * self.position_size_lots
            / self.account_info.leverage
        )

    @cache
    def get_margin_maintenance(self, entry_price: float) -> float:
        return (
            self.symbol_info.margin_maintenance
            * entry_price
            * self.position_size_lots
            / self.account_info.leverage
        )
