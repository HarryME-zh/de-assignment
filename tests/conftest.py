import os

import pytest


@pytest.fixture
def smhi_parameter_xml_response():
    """Fixture to load the test param XML data from a file"""
    xml_path = os.path.join(
        "tests",
        "example_api_responses",
        "smhi_parameter_response.xml",
    )
    with open(xml_path, encoding="utf-8") as file:
        return file.read()
