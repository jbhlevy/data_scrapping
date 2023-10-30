import pandas as pd
import glob
from pathlib import Path
from buildingdata import data_path
from buildingdata.logger import logger
from .utils import (
    check_directory_content,
    extract_table_name,
    get_bdnb_source_table,
    get_columns,
    get_new_label,
    get_second_source_label,
)


def select_bdnb_columns(df: pd.DataFrame) -> dict[str, list[str]]:
    """
    Creates the table name -> list of table columns mapping by reading in the
    input file and extracting the columns names associated to each table name.

    Parameters:
        df: pd.DataFrame
            Dataframe loaded from the excel file containing the mapping.

    Returns:
        table_col_map: dict[str, list[str]]
            The newly created table name -> list[columns] mapping.
    """
    tables = df["Table BDNB"][1:]
    bdnb_map = {table: get_columns(df, table) for table in tables}
    return bdnb_map


def load_bdnb_selection() -> dict[str, list[str]]:
    """
    From the data_tables.xlsx file in data/selection, read in the table &
    columns of interest. Create a mapping table name -> column list that we
    will use for data extraction. Performs a check on the data/extracted
    directory content to avoid running the extraction twice on the same file

    Parameters:
        None

    Returns:
        bdnb_selection: dict[str, list]
            Dictionnary mapping the table name to the list of columns to be
            extracted from it.
    """
    path = Path(data_path["selection"], "data_tables.xlsx")
    df = pd.read_excel(path)
    bdnb_selection = select_bdnb_columns(df)
    bdnb_selection = check_directory_content(
        data_path["bdnb extracted"], bdnb_selection
    )
    logger.info(
        f"Sucessfully loaded bdnb selection, will proceed to extraction on\
 {list(bdnb_selection.keys())}"
    )
    # Logger information
    return bdnb_selection


def load_departement_selection(
    df: pd.DataFrame, name: str
) -> dict[str, list[str]]:
    """
    From the input dataframe file in data/selection, read in the table &
    columns of interest. Create a mapping table name -> column list that we
    will use for data extraction.

    Parameters:
        df: pd.DataFrame
            Dataframe containing the selected departements and columns.
        name: str
            Name of the database for wich the selection is being created.

    Returns:
        bdnb_selection: dict[str, list]
            Dictionnary mapping the table name to the list of columns to be
            extracted from it.
    """
    column_name = f"Colonne {name.upper()}"
    column_list = df.dropna(subset=column_name)[column_name].to_list()
    tables = list(
        map(
            extract_table_name,
            glob.glob(f"{data_path[f'{name} source']}/*/", recursive=True),
        )
    )
    selection = {table: column_list for table in tables}

    return selection


def load_bdtopo_selection(convert: bool = False) -> dict[str, list[str]]:
    """
    From the data_tables.xlsx file in data/selection, read in the table &
    columns of interest. Calls a generic function to create the  mapping table
    name -> column list that we will use for data extraction.

    Parameters:
        None

    Returns:
        bdnb_selection: dict[str, list]
            Dictionnary mapping the table name to the list of columns to be
            extracted from it.
    """
    path = Path(data_path["selection"], "data_tables.xlsx")
    df = pd.read_excel(path)
    bdtopo_selection = load_departement_selection(df, "bdtopo")
    if convert is False:
        bdtopo_selection = check_directory_content(
            data_path["bdtopo extracted"], bdtopo_selection
        )
    return bdtopo_selection


def load_ademe_selection(convert: bool = False) -> dict[str, list[str]]:
    """
    From the data_tables.xlsx file in data/selection, read in the table &
    columns of interest. Calls a generic function to create the  mapping table
    name -> column list that we will use for data extraction.

    Parameters:
        None

    Returns:
        bdnb_selection: dict[str, list]
            Dictionnary mapping the table name to the list of columns to be
            extracted from it.
    """
    path = Path(data_path["selection"], "data_tables.xlsx")
    df = pd.read_excel(path)
    ademe_selection = load_departement_selection(df, "ademe")
    if convert is False:
        ademe_selection = check_directory_content(
            data_path["ademe extracted"], ademe_selection
        )
    return ademe_selection


def create_database_mapping() -> dict[tuple, tuple]:
    """
    Creates the mapping between (BDNB_table, BDNB_column) to the new
    (table, column) it will belong to. This format of correspondance allows to
    know where to acess the data, and where to copy it with one single call.

    Parameters:
        None

    Returns:
        mapping: dict
            Dictionnary containing the newly made mapping.
    """
    path = Path(data_path["selection"], "data_tables.xlsx")
    df = pd.read_excel(path)
    mapping = {}
    new_table = ""
    new_column = ""
    for _, row in df.iterrows():
        if isinstance(row["Type de donnée"], float):
            table, column = row["Table BDNB"], row["Colonne BDNB"]
            if not isinstance(row["Colonne"], float):
                new_column = row["Colonne"]
        elif isinstance(row["Colonne"], float):
            table, column = row["Table BDNB"], row["Colonne BDNB"]
        else:
            table, column = row["Table BDNB"], row["Colonne BDNB"]
            new_table, new_column = row["Type de donnée"], row["Colonne"]

        mapping[(table.strip(), column.strip())] = (
            new_table.strip(),
            new_column.strip(),
        )
    return mapping


def create_merge_map(name: str) -> dict[str, tuple]:
    """
    Creates a map used to merge data obtained from a second source to the data
    obtained from the BDNB.

    Parameters:
        name: str
            Name of the second database that will be merged.

    Returns:
        merge_bdtopo_map: dict[str, tuple]
            Mapping between the columns to be merged and the (table, column) to
            merge it with.
    """
    path = Path(data_path["selection"], "data_tables.xlsx")
    df = pd.read_excel(path)
    column_name = f"Colonne {name.upper()}"
    columns_list = df[column_name].dropna().to_list()
    merge_map = {
        column: get_new_label(df, column, column_name)
        for column in columns_list
    }
    return merge_map


def load_tables_names() -> list[str]:
    """
    Loads the name of the tables organizing the final extracted database.

    Parameters:
        None

    Returns:
        base_tables: list[str]
            List of table names.
    """
    path = Path(data_path["selection"], "data_tables.xlsx")
    df = pd.read_excel(path)
    base_tables = df["Type de donnée"].dropna().to_list()
    return base_tables


def create_source_map(columns: list[str]) -> dict[str, str]:
    """
    Creates a mapping between the extracted BDNB table and the original source
    it came from to display in diagnostics files.

    Parameters:
        columns: list[str]
            List of BDNB tables for which the source needs to be found.

    Returns:
        source_map: dict[str, str]
            Mapping between the BDNB table name and its source.

    """
    path = Path(data_path["selection"], "data_tables.xlsx")
    df = pd.read_excel(path)
    source_map = {col: get_bdnb_source_table(df, col) for col in columns}
    return source_map


def create_second_source_map():
    """
    Creates a map between a column name (for which we have extracted and merged
    a second source and) the name of the second source.

    Parameters:
        None

    Returns:
        second_source_map: dict[str, str]
            mapping between BDNB table and second source.
    """
    path = Path(data_path["selection"], "data_tables.xlsx")
    df = pd.read_excel(path)
    columns = df.loc[
        ~df["Colonne ADEME"].isna() | ~df["Colonne BDTOPO"].isna()
    ]["Colonne"].to_list()
    second_source_map = {
        col: get_second_source_label(df, col) for col in columns
    }
    return second_source_map
