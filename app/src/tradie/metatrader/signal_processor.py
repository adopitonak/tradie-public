from copy import deepcopy
from random import randint
from typing import TypeVar
from tradie.core.settings.tradie_settings import TradieSettings
from tradie.metatrader.brokers.risk_open_request_broker import RiskOpenRequestBroker
from tradie.metatrader.calculator.symbol_trade_calculator import SymbolTradeCalculator
from tradie.metatrader.model.mt5.order_type import OrderType
from tradie.metatrader.model.mt5.symbol_info import SymbolInfo
from tradie.metatrader.model.mt5.trade_direction import TradeDirection
from tradie.metatrader.model.requests.open_request import OpenRequest
from tradie.metatrader.model.requests.processed_open_request import ProcessedOpenRequest
from tradie.metatrader.model.requests.processed_risk_open_request import (
    ProcessedRiskOpenRequest,
)
from tradie.metatrader.signal_parser import SignalParser
from tradie.metatrader.utils.mt5_utils import MT5Utils
from tradie.metatrader.utils.order_utils import OrderUtils
from tradie.utils.error import MT5ParserError
from tradie.utils.log import get_logger

TOpenRequest = TypeVar("TOpenRequest", bound=OpenRequest)
logger = get_logger(__name__)


# TODO: functions under should maybe go to trade features
def _get_signed_rand_int(max_int):
    if max_int > 0:
        return randint(0, max_int)
    else:
        return randint(max_int, 0)
    

def _get_tweak_value(max_tweak, tweak_direction, tick_size):
    return _get_signed_rand_int(max_tweak) * tweak_direction * tick_size


def tweak_order(open_request: TOpenRequest, max_tweak: float, symbol_info: SymbolInfo) -> TOpenRequest:
    if max_tweak == 0:
        return open_request
    
    logger.info(f'Tweaking order with max value: {max_tweak}')

    # sell -> +sl, +tp, -entry (riskier trade, earlier tp, earlier entry) ... buy -> -sl, -tp, +entry, 
    td = 1 if OrderUtils.order_type_to_direction(open_request.type) == TradeDirection.SELL else -1   # tweak direction
    ts = symbol_info.trade_tick_size

    t_sl = open_request.stop_loss + _get_tweak_value(max_tweak, td, ts) if open_request.stop_loss else None
    t_tp = open_request.take_profit + _get_tweak_value(max_tweak, td, ts) if open_request.take_profit else None
    t_entry = open_request.entry_price - _get_tweak_value(max_tweak, td, ts) if open_request.entry_price else None
    
    new_or = deepcopy(open_request)
    new_or.entry_price = t_entry
    new_or.stop_loss = t_sl
    new_or.take_profit = t_tp
    return new_or


def better_execute_with_market(open_request: TOpenRequest, stc: SymbolTradeCalculator, profit_compromise_threshold: float, profit_compromise_always_attempt: bool):
    # FIXME: was not tested and is still not integrated 
    if profit_compromise_threshold == 0:
        return open_request, False
    
    if open_request.type == OrderType.BUY or open_request.type == OrderType.SELL:
        return open_request, False
    
    if open_request.take_profit is None:
        logger.warning("Wanted to use'better execute with market' feature, but take profit was not set.")
        return open_request, False
    
    cmp = SignalProcessor._get_cmp(open_request, stc)
    if open_request.entry_price is None:
        raise AssertionError("Execution type is not market, but entry price is not set.")
    
    cmp_p = stc.round_to_price_precision(cmp)
    entry_p = stc.round_to_price_precision(open_request.entry_price)
    tp_p = stc.round_to_price_precision(open_request.take_profit)

    # only ratio matters (you can ignore sign, scaling, ...)
    limit_pips = tp_p - entry_p
    market_pips = tp_p - cmp_p

    ratio = market_pips / limit_pips
    if ratio < 0:
        raise MT5ParserError('Entry price or market price are on the opposite directions of take profit.')
    elif ratio == 0:
        raise MT5ParserError('Market price is equal to take profit.')
    elif ratio >= 1:
        logger.info('Market price is better or equal to limit price. Executing as market order.')
    else:
        difference = 1 - ratio
        if difference > profit_compromise_threshold:
            if profit_compromise_always_attempt:
                # TODO: calculate new price according to profit_compromise_threshold
                pass
            return open_request, False
        else:
            logger.info(f'Market price is within the defined threshold {difference} <= {profit_compromise_threshold}. Executing as market order.')
    
    new_or = deepcopy(open_request)
    new_or.type = OrderType.SELL if OrderUtils.order_type_to_direction(open_request.type) == TradeDirection.SELL else OrderType.BUY
    new_or.entry_price = cmp_p
    return new_or, True


class SignalProcessor:
    @staticmethod
    def process_risk_open_request_signal(signal: str, tradie_settings: TradieSettings) -> RiskOpenRequestBroker:
        ror = SignalParser.parse_signal_to_ror(signal)
        por, symbol_info = SignalProcessor._process_open_request(ror, tradie_settings.max_tweak, tradie_settings.profit_compromise_threshold, tradie_settings.profit_comporomise_always_attempt)
        pror = ProcessedRiskOpenRequest(
            **por.model_dump(), risk_multiplier=ror.risk_multiplier
        )
        return RiskOpenRequestBroker(pror, symbol_info, MT5Utils.mt_account_info_get(), tradie_settings)

    @staticmethod
    def _process_open_request(
        ror: OpenRequest,
        max_tweak: float,
        profit_compromise_threshold: float,
        profit_compromise_always_attempt: bool
    ) -> tuple[ProcessedOpenRequest, SymbolInfo]:
        symbol_info = MT5Utils.get_symbol_info(ror.symbol)
        stc = SymbolTradeCalculator(symbol_info)
        if ror.entry_price is None:
            ror.entry_price = SignalProcessor._resolve_entry_price(ror, stc)
        # TODO: disable features for now. There were side effects (required market price for limit order, etc.) Put it elsewhere.
        # ror, is_changed = better_execute_with_market(ror, stc, profit_compromise_threshold, profit_compromise_always_attempt)
        # if not is_changed:
        #     ror = tweak_order(ror, max_tweak, symbol_info)
        return ProcessedOpenRequest(**ror.model_dump()), symbol_info

    @staticmethod
    def _resolve_entry_price(req: OpenRequest, stc: SymbolTradeCalculator) -> float:
        if req.entry_price:
            return req.entry_price
        return SignalProcessor._get_cmp(req, stc)
    
    @staticmethod
    def _get_cmp(req: OpenRequest, stc: SymbolTradeCalculator) -> float:
        direction = OrderUtils.order_type_to_direction(req.type)
        return stc.get_cmp(direction)
