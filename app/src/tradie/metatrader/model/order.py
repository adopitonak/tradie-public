from typing import Optional

from tradie.metatrader.model.mt5.order_filling import OrderFilling
from tradie.metatrader.model.mt5.order_time import OrderTime
from tradie.metatrader.model.mt5.order_type import OrderType
from tradie.metatrader.model.mt5.symbol_info import SymbolInfo
from tradie.metatrader.model.mt5.trade_action import TradeAction
from tradie.metatrader.model.normalized_order import NormalizedOrder


class Order(NormalizedOrder):
    action: TradeAction
    type: Optional[OrderType] = None
    type_filling: Optional[OrderFilling] = None
    type_time: Optional[OrderTime] = None
    symbol_info: SymbolInfo  # won't be exported in dict
