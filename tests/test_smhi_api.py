from unittest.mock import Mock, patch

import aiohttp
import pytest
import requests

from smhi.smhi_api import SMHIDataAPI

from .mock_response import MockResponse


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


def test_display_parameters(smhi_parameter_xml_response, capfd):
    """Test overall functions to display the parameters with an example xml response."""
    api = SMHIDataAPI()

    with patch.object(
        api, "_fetch_smhi_parameters", return_value=smhi_parameter_xml_response
    ):
        api.display_parameters()

    expected_output = (
        "11. Global Irradians (svenska stationer) (medelvärde 1 timma, varje timme)\n"
        "21. Byvind (max, 1 gång/tim)\n"
        "22. Lufttemperatur (medel, 1 gång per månad)\n"
        "39. Daggpunktstemperatur (momentanvärde, 1 gång/tim)\n"
    )
    captured = capfd.readouterr()
    assert captured.out == expected_output


def test_get_station_data_success():
    """Test the _get_station_data method when the request is successful."""
    api = SMHIDataAPI()

    example_station_data = {
        "station": [
            {"id": 1, "name": "Station A"},
            {"id": 2, "name": "Station B"},
        ]
    }

    expected_stations = example_station_data["station"]

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = example_station_data

    with patch("requests.get", return_value=mock_response):
        result = api._get_station_data()
        assert result == expected_stations


def test_get_station_data_failure():
    """Test the _get_station_data method when the request fails."""
    api = SMHIDataAPI()

    mock_response = Mock()
    mock_response.status_code = 404

    with patch("requests.get", return_value=mock_response):
        result = api._get_station_data()
        assert result is None


@pytest.mark.asyncio
async def test_fetch_station_temp_success(smhi_temperature_json_response):
    """Test the fetch_station_temp method when the request is successful."""
    station = {"id": 159880, "name": "Arvidsjaur A"}
    api = SMHIDataAPI()

    mock_response = MockResponse(smhi_temperature_json_response, 200)

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        async with aiohttp.ClientSession() as session:
            result = await api._fetch_station_temp(session, station)
            assert result == {"Arvidsjaur A": 5.3}


@pytest.mark.asyncio
async def test_fetch_station_temp_failure():
    """Test the fetch_station_temp method when the request fails."""

    station = {"id": 178740, "name": "Aktse"}
    api = SMHIDataAPI()

    mock_response = MockResponse({}, 404)

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        async with aiohttp.ClientSession() as session:
            result = await api._fetch_station_temp(session, station)
            assert result == {}


@pytest.mark.asyncio
async def test_get_daily_temperature_success():
    """Test the get_daily_temperature method when the API calls are successful."""

    stations = [{"id": 159880, "name": "Arvidsjaur A"}, {"id": 178740, "name": "Aktse"}]
    api = SMHIDataAPI()

    with patch.object(api, "_get_station_data", return_value=stations):
        with patch.object(
            api,
            "_fetch_station_temp",
            side_effect=[{"Arvidsjaur A": 5.3}, {"Aktse": 6.1}],
        ):
            result = await api.get_daily_temperature()
            expected_result = {"Arvidsjaur A": 5.3, "Aktse": 6.1}
            assert result == expected_result


@pytest.mark.asyncio
async def test_get_daily_temperature_no_stations():
    """Test the get_daily_temperature method when no stations are returned."""
    api = SMHIDataAPI()

    with patch.object(api, "_get_station_data", return_value=None):
        result = await api.get_daily_temperature()
        assert result == {}


@pytest.mark.asyncio
async def test_display_temperature_info_success(smhi_temperature_dict_data, capfd):
    """Test display_temperature_info method when temperature data is available."""
    api = SMHIDataAPI()

    with patch.object(
        api, "get_daily_temperature", return_value=smhi_temperature_dict_data
    ):
        await api.display_temperature_info()

    captured = capfd.readouterr()

    expected_highest = "Highest temperature: Hoburg A, 16.6 degrees"
    expected_lowest = "Lowest temperature: Tarfala A, -0.9 degrees"

    assert expected_highest in captured.out
    assert expected_lowest in captured.out


@pytest.mark.asyncio
async def test_display_temperature_info_no_data(capfd):
    """Test display_temperature_info method when no temperature data is available."""
    api = SMHIDataAPI()

    with patch.object(api, "get_daily_temperature", return_value={}):
        await api.display_temperature_info()

    captured = capfd.readouterr()
    assert "No temperature data available." in captured.out
