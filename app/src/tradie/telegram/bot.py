import telegram

from tradie.telegram.bot_state import CALCULATE, DECISION, OPEN
from tradie.telegram.context_handler import ContextHandler
from tradie.telegram.execution import (
    calculate_position_size,
    open_trade_request,
    place_trade,
)
from tradie.telegram.update_handler import UpdateHandler
from tradie.telegram.utils import restricted, return_on_error
from tradie.utils.env import EnvVars, read_env_var

from telegram import Update
from telegram.ext import (
    filters,
    Application,
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
)

from tradie.utils.log import get_logger


logger = get_logger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error(f"🥀🥀🥀\nTelegram Exception: {context.error}\n🥀🥀🥀")


@restricted
@return_on_error(logger, ConversationHandler.END)
async def start(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends welcome message to user.

    Arguments:
        update: update from Telegram
        context: ContextTypes.DEFAULT_TYPE object that stores commonly used objects in handler callbacks
    """
    update_handler = UpdateHandler(update)
    welcome_message = "~~~~~~ 🤖🌱 Hi I'm Tradie 🌱🤖 ~~~~~~\n\nLet's make sum moneeeeeeeeeey. See /help and get some help."

    await update_handler.get_effective_message().reply_text(welcome_message)


@restricted
@return_on_error(logger, ConversationHandler.END)
async def help(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a help message when the command /help is issued

    Arguments:
        update: update from Telegram
        context: ContextTypes.DEFAULT_TYPE object that stores commonly used objects in handler callbacks
    """
    update_handler = UpdateHandler(update)

    help_message = "This bot is used to automatically enter trades onto your MetaTrader account directly from Telegram. To begin, ensure that you are authorized to use this bot by adjusting your Python script or environment variables.\n\nThis bot supports all trade order types (Market Execution, Limit, and Stop)"
    commands = "List of commands:\n/start : displays welcome message\n/help : displays list of commands and example trades\n/open : takes in user inputted trade for parsing and placement of new trade\n/calculate : calculates trade position size in lots"
    trade_example = "Example Trades 💴:\n\n"
    market_execution_example = "Market Execution:\nBUY GBPUSD\n[Entry NOW] (optional)\nSL 1.14336\nTP 1.28930\n\n"
    limit_example = (
        "Limit Execution:\nBUY LIMIT GBPUSD\nEntry 1.14480\nSL 1.14336\n[TP 1.28930] (optional)\n\n"
    )
    limit_example2 = (
        "Limit Execution:\nBUY LIMIT EURUSD\nEntry 1.13480\nSL 1.12336\nTP 1.28677\n[Risk 0.5] (optional)\n\n"
    )
    note = "Possible open commands are: BUY, SELL, BUY LIMIT, SELL LIMIT, BUY STOP, SELL STOP\n\n"
    closing_note = "Capitalization of the symbol does matter, capitalization of the 'entry' keyword does not matter. All other words can be anything (order matters)."

    # sends messages to user
    await update_handler.get_effective_message().reply_text(help_message)
    await update_handler.get_effective_message().reply_text(commands)
    await update_handler.get_effective_message().reply_text(
        trade_example + market_execution_example + limit_example + limit_example2 + note
    )


@restricted
@return_on_error(logger, ConversationHandler.END)
async def unknown_command(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Checks if the user is authorized to use this bot or shares to use /help command for instructions.

    Arguments:
        update: update from Telegram
        context: CallbackContext object that stores commonly used objects in handler callbacks
    """
    update_handler = UpdateHandler(update)
    await update_handler.get_effective_message().reply_text(
        "Unknown command. Use /open to place a trade or /calculate to find information for a trade. You can also use the /help command to view instructions for this bot."
    )


@restricted
@return_on_error(logger, ConversationHandler.END)
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation.

    Arguments:
        update: update from Telegram
        context: ContextTypes.DEFAULT_TYPE object that stores commonly used objects in handler callbacks
    """
    update_handler = UpdateHandler(update)
    context_handler = ContextHandler(context)
    
    context_handler.clear_open_order()

    await update_handler.get_effective_message().reply_text("Command has been canceled.")
    return ConversationHandler.END


@restricted
def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Logs Errors caused by updates.

    Arguments:
        update: update from Telegram
        context: ContextTypes.DEFAULT_TYPE object that stores commonly used objects in handler callbacks
    """

    logger.error('Update "%s" caused error "%s"', update, context.error)
    return


@restricted
@return_on_error(logger, ConversationHandler.END)
async def calculation_command(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks user to enter the trade they would like to calculate trade information for.

    Arguments:
        update: update from Telegram
        context: ContextTypes.DEFAULT_TYPE object that stores commonly used objects in handler callbacks
    """
    update_handler = UpdateHandler(update)

    # asks user to enter the trade
    await update_handler.get_effective_message().reply_text(
        "Please enter the trade that you would like to calculate."
    )

    return CALCULATE


@restricted
@return_on_error(logger, ConversationHandler.END)
async def open_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks user to enter the trade they would like to place.

    Arguments:
        update: update from Telegram
        context: ContextTypes.DEFAULT_TYPE object that stores commonly used objects in handler callbacks
    """
    update_handler = UpdateHandler(update)
    context_handler = ContextHandler(context)
    logger.info(f"Hi {update_handler.get_username()}")
    context_handler.clear_open_order()
    await update_handler.get_effective_message().reply_text(
        "Please enter the trade that you would like to place."
    )

    return OPEN


async def main_telegram():
    bot = telegram.Bot(read_env_var(EnvVars.TELEGRAM_BOT_API))
    async with bot:
        print(await bot.get_me())


def telegram_entrypoint() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = (
        Application.builder().token(read_env_var(EnvVars.TELEGRAM_BOT_API)).build()
    )

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("open", open_command),
            CommandHandler("calculate", calculation_command),
        ],
        states={
            CALCULATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, calculate_position_size)
            ],
            OPEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, open_trade_request)],
            DECISION: [
                CommandHandler("yes", place_trade),
                CommandHandler("no", cancel),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT, unknown_command))

    application.add_error_handler(error_handler)

    logger.info("Running 🤖 🌸 🤖 🌺 🤖 🌹 🤖 💐 🤖")

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
