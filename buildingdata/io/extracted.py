import os
import pandas as pd
from pathlib import Path
from buildingdata import data_path


def write_bdnb_data(df: pd.DataFrame, name: str) -> None:
    """
    Writes BDNB data to the data/extracted directory using df.to_csv without
    index.

    Parameters:
        df: pd.DataFrame
            Dataframe to be written.
        name: str
            Name of the output file (no extesntion).

    Returns:
        None

    """
    table_directory = Path(data_path["bdnb extracted"])
    os.makedirs(table_directory, exist_ok=True)
    path = Path(table_directory, f"{name}.csv")
    df.to_csv(path, index=False)


def load_bdnb_data(name: str) -> pd.DataFrame:
    """
    Loads BDNB data from the data/extracted directory using pd.read_csv,
    indexed with BDNB ids.

    Parameters:
        name: str
            Name of the input file (no extension).

    Returns:
        df: pd.DataFrame
            Dataframe containing the input data.
    """
    path = Path(data_path["bdnb extracted"], f"{name}.csv")
    df = pd.read_csv(path, index_col="batiment_groupe_id")
    return df


def load_ademe_data(dir: str) -> pd.DataFrame:
    """
    Loads ADEME data from the data/extracted directory using pd.read_csv,
    indexed with BDNB ids.

    Parameters:
        dir: str
            Name of the directory where the extracted data is stored.

    Returns:
        df: pd.DataFrame
            Dataframe containing the input data.
    """
    path = Path(data_path["ademe extracted"], dir, "dpe_extracted.csv")
    df = pd.read_csv(path, sep=";")
    return df


def write_ademe_data(df: pd.DataFrame, name: str, dir: str) -> None:
    """
    Writes ADEME data to the data/extracted directory using pd.to_csv. Creates
    the directory organisation to match the one from source ADEME data if it
    does not exist.

    Parameters:
        df: pd.DataFrame
            Datframe to be written.
        name: str
            Name of the csv file to be save.
        dir: str
            Name of the directory where to save the file.

    Returns:
        None

    """
    table_directory = Path(data_path["ademe extracted"], dir)
    os.makedirs(table_directory, exist_ok=True)
    path = Path(table_directory, f"{name}.csv")
    df.to_csv(path, sep=";", index=False)
