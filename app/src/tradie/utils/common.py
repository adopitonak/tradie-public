import json
from rich import print


def rich_print(*args, **kwargs):
    """Used in verbose mode to provide CLI feedback for the user"""
    print(*args, **kwargs)


def object_to_dict(obj):
    obj_dict = {}
    for attr in dir(obj):
        if not callable(getattr(obj, attr)) and not attr.startswith("__"):
            obj_dict[attr] = getattr(obj, attr)
    return obj_dict


def print_format_dict(obj: dict):
    return json.dumps(obj, sort_keys=True, indent=4)
