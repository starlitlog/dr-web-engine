from .json5_parser import parse_json5
from .yaml_parser import parse_yaml


def get_parser(query_format: str):
    if query_format == "json5":
        return parse_json5
    elif query_format == "yaml":
        return parse_yaml
    else:
        raise ValueError(f"Unsupported query format: {query_format}")
