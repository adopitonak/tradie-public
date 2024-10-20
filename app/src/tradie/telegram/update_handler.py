from telegram import Update

from tradie.utils.error import TelegramMessageError


class UpdateHandler:
    def __init__(self, update: Update):
        self.update = update

    def is_effective_message_set(self):
        return (
            self.update.effective_message is not None
            and self.update.effective_message.text is not None
        )

    def get_effective_message_text(self) -> str:
        if not self.is_effective_message_set():
            raise TelegramMessageError()
        return self.update.effective_message.text  # type: ignore

    def get_effective_message(self):
        if self.update.effective_message is None:
            raise TelegramMessageError("Expected effective message object to exist.")
        return self.update.effective_message
    
    def get_username(self):
        return self.update.effective_message.chat.username
