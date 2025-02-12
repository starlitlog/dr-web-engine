import pytest
from unittest.mock import patch, mock_open
from engine.web_engine.parsers.json5_parser import parse_json5
# from engine.web_engine.models import ExtractionQuery, ExtractStep, FollowStep, PaginationSpec
import json


# Test parse_json5
def test_parse_json5():
    query_data = {
        "@url": "https://example.com",
        "@steps": [
            {
                "@xpath": "//div",
                "@name": "step1",
                "@fields": {"field1": ".//span"},
                "@follow": {
                    "@xpath": "//a",
                    "@steps": [
                        {
                            "@xpath": "//span",
                            "@fields": {"field2": ".//p"}
                        }
                    ]
                }
            }
        ],
        "@pagination": {"@xpath": "//pagination", "@limit": 10}
    }

    # Mock the file reading
    with patch("builtins.open", mock_open(read_data=json.dumps(query_data))):
        query = parse_json5("dummy_file.json5")

    # Assertions
    assert query.url == "https://example.com"
    assert len(query.steps) == 1
    step = query.steps[0]
    assert step.xpath == "//div"
    assert step.name == "step1"
    assert step.fields["field1"] == ".//span"
    assert step.follow is not None
    assert step.follow.xpath == "//a"
    assert len(step.follow.steps) == 1
    assert step.follow.steps[0].xpath == "//span"
    assert step.follow.steps[0].fields["field2"] == ".//p"
    assert query.pagination is not None
    assert query.pagination.xpath == "//pagination"
    assert query.pagination.limit == 10
