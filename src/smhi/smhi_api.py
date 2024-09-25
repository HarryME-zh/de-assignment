import xml.etree.ElementTree as ET

import requests


class SMHIDataAPI:
    """
    Class to handle communication with and extract data from the SMHI Open API.
    """

    def __init__(self):
        """Initialize SMHIDataAPI class"""
        self.base_url = "https://opendata-download-metobs.smhi.se/api/version/latest/"

    def fetch_smhi_parameters(self, endpoint="parameter/"):
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

    def parse_smhi_parameters(self, xml_data):
        """Parse the XML data and extract parameters and summaries."""
        try:
            root = ET.fromstring(xml_data)
            namespace = {"atom": "http://www.w3.org/2005/Atom"}
            parameters = []

            for entry in root.findall("atom:entry", namespace):
                title = entry.find("atom:title", namespace).text
                summary = entry.find("atom:summary", namespace).text
                parameters.append(f"{title} ({summary})")

            return parameters
        except ET.ParseError as e:
            print(f"Error parsing XML: {e}")
            return []

    def display_parameters(self):
        """Fetch and display parameters from the SMHI API."""
        # Fetch XML data
        xml_data = self.fetch_smhi_parameters()

        if xml_data:
            # Parse and extract parameters
            parameters = self.parse_smhi_parameters(xml_data)

            for idx, param in enumerate(parameters, 1):
                print(f"{idx}. {param}")
        else:
            print("Failed to retrieve data from the SMHI API.")
