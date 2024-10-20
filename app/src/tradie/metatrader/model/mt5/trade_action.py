from enum import Enum
import MetaTrader5 as mt5


class TradeAction(Enum):
    DEAL = 1
    PENDING = 2
    SLTP = 3
    MODIFY = 4
    REMOVE = 5
    CLOSE_BY = 6

    def mt5(self):
        return {
            # Place an order for an instant deal with the specified parameters (set a market order)
            TradeAction.DEAL: mt5.TRADE_ACTION_DEAL,
            # Place an order for performing a deal at specified conditions (pending order)
            TradeAction.PENDING: mt5.TRADE_ACTION_PENDING,
            # Change open position Stop Loss and Take Profit
            TradeAction.SLTP: mt5.TRADE_ACTION_SLTP,
            # Change parameters of the previously placed trading order
            TradeAction.MODIFY: mt5.TRADE_ACTION_MODIFY,
            # Remove previously placed pending order
            TradeAction.REMOVE: mt5.TRADE_ACTION_REMOVE,
            # Close a position by an opposite one
            TradeAction.CLOSE_BY: mt5.TRADE_ACTION_CLOSE_BY,
        }[self]
