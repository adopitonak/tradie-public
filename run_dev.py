import locale

from dotenv import load_dotenv
from tradie.telegram.bot import telegram_entrypoint
from tradie.utils.log import get_logger

logger = get_logger(__name__)

load_dotenv('dev.env', override=True)

if __name__ == "__main__":
    logger.info('🏃🏃🏃 Running dev version 🏃🏃🏃')
    telegram_entrypoint()
