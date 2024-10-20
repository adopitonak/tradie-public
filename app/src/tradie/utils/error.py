class AppException(Exception):
    pass


class MT5Error(AppException):
    def __init__(self, msg="Failed in MT5."):
        super().__init__(msg)


class MT5BadConfiguration(MT5Error):
    def __init__(
        self,
        msg="Bad or missing configuration. Ensure ENV variables are set or configuration arguments are provided and valid.",
    ):
        super().__init__(msg)


class MT5HandlerError(AppException):
    def __init__(self, msg="Failed in MT5 Handler."):
        super().__init__(msg)


class MT5ParserError(AppException):
    def __init__(self, msg="Failed in MT5 Parser."):
        super().__init__(msg)


class MT5SymbolNotFound(MT5Error):
    def __init__(self, symbol):
        self.msg = f"{symbol} not found"


class MT5OrderRequestParserError(MT5Error):
    def __init__(self, msg="Failed in MT5 Request Parser."):
        super().__init__(msg)


class TelegramError(AppException):
    def __init__(self, msg="Failed in Telegram."):
        super().__init__(msg)


class TelegramMessageError(TelegramError):
    def __init__(self, msg="Missing message."):
        super().__init__(msg)


class TelegramContextError(TelegramError):
    def __init__(self, msg="Missing context."):
        super().__init__(msg)
