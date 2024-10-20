import MetaTrader5 as mt5

from tradie.core.settings.tradie_settings import TradieSettings
from tradie.metatrader.brokers.open_request_broker import OpenRequestBroker
from tradie.metatrader.model.mt5.position_info import PositionInfo
from tradie.metatrader.model.order import Order
from tradie.metatrader.order_creator import OrderCreator
from tradie.metatrader.order_handler import OrderHandler
from tradie.metatrader.signal_processor import SignalProcessor
from tradie.metatrader.utils.mt5_utils import get_mt5_error_message
from tradie.utils.env import EnvVars, read_env_bool, read_env_var
from tradie.utils.error import MT5BadConfiguration
from tradie.utils.log import get_logger
from typing import Any


logger = get_logger(__name__)

FLOAT_OUTPUT_FORMAT = "{:,.2f}"


class MT5Client:
    def __init__(self):
        self._server: str = read_env_var(EnvVars.MT5_SERVER)
        self._username: int = read_env_var(EnvVars.MT5_USERNAME)
        self._password: str = read_env_var(EnvVars.MT5_PASSWORD)
        try:
            logger.debug(f"🪷 Connecting to mt5 server. {self._server} 🪷")
            connected = mt5.initialize(
                server=self._server, login=int(self._username), password=self._password
            )
            if not connected:
                raise Exception()
            else:
                logger.debug(f"💮 User: {self._username}! 💮")
        except Exception as e:
            raise MT5BadConfiguration(
                get_mt5_error_message(
                    "🥀🥀🥀 Couldn't login to mt5. Please check if you provided correct credentials in env vars. 🥀🥀🥀"
                )
            ) from e
        self._tradie_settings = TradieSettings(
            risk_amount=read_env_var(EnvVars.TRADIE_RISK_AMOUNT),
            risk_factor=read_env_var(EnvVars.TRADIE_RISK_FACTOR),
            max_tweak=read_env_var(EnvVars.TWEAK_TOWARDS_AGGRESSIVE_TRADE),
            profit_compromise_threshold=read_env_var(EnvVars.PROFIT_COMPROMISE_THRESHOLD),
            profit_comporomise_always_attempt=read_env_bool(EnvVars.PROFIT_COMPROMISE_ALWAYS_ATTEMPT)
        )
        logger.info(f"Tradie settings\n🌸🌺💐 {self._tradie_settings} 💐🌺🌸")
        max_tweak = read_env_var(EnvVars.TWEAK_TOWARDS_AGGRESSIVE_TRADE)
        self._max_tweak: int = int(max_tweak) if max_tweak else 0

    def __exit__(self):
        logger.debug("🎴 Disconnecting from mt5 server 🎴")
        mt5.shutdown()

    def check_order(self, order: Order):
        oh = OrderHandler(order)
        check_order_dict = oh.check_order()._asdict()
        check_order_dict.pop("request")
        return check_order_dict
    
    def amend_order(self, order: Order):
        oh = OrderHandler(order)
        return oh.check_and_amend_order()

    def peak_order(self, order: Order):
        oh = OrderHandler(order)
        return oh.get_request_dict()

    def place_order(self, order: Order):
        oh = OrderHandler(order)
        oh.place_order()

    def calculate_position_size_from_risk(self, signal: str, with_position_info=False):
        rorb = SignalProcessor.process_risk_open_request_signal(signal, self._tradie_settings)
        position_size = rorb.get_position_size_lots()
        return self._resolve_return_with_position_info(
            position_size, rorb, with_position_info
        )

    def create_open_order_from_risk(
        self, signal: str, with_position_info=False
    ) -> Order | tuple[Order, PositionInfo]:
        rorb = SignalProcessor.process_risk_open_request_signal(signal, self._tradie_settings)
        oc = OrderCreator()
        return self._resolve_return_with_position_info(
            oc.open_position_with_orb(rorb), rorb, with_position_info
        )

    def _get_position_info(self, orb: OpenRequestBroker) -> PositionInfo:
        risk_amount = FLOAT_OUTPUT_FORMAT.format(orb.get_risk_amount())
        position_size = FLOAT_OUTPUT_FORMAT.format(orb.get_position_size())
        est_initial_margin = FLOAT_OUTPUT_FORMAT.format(orb.get_est_margin_initial())
        initial_margin = FLOAT_OUTPUT_FORMAT.format(orb.get_margin_initial())
        maintenance_margin = FLOAT_OUTPUT_FORMAT.format(orb.get_margin_maintenance())
        return PositionInfo(
            risk_amount=risk_amount,
            position_size=position_size,
            est_initial_margin=est_initial_margin,
            initial_margin=initial_margin,
            maintenance_margin=maintenance_margin,
        )

    def _resolve_return_with_position_info(
        self, value: Any, orb: OpenRequestBroker, with_position_info: bool
    ) -> Any | tuple[Any, PositionInfo]:
        if not with_position_info:
            return value
        else:
            return value, self._get_position_info(orb)


'''
    def send_order(self, symbol, lot, buy, sell, id_position=None, pct_tp=0.02, pct_sl=0.01, comment=" No specific comment", magic=0):
        # Extract filling_mode
        filling_type = MT5Client.find_filling_mode(symbol)

        """ OPEN A TRADE """
        if buy and id_position == None:
            tp, sl = MT5Client.risk_reward_threshold(
                symbol, buy=True, risk=pct_sl, reward=pct_tp)

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot,
                "type": mt5.ORDER_TYPE_BUY,
                "price": mt5.symbol_info_tick(symbol).ask,
                "deviation": 10,
                "tp": tp,
                "sl": sl,
                "magic": magic,
                "comment": comment,
                "type_filling": filling_type,
                "type_time": mt5.ORDER_TIME_GTC}

            result = mt5.order_send(request)
            return result

        if sell and id_position == None:
            tp, sl = MT5Client.risk_reward_threshold(
                symbol, buy=False, risk=pct_sl, reward=pct_tp)
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot,
                "type": mt5.ORDER_TYPE_SELL,
                "price": mt5.symbol_info_tick(symbol).bid,
                "deviation": 10,
                "tp": tp,
                "sl": sl,
                "magic": magic,
                "comment": comment,
                "type_filling": filling_type,
                "type_time": mt5.ORDER_TIME_GTC}

            result = mt5.order_send(request)
            return result

        """ CLOSE A TRADE """
        if buy and id_position != None:
            request = {
                "position": id_position,
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot,
                "type": mt5.ORDER_TYPE_SELL,
                "price": mt5.symbol_info_tick(symbol).bid,
                "deviation": 10,
                "magic": magic,
                "comment": comment,
                "type_filling": filling_type,
                "type_time": mt5.ORDER_TIME_GTC}

            result = mt5.order_send(request)
            return result

        if sell and id_position != None:
            request = {
                "position": id_position,
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot,
                "type": mt5.ORDER_TYPE_BUY,
                "price": mt5.symbol_info_tick(symbol).ask,
                "deviation": 10,
                "magic": magic,
                "comment": comment,
                "type_filling": filling_type,
                "type_time": mt5.ORDER_TIME_GTC}

            result = mt5.order_send(request)
            return result

    @staticmethod
    def resume():
        """ Return the current positions. Position=0 --> Buy """

        # Define the name of the columns that we will create
        colonnes = ["ticket", "position", "symbol", "volume",
                    "magic", "profit", "price", "tp", "sl", "trade_size"]

        # Go take the current open trades
        liste = mt5.positions_get()

        # Create a empty dataframe
        summary = pd.DataFrame()

        # Loop to add each row in dataframe
        for element in liste:
            element_pandas = pd.DataFrame([element.ticket, element.type, element.symbol, element.volume, element.magic,
                                           element.profit, element.price_open, element.tp,
                                           element.sl, mt5.symbol_info(element.symbol).trade_contract_size],
                                          index=colonnes).transpose()
            summary = pd.concat((summary, element_pandas), axis=0)

        try:
            summary["profit %"] = summary.profit / \
                (summary.price * summary.trade_size * summary.volume)
            summary = summary.reset_index(drop=True)
        except:
            pass
        return summary

    @staticmethod
    def trailing_stop_loss():

        # Extract the current open positions
        MT5Client.summary = MT5Client.resume()

        # Verification: Is there any open position?
        if MT5Client.summary.shape[0] > 0:
            for i in range(MT5Client.summary.shape[0]):

                # Extract information
                row = MT5Client.summary.iloc[i]
                symbol = row["symbol"]

                """ CASE 1: Change dynamicly the stop loss for a BUY ORDER """
                # Trailing stop loss for a buy order
                if row["position"] == 0:

                    if symbol not in MT5Client.max_price.keys():
                        MT5Client.max_price[symbol] = row["price"]

                    # Extract current price
                    current_price = (mt5.symbol_info(
                        symbol).ask + mt5.symbol_info(symbol).bid) / 2

                    # Compute distance between current price an max price
                    from_sl_to_curent_price = current_price - row["sl"]
                    from_sl_to_max_price = MT5Client.max_price[symbol] - row["sl"]

                    # If current price is greater than preivous max price --> new max price
                    if current_price > MT5Client.max_price[symbol]:
                        MT5Client.max_price[symbol] = current_price

                    # Find the difference between the current minus max
                    if from_sl_to_curent_price > from_sl_to_max_price:
                        difference = from_sl_to_curent_price - from_sl_to_max_price

                        # Set filling mode
                        filling_type = mt5.symbol_info(symbol).filling_mode

                        # Set the point
                        point = mt5.symbol_info(symbol).point

                        # Change the sl
                        request = {
                            "action": mt5.TRADE_ACTION_SLTP,
                            "symbol": symbol,
                            "position": row["ticket"],
                            "volume": row["volume"],
                            "type": mt5.ORDER_TYPE_BUY,
                            "price": row["price"],
                            "sl": row["sl"] + difference,
                            "type_filling": filling_type,
                            "type_time": mt5.ORDER_TIME_GTC,
                        }

                        information = mt5.order_send(request)
                        print(information)

                """ CASE 2: Change dynamicly the stop loss for a SELL ORDER """
                # Trailing stop loss for a sell order
                if row["position"] == 1:

                    if symbol not in MT5Client.min_price.keys():
                        MT5Client.min_price[symbol] = row["price"]

                    # Extract current price
                    current_price = (mt5.symbol_info(
                        symbol).ask + mt5.symbol_info(symbol).bid) / 2

                    # Compute distance between current price an max price
                    from_sl_to_curent_price = row["sl"] - current_price
                    from_sl_to_min_price = row["sl"] - \
                        MT5Client.min_price[symbol]

                    # If current price is greater than preivous max price --> new max price
                    if current_price < MT5Client.min_price[symbol]:
                        MT5Client.min_price[symbol] = current_price

                    # Find the difference between the current minus max
                    if from_sl_to_curent_price > from_sl_to_min_price:
                        difference = from_sl_to_curent_price - from_sl_to_min_price

                        # Set filling mode
                        filling_type = mt5.symbol_info(symbol).filling_mode

                        # Set the point
                        point = mt5.symbol_info(symbol).point

                        # Change the sl
                        request = {
                            "action": mt5.TRADE_ACTION_SLTP,
                            "symbol": symbol,
                            "position": row["ticket"],
                            "volume": row["volume"],
                            "type": mt5.ORDER_TYPE_SELL,
                            "price": row["price"],
                            "sl": row["sl"] - difference,
                            "type_filling": filling_type,
                            "type_time": mt5.ORDER_TIME_GTC,
                        }

                        information = mt5.order_send(request)
                        print(information)

    @staticmethod
    def verif_tsl():

        # print("MAX", MT5.max_price)

        # print("MIN", MT5.min_price)

        if len(MT5Client.summary) > 0:
            buy_open_positions = MT5Client.summary.loc[MT5Client.summary["position"]
                                                       == 0]["symbol"]
            sell_open_positions = MT5Client.summary.loc[MT5Client.summary["position"]
                                                        == 0]["symbol"]
        else:
            buy_open_positions = []
            sell_open_positions = []

        """ IF YOU CLOSE ONE OF YOUR POSITION YOU NEED TO DELETE THE PRICE IN THE MAX AND MIN PRICES DICTIONNARIES"""
        if len(MT5Client.max_price) != len(buy_open_positions) and len(buy_open_positions) > 0:
            symbol_to_delete = []

            for symbol in MT5Client.max_price.keys():

                if symbol not in list(buy_open_positions):
                    symbol_to_delete.append(symbol)

            for symbol in symbol_to_delete:
                del MT5Client.max_price[symbol]

        if len(MT5Client.min_price) != len(sell_open_positions) and len(sell_open_positions) > 0:
            symbol_to_delete = []

            for symbol in MT5Client.min_price.keys():

                if symbol not in list(sell_open_positions):
                    symbol_to_delete.append(symbol)

            for symbol in symbol_to_delete:
                del MT5Client.min_price[symbol]

        if len(buy_open_positions) == 0:
            MT5Client.max_price = {}

        if len(sell_open_positions) == 0:
            MT5Client.min_price = {}
'''
