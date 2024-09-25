import argparse

from smhi.smhi_api import SMHIDataAPI


def main():
    parser = argparse.ArgumentParser(
        description="Script to extract data from SMHI's Open API"
    )

    parser.add_argument(
        "--parameters", action="store_true", help="List SMHI API parameters"
    )

    smhi_api = SMHIDataAPI()

    args = parser.parse_args()
    if args.parameters:
        smhi_api.display_parameters()


if __name__ == "__main__":
    main()
