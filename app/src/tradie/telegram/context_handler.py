import json
from telegram.ext import CallbackContext

from tradie.metatrader.model.order import Order
from tradie.utils.error import TelegramContextError


class ContextHandler:
    def __init__(self, context: CallbackContext):
        self.context = context
        self.open_order_field = "open order"

    def is_open_order_set(self):
        return (
            self.context.user_data is not None
            and self.context.user_data[self.open_order_field] is not None
        )

    def serialize_open_order(self, order: Order):
        if self.is_open_order_set():
            raise TelegramContextError(
                "Open order is already set. Will not set a new one."
            )
        if not self.context.user_data:
            raise TelegramContextError("Missing user data in telegram context object.")
        self.context.user_data[self.open_order_field] = order.model_dump_json()

    def deserialize_open_order(self):
        if not self.is_open_order_set():
            raise TelegramContextError(
                "Cannot deserialize open order, because open order is missing."
            )
        order_json = self.context.user_data[self.open_order_field]
        order_dict = json.loads(order_json)
        return Order(**order_dict)
    
    def clear_open_order(self):
        self.context.user_data[self.open_order_field] = None
