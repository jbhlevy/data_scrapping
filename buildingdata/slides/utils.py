import os
import pandas as pd
from pathlib import Path
from buildingdata import data_path
from buildingdata.identification.utils import clean_address


def images_available() -> bool:
    """
    Helper function to know if the solar images have already been extracted.

    Parameters:
        None

    Returns:
        True | False: bool
            Boolean value showing if directory ../images/solar exists.
    """
    path = Path(data_path["ppt"], "images/solar")
    if os.path.exists(path):
        return True
    os.makedirs(path)
    return False


def load_addresses(df: pd.DataFrame) -> list[str]:
    """
    Extract addresses from the input dataframe.

    Parameters:
        df: pd.DataFrame
            Dataframe containing all the merged data.

    Returns:
        addresses: list[str]
            List of all the addresses that will be used in slide generation.
    """
    addresses = df["ID"]["addresse"].to_list()
    addresses = list(map(clean_address, addresses))
    addresses = list(map(str.lower, addresses))
    return addresses


text_placeholder_map = {
    "2": "Localisation",
    "4": "Système",
    "5": "Parois",
    "6": "Général",
    "7": "Menuiseries",
    "13": "Occupants",
}


row_map = {"8": 2, "9": 6, "10": 11, "11": 9, "12": 4, "14": 2}
