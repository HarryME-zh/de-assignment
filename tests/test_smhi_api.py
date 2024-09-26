from unittest.mock import Mock, patch

import requests

from smhi.smhi_api import SMHIDataAPI


def test_fetch_smhi_parameters_success():
    """Test the _fetch_smhi_parameters method when the request is successful."""
    api = SMHIDataAPI()

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"<xml>Test Data</xml>"

    with patch("requests.get", return_value=mock_response):
        result = api._fetch_smhi_parameters()

        assert result == b"<xml>Test Data</xml>"


def test_fetch_smhi_parameters_failure():
    """Test the _fetch_smhi_parameters method when the request fails."""
    api = SMHIDataAPI()

    mock_response = Mock()
    mock_response.status_code = 404

    with patch("requests.get", return_value=mock_response):
        result = api._fetch_smhi_parameters()
        assert result is None


def test_fetch_smhi_parameters_exception():
    """Test the _fetch_smhi_parameters method when there is a RequestException."""
    api = SMHIDataAPI()

    with patch("requests.get", side_effect=requests.RequestException("Error")):
        result = api._fetch_smhi_parameters()
        assert result is None


def test_parse_smhi_parameters(smhi_parameter_xml_response):
    """Test the _parse_smhi_parameters method with an example xml response."""
    api = SMHIDataAPI()

    expected_parameters = {
        11: "Global Irradians (svenska stationer) (medelvärde 1 timma, varje timme)",
        21: "Byvind (max, 1 gång/tim)",
        22: "Lufttemperatur (medel, 1 gång per månad)",
        39: "Daggpunktstemperatur (momentanvärde, 1 gång/tim)",
    }

    parsed_parameters = api._parse_smhi_parameters(smhi_parameter_xml_response)
    assert parsed_parameters == expected_parameters


def test_display_parameters(smhi_parameter_xml_response, capfd, mocker):
    """Test overall functions to display the parameters with an example xml response."""
    api = SMHIDataAPI()

    mocker.patch.object(
        api, "_fetch_smhi_parameters", return_value=smhi_parameter_xml_response
    )
    expected_output = (
        "11. Global Irradians (svenska stationer) (medelvärde 1 timma, varje timme)\n"
        "21. Byvind (max, 1 gång/tim)\n"
        "22. Lufttemperatur (medel, 1 gång per månad)\n"
        "39. Daggpunktstemperatur (momentanvärde, 1 gång/tim)\n"
    )
    api.display_parameters()

    captured = capfd.readouterr()
    assert captured.out == expected_output
