from tradie.metatrader.model.mt5.symbol_info import SymbolInfo
from tradie.metatrader.model.mt5.trade_direction import TradeDirection
from tradie.utils.error import MT5Error
from tradie.utils.log import get_logger

logger = get_logger(__name__)


class SymbolTradeCalculator:
    def __init__(self, symbol_info: SymbolInfo):
        self.symbol_info: SymbolInfo = symbol_info

    def round_to_minimal_volume(self, amount: float) -> float:
        minimal_volume = self.symbol_info.volume_min
        if minimal_volume == 0:
            return amount
        rounded_amount = round(amount / minimal_volume) * minimal_volume
        if rounded_amount == 0:
            raise MT5Error(
                f"Volume too small: {amount}. Would be 0 if rounded to: {minimal_volume}"
            )
        return rounded_amount

    def round_to_price_precision(self, price: float):
        """Get number of decimal from symbol info and round price to that number of decimals

        Args:
            price (float): _description_

        Returns:
            _type_: _description_
        """
        return round(price, self.symbol_info.digits)

    def get_cmp(self, direction=TradeDirection) -> float:
        # assume we want to sell -> cmp is the highest available bid from buyer
        cmp = self.symbol_info.bid if direction.SELL else self.symbol_info.ask
        if cmp == 0:
            raise MT5Error(f'Current Market Price is 0. Market for current symbol is probably closed.')
        return cmp
