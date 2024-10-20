import locale

from dotenv import load_dotenv
from tradie.telegram.bot import telegram_entrypoint

load_dotenv(override=True)

locale.setlocale(locale.LC_ALL, "")

if __name__ == "__main__":
    telegram_entrypoint()
