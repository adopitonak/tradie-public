from enum import Enum
import MetaTrader5 as mt5


class TradeDirection(Enum):
    BUY = 1
    SELL = 2

    def mt5(self):
        return {
            TradeDirection.BUY: mt5.ORDER_TYPE_BUY,
            TradeDirection.SELL: mt5.ORDER_TYPE_SELL,
        }[self]
