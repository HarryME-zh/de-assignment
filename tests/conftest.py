import json
import os

import pytest


@pytest.fixture
def smhi_parameter_xml_response():
    """Fixture to load the param XML response from a file"""
    xml_path = os.path.join(
        "tests",
        "example_api_responses",
        "smhi_parameter_response.xml",
    )
    with open(xml_path, encoding="utf-8") as file:
        return file.read()


@pytest.fixture
def smhi_temperature_json_response():
    """Fixture to load the temp response json data from a file"""
    json_path = os.path.join(
        "tests",
        "example_api_responses",
        "smhi_temperature_response.json",
    )
    with open(json_path) as f:
        data = json.load(f)
    return data


@pytest.fixture
def smhi_temperature_dict_data():
    """Fixture to load the test temp dict data from a file"""
    json_path = os.path.join(
        "tests",
        "example_api_responses",
        "smhi_temp_dict.json",
    )
    with open(json_path) as f:
        data = json.load(f)
    return data
