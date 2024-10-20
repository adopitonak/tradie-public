import os

import typer


def envvar_callback(param: typer.CallbackParam, value: str | None):
    if value is not None:
        os.environ[param.envvar] = value  # type: ignore


def envvar_bool_callback(param: typer.CallbackParam, value: bool):
    os.environ[param.envvar] = str(value)  # type: ignore
