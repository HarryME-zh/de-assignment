import argparse
import asyncio

from smhi.smhi_api import SMHIDataAPI


def main():
    parser = argparse.ArgumentParser(
        description="Script to extract data from SMHI's Open API"
    )

    parser.add_argument(
        "--parameters", action="store_true", help="List SMHI API parameters"
    )
    parser.add_argument(
        "--temperatures",
        action="store_true",
        help="Display highest and lowest temperatures",
    )

    smhi_api = SMHIDataAPI()

    args = parser.parse_args()
    if args.parameters:
        smhi_api.display_parameters()

    if args.temperatures:
        asyncio.run(smhi_api.display_temperature_info())


if __name__ == "__main__":
    main()
