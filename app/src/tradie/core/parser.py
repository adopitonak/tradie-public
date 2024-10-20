# allowed FX symbols
from tradie.utils.env import EnvVars, read_env_var


SYMBOLS = [
    "AUDCAD",
    "AUDCHF",
    "AUDJPY",
    "AUDNZD",
    "AUDUSD",
    "CADCHF",
    "CADJPY",
    "CHFJPY",
    "EURAUD",
    "EURCAD",
    "EURCHF",
    "EURGBP",
    "EURJPY",
    "EURNZD",
    "EURUSD",
    "GBPAUD",
    "GBPCAD",
    "GBPCHF",
    "GBPJPY",
    "GBPNZD",
    "GBPUSD",
    "NOW",
    "NZDCAD",
    "NZDCHF",
    "NZDJPY",
    "NZDUSD",
    "USDCAD",
    "USDCHF",
    "USDJPY",
    "XAGUSD",
    "XAUUSD",
]

# RISK FACTOR
RISK_FACTOR = read_env_var(EnvVars.TRADIE_RISK_FACTOR)


def parse_signal(signal: str) -> dict:
    """Starts process of parsing signal and entering trade on MetaTrader account.

    Arguments:
        signal: trading signal

    Returns:
        a dictionary that contains trade signal information
    """

    # converts message to list of strings for parsing
    signal = signal.splitlines()
    signal = [line.rstrip() for line in signal]

    trade = {}

    # determines the order type of the trade
    if "Buy Limit".lower() in signal[0].lower():
        trade["OrderType"] = "Buy Limit"

    elif "Sell Limit".lower() in signal[0].lower():
        trade["OrderType"] = "Sell Limit"

    elif "Buy Stop".lower() in signal[0].lower():
        trade["OrderType"] = "Buy Stop"

    elif "Sell Stop".lower() in signal[0].lower():
        trade["OrderType"] = "Sell Stop"

    elif "Buy".lower() in signal[0].lower():
        trade["OrderType"] = "Buy"

    elif "Sell".lower() in signal[0].lower():
        trade["OrderType"] = "Sell"

    # returns an empty dictionary if an invalid order type was given
    else:
        return {}

    # extracts symbol from trade signal
    trade["Symbol"] = (signal[0].split())[-1]

    # checks if the symbol is valid, if not, returns an empty dictionary
    if trade["Symbol"] not in SYMBOLS:
        return {}

    # checks wheter or not to convert entry to float because of market exectution option ("NOW")
    if trade["OrderType"] == "Buy" or trade["OrderType"] == "Sell":
        trade["Entry"] = (signal[1].split())[-1]

    else:
        trade["Entry"] = float((signal[1].split())[-1])

    trade["StopLoss"] = float((signal[2].split())[-1])
    trade["TP"] = [float((signal[3].split())[-1])]

    # checks if there's a fourth line and parses it for TP2
    if len(signal) > 4:
        trade["TP"].append(float(signal[4].split()[-1]))

    # adds risk factor to trade
    trade["RiskFactor"] = RISK_FACTOR

    return trade
