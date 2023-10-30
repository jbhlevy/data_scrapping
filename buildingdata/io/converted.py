import glob
import os
import pandas as pd
from pathlib import Path
from buildingdata import data_path


def write_converted_data(df: pd.DataFrame, name: str) -> None:
    """
    Writes data to the data/converted directory using df.to_csv.

    Parameters:
        df: pd.DataFrame
            Dataframe to be written.
        name: str
            Name of the output file (no extesntion).

    Returns:
        None

    """
    path = Path(data_path["converted"], f"{name}.csv")
    df.to_csv(path)


def load_converted_data(name: str) -> pd.DataFrame:
    """
    Loads data from the data/converted directory using pd.read_csv.

    Parameters:
        name: str
            Name of the input file (no extension).

    Returns:
        df: pd.DataFrame
            Dataframe containing the input data.
    """
    path = Path(data_path["converted"], f"{name}.csv")
    df = pd.read_csv(path, index_col="batiment_groupe_id")
    df = df.fillna("MISSING")
    return df


def load_frames_columns(
    tables: list[str],
) -> tuple[list[pd.DataFrame], list[str]]:
    """
    Loads multiple frames and their columns names from the data/converted
    directory. Given a list of table names, loads the corresponding data and
    storeds the corresponding columns.

    Parameters:
        tables: list[str]
            List of table names to be loaded (no extension).

    Returns:
        res, columns: tuple[list[pd.DataFrame], list[str]]
            Tuple containing the list of loaded frames and the list of their
            columns.

    """
    res, columns = [], []
    for name in tables:
        df = load_converted_data(name)
        res.append(df)
        columns.append(
            [e for e in list(df.columns) if e != "batiment_groupe_id"]
        )
    return res, columns


def cleanup_converted_dir():
    to_delete_files = glob.glob(data_path["converted"] + "/*.csv")
    for file in to_delete_files:
        os.remove(file)
