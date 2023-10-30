import pandas as pd
from pathlib import Path
from buildingdata import PATH_TO_ADDRESSES
from buildingdata import data_path
from buildingdata.logger import logger


def load_bdnb_data(table: str, columns: list[str]) -> pd.DataFrame:
    """
    Loads data from the data/source/bdnb directory using pd.read_csv.

    Parameters:
        table: str
            Name of the input file (no extension).
        columns: list[str]
            Column names to be extracted from the table.

    Returns:
        df: pd.DataFrame
            Dataframe containing the input data.
    """
    logger.info(f"Importing {' '.join(columns)} from {table}")
    path = Path(data_path["bdnb source"], f"{table}.csv")
    df = pd.read_csv(path, usecols=columns)
    return df


def load_address_data(columns: list[str]) -> pd.DataFrame:
    """
    Loads data from the data/source/nexity directory using pd.read_csv.

    Parameters:
        columns: list[str]
            Column names to be extracted from the table.

    Returns:
        df: pd.DataFrame
            Dataframe containing the input data.
    """
    path = PATH_TO_ADDRESSES
    df = pd.read_csv(path, usecols=columns, sep=";")
    return df


def load_ademe_data(table: str, columns: list[str]):
    """
    Loads data from the data/source/ademe directory using pd.read_csv.

    Parameters:
        table: str
            Name of the input directory.
        columns: list[str]
            Column names to be extracted from the table.

    Returns:
        df: pd.DataFrame
            Dataframe containing the input data.
    """
    logger.info(f"Importing {' '.join(columns)} from {table}")
    path = Path(data_path["ademe source"], table, "td001_dpe-clean.csv")
    df = pd.read_csv(path, usecols=columns)
    return df
