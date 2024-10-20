from typing import Optional
from tradie.metatrader.brokers.open_request_broker import OpenRequestBroker
from tradie.metatrader.model.mt5.order_filling import OrderFilling
from tradie.metatrader.model.mt5.order_time import OrderTime
from tradie.metatrader.model.mt5.order_type import OrderType
from tradie.metatrader.model.mt5.symbol_info import SymbolInfo
from tradie.metatrader.model.mt5.trade_action import TradeAction
from tradie.metatrader.model.order import Order
from tradie.metatrader.model.requests.processed_risk_open_request import (
    ProcessedRiskOpenRequest,
)
from tradie.utils.log import get_logger
import MetaTrader5 as mt5

logger = get_logger(__name__)


class OrderCreator:
    @staticmethod
    def open_position_with_orb(
        orb: OpenRequestBroker,
        order_filling: OrderFilling = OrderFilling.RETURN,
        order_time: OrderTime = OrderTime.GTC,
        deviation: Optional[float] = None,
        magic: Optional[int] = None,
        ocm: Optional[str] = None,
    ):
        req: ProcessedRiskOpenRequest = orb.request
        return OrderCreator.open_position(
            orb.symbol_info,
            req.type,
            orb.get_position_size_lots(),
            req.entry_price,
            req.take_profit,
            req.stop_loss,
            order_filling,
            order_time,
            deviation,
            magic,
            ocm,
        )

    @staticmethod
    def open_position(
        symbol_info: SymbolInfo,
        order_type: OrderType,
        volume_lots: float,
        entry_price: Optional[float] = None,
        tp_price: Optional[float] = None,
        sl_price: Optional[float] = 0.0,
        order_filling: OrderFilling = None,
        order_time: OrderTime = OrderTime.GTC,
        deviation: Optional[float] = None,
        magic: Optional[int] = None,
        ocm: Optional[str] = None,
    ):
        """Open position. Note that error handling is mostly solved on the mt5 side.

        Args:
            order_type (OrderType): _description_
            size (float): _description_
            entry_price (Optional[float], optional): _description_. Defaults to None.
            tp_price (Optional[float], optional): _description_. Defaults to None.
            sl_price (Optional[float], optional): _description_. Defaults to 0.0.
            magic (int, optional): _description_. Defaults to 5240.
            ocm (str, optional): _description_. Defaults to "".

        Returns:
            _type_: _description_
        """
        order = order_type.mt5()
        price: Optional[float] = None
        sl = sl_price
        tp = tp_price
        order_filling_tmp = (
            order_filling if order_filling is not None else OrderFilling.RETURN
        )
        if order_type == OrderType.BUY:
            action = TradeAction.DEAL
            order_filling_tmp = (
                order_filling_tmp if order_filling_tmp is not None else OrderFilling.FOK
            )

        if order_type == OrderType.SELL:
            action = TradeAction.DEAL
            order_filling_tmp = (
                order_filling_tmp if order_filling_tmp is not None else OrderFilling.FOK
            )

        if order_type == OrderType.BUY_LIMIT:
            action = TradeAction.PENDING
            price = entry_price

        if order_type == OrderType.BUY_STOP:
            action = TradeAction.PENDING
            price = entry_price

        if order_type == OrderType.SELL_LIMIT:
            action = TradeAction.PENDING
            price = entry_price

        if order_type == OrderType.BUY_LIMIT:
            action = TradeAction.PENDING
            price = entry_price

        order = Order(
            action=action,
            type=order_type,
            symbol=symbol_info.name,
            symbol_info=symbol_info,
            volume=volume_lots,
            tp=tp,
            sl=sl,
            type_filling=order_filling,
            type_time=order_time,
            price=price,
            deviation=deviation,
        )

        return order
