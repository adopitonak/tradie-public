from enum import Enum
import MetaTrader5 as mt5


class OrderTime(Enum):
    GTC = 1
    DAY = 2
    SPECIFIED = 3
    SPECIFIED_DAY = 4

    def mt5(self):
        return {
            # The order stays in the queue until it is manually canceled
            OrderTime.GTC: mt5.ORDER_TIME_GTC,
            # The order is active only during the current trading day
            OrderTime.DAY: mt5.ORDER_TIME_DAY,
            # The order is active until the specified date
            OrderTime.SPECIFIED: mt5.ORDER_TIME_SPECIFIED,
            # The order is active until 23:59:59 of the specified day. If this time appears to be out of a trading session, the expiration is processed at the nearest trading time.
            OrderTime.SPECIFIED_DAY: mt5.ORDER_TIME_SPECIFIED_DAY,
        }[self]
