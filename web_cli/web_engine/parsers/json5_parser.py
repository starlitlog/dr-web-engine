import json5
from ..models import ExtractionQuery


def parse_json5(query_file: str) -> ExtractionQuery:
    with open(query_file, "r") as f:
        query_data = json5.load(f)
    return ExtractionQuery(**query_data)
