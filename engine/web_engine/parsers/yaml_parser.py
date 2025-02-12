import yaml
from ..models import ExtractionQuery


def parse_yaml(query_file: str) -> ExtractionQuery:
    with open(query_file, "r") as f:
        query_data = yaml.safe_load(f)
    return ExtractionQuery(**query_data)
