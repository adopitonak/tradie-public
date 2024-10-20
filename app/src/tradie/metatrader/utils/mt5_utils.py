import functools
import MetaTrader5 as mt5

from time import sleep

from tradie.metatrader.model.mt5.account_info import AccountInfo
from tradie.metatrader.model.mt5.symbol_info import SymbolInfo
from tradie.utils.common import object_to_dict
from tradie.utils.error import MT5Error
from tradie.utils.log import get_logger

logger = get_logger(__name__)


def get_mt5_error_message(prefix: str = "") -> str:
    if prefix != "":
        if not prefix.endswith(" "):
            if not prefix.endswith("."):
                prefix += "."
            prefix += " "

    return f"{prefix}Failed with code {mt5.last_error()}, see https://www.mql5.com/en/docs/python_metatrader5/mt5lasterror_py"


def raise_mt5_error(msg):
    def intermid_wrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            value = func(*args, **kwargs)
            if value is None:
                raise MT5Error(get_mt5_error_message())
            return value

        return wrapper

    return intermid_wrapper


class MT5Utils:
    @staticmethod
    @raise_mt5_error("Couldn't retrieve account info")
    def mt_account_info_get() -> AccountInfo:
        return mt5.account_info()

    @staticmethod
    @raise_mt5_error("Couldn't get symbols")
    def mt_symbols_get():
        return mt5.symbols_get()

    @staticmethod
    def get_symbols():
        res = MT5Utils.mt_symbols_get()
        return [symbol.name for symbol in res]

    @staticmethod
    @raise_mt5_error("Couldn't get info")
    def mt_symbol_info(symbol: str) -> any:
        avail_symbols = MT5Utils.get_symbols()
        if symbol not in avail_symbols:
            raise MT5Error(
                f"Symbol not '{symbol}' found among symbols. Possible options: {str(avail_symbols)}"
            )
        symbol_info = mt5.symbol_info(symbol)
        
        if not symbol_info.visible:
            logger.info(f"Symbol {symbol} is not visible, trying to switch on")
            if not mt5.symbol_select(symbol, True):
                raise MT5Error(f"Failed to add symbol {symbol} to market watch.")
            else:
                # Retry data, because if the symbol is not selected, you won't receive anything
                sleep(2)    # wait until the symbol is added to market watch
                # Maybe this can be replaced by 
                symbol_info = mt5.symbol_info(symbol)
                
        return symbol_info

    @staticmethod
    def get_symbol_info(symbol: str) -> SymbolInfo:
        mt_symbol_info = MT5Utils.mt_symbol_info(symbol)
        symbol_info = SymbolInfo(**object_to_dict(mt_symbol_info))
        return symbol_info
