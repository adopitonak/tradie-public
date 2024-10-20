# tradie

## Installation

### Windows

#### mt5

##### Enable Algorithmic Trading
1. Download and install MetaTrader5
2. Log in to your account (the script seems to take it nicer to when you log in first in UI)
3. Tools > Options > Expert Advisors > Allow Algorithmic Trading + Uncheck restrictions

##### Log in the right way
It is important to:
1. Right Click > Accounts
2. Open an Account
3. Enter your broker
4. Log in with existing account

Skipping this step might cause you endless loading and not logging in.

#### app
Note that on windows you might need to use `python -m pip` instead of pip
```
python3 -m venv venv
.\venv\Scripts\activate
pip install -e ".[dev,mt5]"
```

## Docs

### Telegram Bot
- Start here: https://github.com/python-telegram-bot/python-telegram-bot/wiki/Introduction-to-the-API
- Documentation: https://docs.python-telegram-bot.org/en/v21.4/telegram.html
- Starter Example: https://docs.python-telegram-bot.org/en/v21.4/examples.conversationbot.html

## Unit Test Values

### Position size calculations
```
EURUSD SELL 1.1167 -> 1.1168 (risk 10 EUR [10.00]) ---> 1 lot
CADCHF SELL 0.6286 -> 0.6290 (risk 100 EUR [100.06]) ---> 2.12 lot
XAUEUR SELL 2252 -> 2254 (risk 100 EUR [100.46]) ---> 0.45 lot
XAUEUR BUY 2257 -> 2256 (risk 100 EUR [99.89]) ---> 1.79 lot
```

## Inspired By
https://github.com/ehijiele1/Telegram-Signal-Copier-to-MT4-MT5
