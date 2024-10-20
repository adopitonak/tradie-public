import os
from enum import Enum


class EnvVars(str, Enum):
    VERBOSE = "VERBOSE"
    DEV_MODE = "DEV_MODE"
    TELEGRAM_BOT_API = "TELEGRAM_BOT_API"
    TELEGRAM_USER = "TELEGRAM_USER"
    TELEGRAM_ID = "TELEGRAM_ID"
    MT5_SERVER = "MT5_SERVER"
    MT5_USERNAME = "MT5_USERNAME"
    MT5_PASSWORD = "MT5_PASSWORD"
    TRADIE_RISK_FACTOR = "TRADIE_RISK_FACTOR"
    TRADIE_RISK_AMOUNT = "TRADIE_RISK_AMOUNT"
    TWEAK_TOWARDS_AGGRESSIVE_TRADE = "TWEAK_TOWARDS_AGGRESSIVE_TRADE"
    PROFIT_COMPROMISE_THRESHOLD = "PROFIT_COMPROMISE_THRESHOLD"
    PROFIT_COMPROMISE_ALWAYS_ATTEMPT = "PROFIT_COMPROMISE_ALWAYS_ATTEMPT"


def read_env_var(env_var: EnvVars):
    """Reads env_var and returns None if it doesn't exist. Otherwise returns True/False"""
    return os.environ.get(env_var, None)


def read_env_bool(env_var: EnvVars):
    """Reads env_var and returns None if it doesn't exist. Otherwise returns True/False"""
    var = os.getenv(env_var, None)
    if var is None:
        return None
    return var.lower() in ("true", "1", "t")


def read_env_bool_default_false(env_var: EnvVars):
    """Reads env_var and returns False if it doesn't exist. Otherwise returns True/False"""
    return False if read_env_bool(env_var) is None else read_env_bool(env_var)
