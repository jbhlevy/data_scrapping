import pandas as pd
from pathlib import Path
from buildingdata import data_path


def write_columns(df: pd.DataFrame, name: str) -> None:
    """
    Writes the columns extracted using the get_columns function of the main
    file to a csv file specified as argument.

    Parameters:
        df: pd.DataFrame
            Dataframe to be saved.
        name: str
            Name of the file where to save the dataframe.

    Returns:
        None
    """
    path = Path(data_path["merged"], f"{name}.csv")
    df.to_csv(path)


def write_merged_data(df: pd.DataFrame) -> None:
    """
    Writes the final merged data to the data/merged directory using df.to_csv.

    Parameters:
        df: pd.DataFrame
            Dataframe to be written.

    Returns:
        None

    """
    path = Path(data_path["merged"], "final_data.csv")
    df.to_csv(path)


def load_merged_data() -> pd.DataFrame:
    """
    Loads data from the data/merged directory using pd.read_csv, header is
    specified for multi-indexing and na_values used to count missing values in
    data diagnostics.

    Parameters:
        None

    Returns:
        df: pd.DataFrame
            Dataframe containing the input data.
    """
    path = Path(data_path["merged"], "final_data.csv")
    df = pd.read_csv(path, header=[0, 1], na_values="MISSING", index_col=0)
    return df
