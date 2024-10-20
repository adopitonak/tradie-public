from functools import cache
from typing import Optional

from tradie.metatrader.calculator.symbol_trade_calculator import SymbolTradeCalculator
from tradie.metatrader.model.mt5.account_info import AccountInfo
from tradie.metatrader.model.mt5.symbol_info import SymbolInfo
from tradie.utils.error import MT5BadConfiguration
from tradie.utils.log import get_logger

logger = get_logger(__name__)


class RiskTradeCalculator(SymbolTradeCalculator):
    def __init__(
        self,
        symbol_info: SymbolInfo,
        account_info: AccountInfo,
        risk_multiplier: float,
        risk_factor: Optional[float] = None,
        risk_amount: Optional[float] = None,
        prefer_risk_amount=True,
    ):
        super().__init__(symbol_info)
        self.account_info: AccountInfo = account_info

        risk_amount_from_factor = (
            self.account_info.balance * risk_factor if risk_factor is not None else None
        )
        any_risk_amount = risk_amount or risk_amount_from_factor
        if any_risk_amount is None:
            raise MT5BadConfiguration(
                "Either risk amount or risk factor must be specified."
            )
        if risk_amount_from_factor is not None and risk_amount is not None:
            prefered_risk_amount = (
                risk_amount if prefer_risk_amount else risk_amount_from_factor
            )

        self.risk_amount = (
            prefered_risk_amount if prefered_risk_amount else any_risk_amount
        )
        self.risk_multiplier = risk_multiplier

    @cache
    def get_position_size_lots(self, stop_loss: float, entry_price: float) -> float:
        # The smallest possible price change (EURUSD: 1e-5)
        tick_size = self.symbol_info.trade_tick_size

        # How much would you loose if you hold 1 lot and the price moves one tick against you in native currency (EURUSD: 1.0 -> if price moves by one tick you will loose 1$, AUDCAD: depends on current price of AUDUSD)
        tick_value_loss = self.symbol_info.trade_tick_value_loss

        # Calculation - the prices need to be rounded, to match the order execution
        r_entry_price = self.round_to_price_precision(entry_price)
        r_stop_loss = self.round_to_price_precision(stop_loss)

        if tick_size == 0:
            raise

        # determine how many ticks are between entry price and stop loss
        entry_sl_diff = self.round_to_price_precision(abs(r_entry_price - r_stop_loss))
        distance_sl_ticks = round(entry_sl_diff / tick_size)

        # expected loss per lot in native currency
        expected_loss_per_lot = distance_sl_ticks * tick_value_loss

        # expected_loss_native = expected_loss_per_lot * size_in_lots;
        size_in_lots = (self.risk_amount / expected_loss_per_lot) * self.risk_multiplier

        logger.debug(
            {
                "entry_price": r_entry_price,
                "stop_loss": r_stop_loss,
                "type": "Calculate from native position size -> lot size",
                "tick_value_loss": tick_value_loss,
                "entry_sl_diff": entry_sl_diff,
                "distance_sl_ticks": distance_sl_ticks,
                "expected_loss_per_lot": expected_loss_per_lot,
                "expected_loss_native": self.risk_amount,
                "size_in_lots": size_in_lots,
            }
        )

        rounded_psl = self.round_to_minimal_volume(size_in_lots)
        logger.debug(
            {
                "risk_amount_native": self.risk_amount,
                "position_size_lots": size_in_lots,
                "rounded_position_size_lots": rounded_psl,
            }
        )
        return rounded_psl
