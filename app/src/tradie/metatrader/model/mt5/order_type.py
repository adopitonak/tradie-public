from enum import IntEnum
import MetaTrader5 as mt5


# odd types are buy types, even types are sell types.
class OrderType(IntEnum):
    BUY = 1
    SELL = 2
    BUY_LIMIT = 3
    SELL_LIMIT = 4
    BUY_STOP = 5
    SELL_STOP = 6
    BUY_STOP_LIMIT = 7
    SELL_STOP_LIMIT = 8
    CLOSE_BY = 9

    def mt5(self):
        return {
            # Market Buy order
            OrderType.BUY: mt5.ORDER_TYPE_BUY,
            # Market Sell order
            OrderType.SELL: mt5.ORDER_TYPE_SELL,
            # Buy Limit pending order
            OrderType.BUY_LIMIT: mt5.ORDER_TYPE_BUY_LIMIT,
            # Sell Limit pending order
            OrderType.SELL_LIMIT: mt5.ORDER_TYPE_SELL_LIMIT,
            # Buy Stop pending order
            OrderType.BUY_STOP: mt5.ORDER_TYPE_BUY_STOP,
            # Sell Stop pending order
            OrderType.SELL_STOP: mt5.ORDER_TYPE_SELL_STOP,
            # Upon reaching the order price, a pending Buy Limit order is placed at the StopLimit price
            OrderType.BUY_STOP_LIMIT: mt5.ORDER_TYPE_BUY_STOP_LIMIT,
            # Upon reaching the order price, a pending Sell Limit order is placed at the StopLimit price
            OrderType.SELL_STOP_LIMIT: mt5.ORDER_TYPE_SELL_STOP_LIMIT,
            # Order to close a position by an opposite one
            OrderType.CLOSE_BY: mt5.ORDER_TYPE_CLOSE_BY,
        }[self]
