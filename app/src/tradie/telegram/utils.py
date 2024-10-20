from functools import wraps

from tradie.utils.env import EnvVars, read_env_bool, read_env_var


def restricted(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        allow_list = [int(read_env_var(EnvVars.TELEGRAM_ID))]
        if user_id not in allow_list:
            print(f"Unauthorized access denied for {user_id}.")
            print(f"allow list {allow_list}")
            return
        return await func(update, context, *args, **kwargs)

    return wrapped


def return_on_error(logger, state: int):
    def dec(func):
        @wraps(func)
        async def catch_error(update, context, *args, **kwargs):
            # bypass error handling in dev mode
            dev_mode = read_env_bool(EnvVars.DEV_MODE)
            if dev_mode:
                return await func(update, context, *args, **kwargs)

            try:
                return await func(update, context, *args, **kwargs)
            except Exception as error:
                logger.error(f"Error: {error}")
                errorMessage = f"There was an error 😕\n\nError: {error}\n\nPlease try again or use the /cancel to command to cancel this action."
                await update.effective_message.reply_text(errorMessage)
                return state

        return catch_error

    return dec
