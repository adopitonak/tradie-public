from tradie.metatrader.model.mt5.order_type import OrderType
from tradie.metatrader.model.requests.risk_open_request import RiskOpenRequest
from tradie.utils.env import EnvVars, read_env_var
from tradie.utils.error import MT5OrderRequestParserError
from tradie.utils.log import get_logger


logger = get_logger(__name__)


class SignalParser:
    @staticmethod
    def parse_signal_to_ror(signal: str) -> RiskOpenRequest:
        # converts message to list of strings for parsing
        split_signal = [line.rstrip() for line in signal.splitlines()]

        parsed_order_type, parsed_symbol = split_signal[0].rsplit(" ", 1)
        parsed_order_type = parsed_order_type.strip().upper().replace(" ", "_")
        symbol = parsed_symbol

        # Parse order type
        order_type = None
        for ot in OrderType:
            if ot.name == parsed_order_type:
                order_type = ot

        if order_type is None:
            all_types = ", ".join([ot.name for ot in OrderType])
            raise MT5OrderRequestParserError(
                f"{parsed_order_type} is not a valid order type. Valid types: {all_types}"
            )

        # Parse entry price
        parsed_entry_price = split_signal[1].lower()
        has_entry_price = parsed_entry_price.startswith("e")
        sl_index = 2 if has_entry_price else 1  # sl_index within the list

        # Ignore entry price and execute it as market order
        if order_type == OrderType.BUY or order_type == OrderType.SELL:
            entry_price = None
            logger.info("Ignoring entry price and executing as market order.")
        else:
            if not has_entry_price:
                raise MT5OrderRequestParserError(
                    f"Missing entry price for non market execution type."
                )
            entry_price = float((parsed_entry_price.split())[-1])

        stop_loss = float((split_signal[sl_index].split())[-1])

        if len(split_signal) >= sl_index + 2:
            take_profit = float((split_signal[sl_index + 1].split())[-1])
        else:
            take_profit = None

        if len(split_signal) == sl_index + 3:
            risk_multiplier = float((split_signal[sl_index + 2].split())[-1])
        else:
            risk_multiplier = 1

        # FIXME: other TPs are not supported yet
        # checks if there's a fourth line and parses it for TP2
        # if (len(split_signal) > 4):
        #     take_profit.append(float(split_signal[4].split()[-1]))

        return RiskOpenRequest(
            type=order_type,
            symbol=symbol,
            risk_multiplier=risk_multiplier,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )
