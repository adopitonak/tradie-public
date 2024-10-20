import copy
from typing import Optional
import MetaTrader5 as mt5

from tradie.metatrader.calculator.symbol_trade_calculator import SymbolTradeCalculator
from tradie.metatrader.model.mt5.order_filling import OrderFilling
from tradie.metatrader.model.normalized_order import NormalizedOrder
from tradie.metatrader.model.order import Order
from tradie.metatrader.utils.order_utils import OrderUtils
from tradie.utils.error import MT5HandlerError
from tradie.utils.log import get_logger

logger = get_logger(__name__)


class OrderHandler:
    def __init__(self, order: Order):
        self.order: Order = order
        self.stc: SymbolTradeCalculator = SymbolTradeCalculator(order.symbol_info)

    @staticmethod
    def ensure_symbol_visibility(order: Order, enable_if_not_visible=True) -> None:
        name = order.symbol_info.name
        if not order.symbol_info.visible:
            logger.debug(name, " is not visible.")
            if enable_if_not_visible:
                logger.info(f"Trying to switch on symbol: {name}.")
                if not mt5.symbol_select(name, True):
                    raise MT5HandlerError(f"Cannot set {name} to visible.")
                logger.info(f"Symbol {name} is now visible.")

    def check_and_amend_order(self) -> Order:
        check_result = self.check_order()
        if self._is_order_check_ok(check_result):
            return self.order
        elif check_result.comment != "Unsupported filling mode":
            raise MT5HandlerError(f"Failed order check: {check_result.comment}")

        o_filling = self._amened_order_filling()
        if o_filling is None:
            raise MT5HandlerError("Couldn't find suitable order filling")
        return o_filling

    def check_order(self):
        request = self.get_request_dict()

        logger.info(f"Checking order {request}")
        check_result = mt5.order_check(request)
        logger.info(f"Check Result: {check_result}")
        return check_result

    def place_order(self):
        return self._place_order_with_request(self.get_request_dict())
    
    def _check_order_bool(self, request) -> bool:
        check_result = mt5.order_check(request)
        return self._is_order_check_ok(check_result)
    
    @staticmethod
    def _is_order_check_ok(order_check_result: str):
        return order_check_result.comment == "Done"

    def _amened_order_filling(self) -> Optional[Order]:
        arg_order_filling_prefs = [
            OrderFilling.RETURN,
            OrderFilling.FOK,
            OrderFilling.IOC,
        ]

        order_filling_prefs = (
            arg_order_filling_prefs.copy()
        )  # lists are mutable do a copy as you don't know where it will come from

        if self.order.type_filling in order_filling_prefs:
            order_filling_prefs.remove(self.order.type_filling)
        
        order_filling_prefs.insert(0, self.order.type_filling)

        logger.debug("Falling back to iteration of trading preferences")
        for i, filling_pref in enumerate(order_filling_prefs):
            if i == 0:
                logger.debug(f"Checking original order filling: {filling_pref}")
            else:
                logger.debug(f"Trying again with fallback order filling: {filling_pref}")
            o = copy.deepcopy(self.order)
            o.type_filling = filling_pref
            logger.debug(f"Trying with {self.convert_order_to_dict(o)}")
            is_ok = self._check_order_bool(self.convert_order_to_dict(o))
            if is_ok:
                return o

        return None

    def _place_order_with_request(self, request: dict):
        logger.info(f"Sending order {request}")
        result = mt5.order_send(request)
        logger.info(f"Recieved {result}")

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            raise MT5HandlerError(f"Order send error: {result.comment}")
        else:
            otk = result.order  # order ticket
            return otk

    def convert_order_to_dict(self, order: Order) -> dict:
        return OrderUtils.to_norm_dict(order, self.stc)

    def get_request_dict(self) -> dict:
        return OrderUtils.to_norm_dict(self.order, self.stc)

    def get_request(self) -> NormalizedOrder:
        # unpack to dict and back to NormalizedOrder, so you can ignore empty keys
        return NormalizedOrder(**OrderUtils.to_norm_dict(self.order, self.stc))
