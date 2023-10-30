import re
import pandas as pd
import numpy as np
from buildingdata.logger import logger
from buildingdata.io.utils import load_roof_map


def check_presence_df(value: str | float) -> tuple[bool, str]:
    """
    Checks the pressence of a value in a dataframe.

    Parameters:
        value: str | float
            Value for which the pressence has to be checked.

    Returns:
        res: tuple[bool, str]
            A boolean indicating if the value is present or not. If yes,
            returns the value, else returns MISSING.
    """
    if value == np.NaN or value == "MISSING" or value == "INDETERMINE":
        res = False, "MISSING"
    else:
        res = True, value
    return res


def add_data(df: pd.DataFrame, index: str, receiving_column: str, value: str):
    """
    Adds data to a dataframe.

    Parameters:
        df: pd.DataFrame
            Dataframe receiving data.
        index: str
            Row location where to add the data.
        receiving_column: str
            Column location where to add the data.
        value: str
            Data to be added.

    Returns:
        df: pd.DataFrame
            Dataframe containing the added value.
    """
    df.loc[index, receiving_column] = value
    return df


def create_roof_map() -> dict[str, str]:
    """
    Creates a mapping between BDTOPO roof material code and the actual material
    in string format. Reads in an excel file containing a conversion table and
    stores it in a dictionary.

    Parameters:
        None

    Returns:
        res: dict
            Dictionary containing the code -> material (string) mapping.

    """
    res = {}
    excel = load_roof_map()
    code, value = excel["Code"], excel["Value"]
    for c, v in zip(code, value):
        c = str(c)
        if len(c) == 1:
            c = "0" + c
        res[c] = v
    res["MISSING"] = "MISSING"
    return res


def format_date_range(input_string: str) -> str:
    """
    Formats the string values obtained from the Nexity database to match the
    format of the BDNB. Uses regular expression to find the years and replace
    the original format.

    Parameters:
        input_string: str
            Data value in Nexity format: De XXXX à YYYY

    Returns:
        formatted_string: str
            Converted string to match: XXXX-YYYY
    """
    if input_string == "Non renseigné":
        return "MISSING"
    pattern = r"\bDe (\d{4}) à (\d{4})\b"
    formatted_string = re.sub(pattern, r"\1-\2", input_string)
    return formatted_string


def compare_data(value: str, value1: str) -> int:
    """
    Comapres the values from two databases if present in both databases.
    If the values are the same returns 0, else 1, in order to keep count of the
    different values.

    Parameters:
        value: str
            Data value obtained in one frame.
        value1: str
            Data value obtained in another frame.

    Returns:
        0: int
            If the values are the same, there is no need to increment the
            global counter.
        1: int
            If the values are different, increment the global counter.

    """
    if value == value1:
        return 0
    return 1


def format_data(value: str) -> str:
    """
    Applies some formating rules using regular expressions.

    Parameters:
        value: str
            Value to be formated.
    Returns:
        value: str
            Formatted value.
    """
    pattern = r'\["\s*"(\d{4})"\s*]'
    value = re.sub(pattern, r"\1", value)
    pattern_brackets = r'\[\s*"(.*?)"\s*\]'
    value = re.sub(
        pattern_brackets, lambda m: m.group(1).replace('", "', ";"), value
    )
    pattern_string_brackets = r'\[\s*("[^"]+")\s*\]'
    value = re.sub(pattern_string_brackets, r"\1", value)
    value = value.replace('"', "")
    value = re.sub(r"\.0$", "", value)
    return value


def format_toiture(value: str) -> str:
    """
    Applies some formating rule for High case words.

    Parameters:
        value: str
            Value to be formated.
    Returns:
        value: str
            Formatted value.
    """
    if value != "MISSING":
        value = value.title()
    return value


def format_vitrage(value: str) -> str:
    """
    Applies some formating rules using regular expressions.

    Parameters:
        value: str
            Value to be formated.
    Returns:
        value: str
            Formatted value.
    """
    value = re.sub(r"\b0\.0\b", "NON", value)
    value = re.sub(r"\b1\.0\b", "OUI", value)
    return value


# -----------------------------------------------------------------------------


def create_table_columns(
    tables: list[str], columns: list[list[str]]
) -> tuple[list[str], list[list[str]]]:
    """
    Helper function to handle the structure and order of tables and columns
    during the creation of the multi-index pandas object.

    Parameters:
        tables: list[str]
            List of table names to be merged.
        columns: list[list[str]]
            List of list containing the columns of each tables (there are as
            many lists as there are tables).

    Returns:
        tables: list[str]
            New list of table names to be merged.
        columns: list[list[str]]
            New list of list containing the columns of each tables.
    """
    tables = ["ID"] + tables
    columns = [["batiment_groupe_id"]] + columns
    columns[0] = ["addresse"] + columns[0]
    return tables, columns


def get_missing_columns(row):
    if row.shape[0] != 1:
        logger.error("Single row had shape different from 1 at input.")
    columns = row.columns[row.isna().any()].tolist()
    return columns


def merge_rows(rows: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    """
    Merges similar rows to keep only the one with the least amount of null
    values. First identify the index of the row to keep, then drops all other
    indexes.

    Parameters:
        rows: pd.DataFrame
            Rows to be merged.
        df: pd.DataFrame
            Dataframe containing the rows to be merged/droped.

    Returns:
        df: pd.DataFrame
            The resulting merged dataframe.
    """
    row_keep = rows[
        rows.isnull().sum(axis=1) == min(rows.isnull().sum(axis=1))
    ]
    if row_keep.shape[0] != 1:
        row_keep = pd.Index([row_keep.first_valid_index()])
        different = rows.index.difference(row_keep)
        row_keep = df.loc[row_keep]
    else:
        different = rows.index.difference(row_keep.index)
    missing_columns = get_missing_columns(row_keep)
    for index in different:
        for column in missing_columns:
            if not df.loc[index, column] is np.NaN:
                df.loc[row_keep.index, column] = df.loc[index, column]
    df = df.drop(different, axis=0)
    return df
