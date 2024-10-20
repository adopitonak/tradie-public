from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from tradie.metatrader.model.order import Order
from tradie.metatrader.mt5_client import MT5Client
from tradie.metatrader.order_handler import OrderHandler
from tradie.telegram.bot_state import CALCULATE, DECISION, OPEN
from tradie.telegram.context_handler import ContextHandler
from tradie.telegram.update_handler import UpdateHandler
from tradie.telegram.utils import restricted, return_on_error
from tradie.utils.common import print_format_dict
from tradie.utils.log import get_logger
from tradie.utils.pydantic import print_format_basemodel

logger = get_logger(__name__)


@restricted
@return_on_error(logger, ConversationHandler.END)
async def place_trade(update: Update, context: CallbackContext) -> int:
    """Parses trade and places on MetaTrader account.

    Arguments:
        update: update from Telegram
        context: CallbackContext object that stores commonly used objects in handler callbacks
    """
    message_handler = UpdateHandler(update)
    context_handler = ContextHandler(context)
    order = context_handler.deserialize_open_order()
    oh = OrderHandler(order)
    handler = oh.place_order()

    await message_handler.get_effective_message().reply_text(
        f"Trade Successfully Executed! 🚀 (id: {handler})\n"
    )

    context_handler.clear_open_order()
    return ConversationHandler.END


@restricted
@return_on_error(logger, OPEN)
async def open_trade_request(update: Update, context: CallbackContext) -> int:
    """Parses trade and places on MetaTrader account.

    Arguments:
        update: update from Telegram
        context: CallbackContext object that stores commonly used objects in handler callbacks
    """
    message_handler = UpdateHandler(update)
    context_handler = ContextHandler(context)

    signal = message_handler.get_effective_message_text()

    mt5_client = MT5Client()
    order, position_info = mt5_client.create_open_order_from_risk(
        signal, with_position_info=True
    )
    logger.info(f"Created order: {order}")

    await message_handler.get_effective_message().reply_text(
        f"Trade Successfully Parsed! 🥳 Checking if the order can be executed...\n\nPosition Info: {print_format_basemodel(position_info)}"
    )

    # clean up the order and see if it could be executed on the server
    final_order = mt5_client.amend_order(order)
    peak_order = print_format_dict(mt5_client.peak_order(final_order))
    check_result = print_format_dict(mt5_client.check_order(final_order))
    await message_handler.get_effective_message().reply_text(
        f"Order: {peak_order}\n\nCheck result:\n{check_result}\n"
    )

    # asks the user if they would like to enter or decline trade
    await message_handler.get_effective_message().reply_text(
        "Would you like to enter this trade?\nTo enter, select: /yes\nTo decline, select: /no"
    )

    assert isinstance(final_order, Order)
    context_handler.serialize_open_order(final_order)

    return DECISION


@restricted
@return_on_error(logger, CALCULATE)
async def calculate_position_size(update: Update, context: CallbackContext) -> int:
    """Parses trade and places on MetaTrader account.

    Arguments:
        update: update from Telegram
        context: CallbackContext object that stores commonly used objects in handler callbacks
    """
    if update.effective_message is None or update.effective_message.text is None:
        return ConversationHandler.END

    signal = update.effective_message.text

    mt5_client = MT5Client()
    position_size, position_info = mt5_client.calculate_position_size_from_risk(
        signal, with_position_info=True
    )
    logger.info(f"Calculated position size: {position_size}")

    # sets the user context trade equal to the parsed trade
    await update.effective_message.reply_text("Trade Successfully Parsed! 🥳")
    await update.effective_message.reply_text(
        f"Position size: {position_size}\n\nInfo:\n{print_format_basemodel(position_info)}\n"
    )

    return ConversationHandler.END
