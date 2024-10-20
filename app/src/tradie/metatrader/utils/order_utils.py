from copy import deepcopy
from tradie.metatrader.calculator.symbol_trade_calculator import SymbolTradeCalculator
from tradie.metatrader.model.mt5.order_type import OrderType
from tradie.metatrader.model.mt5.trade_direction import TradeDirection
from tradie.metatrader.model.normalized_order import NormalizedOrder
from tradie.metatrader.model.order import Order
from tradie.utils.error import MT5Error
from rich import inspect


class OrderUtils:
    @staticmethod
    def order_type_to_direction(order_type: OrderType | int) -> TradeDirection:
        if type(order_type) == int:
            order_type = OrderType(order_type)
        enum_name = order_type.name  # type: ignore
        if "BUY" in enum_name:
            return TradeDirection.BUY
        elif "SELL" in enum_name:
            return TradeDirection.SELL
        else:
            raise MT5Error(
                "OrderType cannot be CLOSE BY if you want to convert it to direction."
            )

    @staticmethod
    def order_to_dict(order: Order) -> dict:
        return {
            "action": order.action.mt5(),
            "magic": order.magic,
            "order": order.order,
            "symbol": order.symbol,
            "volume": str(order.volume),
            "price": str(order.price),
            "stoplimit": str(order.stoplimit),
            "sl": str(order.sl),
            "tp": str(order.tp),
            "deviation": str(order.deviation),
            "type": order.type.mt5() if order.type else None,
            "type_filling": order.type_filling.mt5() if order.type_filling else None,
            "type_time": order.type_time.mt5() if order.type_time else None,
            # 'expiration': ,
            "comment": order.comment,
            "position": str(order.position),
            "position_by": str(order.position_by),
        }

    @staticmethod
    def normalize_order(order: Order, stc: SymbolTradeCalculator) -> NormalizedOrder:
        # FIXME: is this necessary?
        # d = self.get_symbol_info(symbol, 'digits')
        # if d == 3:
        #     sl = float('{0:5.3f}'.format(sl))
        #     tp = float('{0:5.3f}'.format(tp))
        # elif d == 2:
        #     sl = float('{0:4.2f}'.format(sl))
        #     tp = float('{0:4.2f}'.format(tp))
        # else:
        #     sl = float('{0:7.5f}'.format(sl))
        #     tp = float('{0:7.5f}'.format(tp))

        if not order.symbol:
            return order
        else:
            o = deepcopy(order)
            if o.volume is not None:
                o.volume = stc.round_to_minimal_volume(o.volume)
            if o.sl is not None:
                o.sl = stc.round_to_price_precision(o.sl)
            if o.tp is not None:
                o.tp = stc.round_to_price_precision(o.tp)
            if o.stoplimit is not None:
                o.stoplimit = stc.round_to_price_precision(o.stoplimit)
            if o.price is not None:
                o.price = stc.round_to_price_precision(o.price)
            return NormalizedOrder(
                **o.model_dump(
                    exclude={
                        "action",
                        "type",
                        "type_filling",
                        "type_time",
                        "symbol_info",
                    }
                ),
                action=o.action.mt5(),
                type=o.type.mt5() if o.type else None,
                type_filling=o.type_filling.mt5() if o.type_filling else None,
                type_time=o.type_time.mt5() if o.type_time else None,
            )

    @staticmethod
    def to_norm_dict(order: Order, stc: SymbolTradeCalculator) -> dict:
        o = OrderUtils.normalize_order(order, stc)
        return o.model_dump(exclude_none=True)
