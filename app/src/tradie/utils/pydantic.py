from pydantic import BaseModel


def print_format_basemodel(obj: BaseModel):
    return obj.model_dump_json(indent=4)
