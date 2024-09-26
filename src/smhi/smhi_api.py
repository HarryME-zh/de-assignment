import asyncio
import xml.etree.ElementTree as ET

import aiohttp
import requests


class SMHIDataAPI:
    """
    Class to handle communication with and extract data from the SMHI Open API.
    """

    def __init__(self):
        """Initialize SMHIDataAPI class"""
        self.base_url = "https://opendata-download-metobs.smhi.se/api/version/latest"
        self.temperature_url = f"{self.base_url}/parameter/2.json"

    def _fetch_smhi_parameters(self, endpoint="/parameter/"):
        """Fetch XML data from the SMHI API."""
        try:
            response = requests.get(self.base_url + endpoint)
            if response.status_code == 200:
                return response.content
            else:
                print(f"Error: Received status code {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None

    def _parse_smhi_parameters(self, xml_data):
        """Parse the XML data and extract parameters and summaries."""
        try:
            root = ET.fromstring(xml_data)
            namespace = {"atom": "http://www.w3.org/2005/Atom"}
            parameters = {}

            for entry in root.findall("atom:entry", namespace):
                title = entry.find("atom:title", namespace).text
                summary = entry.find("atom:summary", namespace).text
                link = entry.find('atom:link[@type="application/json"]', namespace)
                # Extract the index from the href (e.g., parameter/2.json -> key = 2)
                href = link.attrib.get("href", "")
                key = href.split("/")[-1].replace(".json", "") if href else "Unknown"

                parameters.update({int(key): f"{title} ({summary})"})
            parameters_sorted = dict(sorted(parameters.items()))
            return parameters_sorted
        except ET.ParseError as e:
            print(f"Error parsing XML: {e}")
            return []

    def display_parameters(self):
        """Fetch and display parameters from the SMHI API."""
        xml_data = self._fetch_smhi_parameters()

        if xml_data:
            parameters = self._parse_smhi_parameters(xml_data)
            for key, param in parameters.items():
                print(f"{key}. {param}")
        else:
            print("Failed to retrieve data from the SMHI API.")

    def _get_station_data(self):
        """Fetch list of all stations."""
        response = requests.get(self.temperature_url)
        if response.status_code == 200:
            station_data = response.json()
            return station_data["station"]
        else:
            print(f"Failed to fetch station data: {response.status_code}")
            return None

    async def _fetch_station_temp(self, session, station):
        """Async fetch daily temperature of a station"""
        station_name = station["name"]
        station_id = station["id"]
        station_daily_temp_url = (
            f"{self.base_url}/parameter/2/station/{station_id}"
            "/period/latest-day/data.json"
        )

        async with session.get(station_daily_temp_url) as response:
            if response.status == 200:
                station_temp_info = await response.json()
                if station_temp_info.get("value"):
                    temperature = float(station_temp_info["value"][0]["value"])
                    return {station_name: temperature}
            return {}

    async def get_daily_temperature(self):
        """Call api to get daily temperatures of avaliable stations."""
        stations = self._get_station_data()
        stations_daily_temp = {}

        if stations:
            async with aiohttp.ClientSession() as session:
                tasks = [
                    self._fetch_station_temp(session, station) for station in stations
                ]
                results = await asyncio.gather(*tasks)
                for result in results:
                    if result:
                        stations_daily_temp.update(result)

        return stations_daily_temp

    async def display_temperature_info(self):
        """Display the highest and lowest temperatures."""
        stations_daily_temp = await self.get_daily_temperature()

        if stations_daily_temp:
            highest_station = max(stations_daily_temp, key=stations_daily_temp.get)
            lowest_station = min(stations_daily_temp, key=stations_daily_temp.get)

            highest_temp = stations_daily_temp[highest_station]
            lowest_temp = stations_daily_temp[lowest_station]

            print(f"Highest temperature: {highest_station}, {highest_temp} degrees")
            print(f"Lowest temperature: {lowest_station}, {lowest_temp} degrees")
        else:
            print("No temperature data available.")
