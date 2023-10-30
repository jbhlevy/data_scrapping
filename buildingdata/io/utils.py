import glob
import pandas as pd
from pathlib import Path
from buildingdata import data_path


def check_directory_content(name: str, tab_col_map: dict[str, list[str]]):
    """
    Checks the content of a directory against the keys of a table -> columns
    list map to avoid extracting the same table twice. If the table name is
    already present in the directory pop the entry from the map.

    Parameters:
        name: str
            Name of the direcrtory to be checked.
        table_col_map: dict[str, list[str]]
            Mapping between tables and the columns to be extracted from each
            table.

    Returns:
        table_col_map: dict[str, list[str]]
            Mapping between tables and the columns to be extracted from each
            table where tables that have already been extracted have been
            removed.

    """
    if "bdnb" in name:
        files = glob.glob(name + "/*.csv")
    else:
        files = glob.glob(name + "/*/")
    for tab in list(tab_col_map.keys()):
        for file in files:
            if tab in file:
                # Add read and check columns are the same...
                tab_col_map.pop(tab)
                break
    return tab_col_map


def load_roof_map() -> pd.DataFrame:
    """
    Loads from the data/utils directory the code to name map used by the
    BDTOPO for roof information using pd.read_excel.

    Parameters:
        None

    Returns:
        df: pd.DataFrame
            Dataframe containing the code to name of roof material mapping.
    """
    path = Path(data_path["utils"], "bdtopo_roof.xlsx")
    df = pd.read_excel(path)
    return df


def get_columns(df: pd.DataFrame, table: str) -> list[str]:
    """
    Getter function to set the names of columns used when creating the final
    database.

    Parameters:
        df: pd.DataFrame
            Dataframe containing the names of the columns and tables from which
            the data is extracted.
        table: str
            Name of the table for which we retrieve the columns.

    Returns:
        columns: list[str]
            List of column names for the corresponding table.

    """
    columns = df.loc[df["Table BDNB"] == table]["Colonne BDNB"].to_list()
    if table == "proprietaire":
        columns = ["personne_id"] + columns
    columns = ["batiment_groupe_id"] + columns

    return columns


def extract_table_name(table: str) -> str:
    """
    Extracts the table name from a file path and removes the .csv extension.

    Parameters:
        table: str
            Path to table.
    Returns:
        table: str
            Extracted table name.
    """
    index = table[:-2].rfind("\\")
    table = table[index + 1 : -1]
    return table


def get_new_table(df: pd.DataFrame, index: int) -> str:
    """
    Gets the name of the new table used in the get_new_label function.

    Parameters:
        df: pd.DataFrame
            Dataframe containing the names of the columns and tables from which
            the data is extracted.
        index: int
            Index of the row where data has to be extracted.

    Returns:
        label: str
            Name of the new table.
    """
    label = df.at[index, "Type de donnée"]
    if isinstance(label, float):
        return get_new_table(df, index - 1)
    return label


def get_new_column(df: pd.DataFrame, index: int) -> str:
    """
    Get the name of the new column used in the get_new_label function.

    Parameters:
        df: pd.DataFrame
            Dataframe containing the names of the columns and tables from which
            the data is extracted.
        index: int
            Index of the row where data has to be extracted.

    Returns:
        label: str
            Name of the new table.
    """
    label = df.at[index, "Colonne"]
    return label


def get_new_label(df: pd.DataFrame, column: str, name: str) -> tuple[str, str]:
    """
    Gets the new (table, columns) named for the merging map used in data
    conversion using the input arguments.

    Parameters:
        df: pd.DataFrame
            Dataframe containing the names of the columns and tables from which
            the data is extracted.
        column: str
            Name of the old column.
        name: str
            Name of the database from which the column has been extracted.

    Returns:
        res: tuple[str, str]
            Tuple containing the new (table name, column name).

    """
    index = df.loc[df[name] == column].index.values[0]
    res = (get_new_table(df, index), get_new_column(df, index))
    return res


def get_bdnb_source_table(df: pd.DataFrame, column: str) -> str:
    """
    Gets the source table a BDNB column.

    Parameters:
        df: pd.DataFrame
            Dataframe containing the names of the columns and tables from which
            the data is extracted.
        columns: str
            Name of the columns for which we find the table name.

    Returns:
        label: str
            Name of the BDNB source table.

    """
    label = df.loc[df["Colonne"] == column]["Table BDNB"].values[0]
    label = source_map[label]
    return label


def get_col(df: pd.DataFrame, column: str, name: str) -> str:
    """
    Gets the name of the second source column for a given BDNB column.

    Parameters:
        df: pd.DataFrame
            Dataframe containing the names of the columns and tables from which
            the data is extracted.
        column: str
            Name of the column to match.
        name: str
            Name of the second source.

    Returns:
        label: str
            Name of the column in the second source database corresponding to
            the column argument.
    """
    label = df.loc[df["Colonne"] == column][f"Colonne {name.upper()}"].values[
        0
    ]
    return label


def get_second_source_label(df: pd.DataFrame, column: str) -> tuple[str, str]:
    """
    Gets the label of the second source for a given column.

    Parameters:
        df: pd.DataFrame
            Dataframe containing the names of the columns and tables from which
            the data is extracted.
        column: str
            Name of the column to match.

    Returns:
        label: tuple[str, str]
            Tuple containing the name of the second source and the column name.
    """
    label = ("bdtopo", get_col(df, column, "bdtopo"))
    if isinstance(label[1], float):
        label = ("ademe", get_col(df, column, "ademe"))
    return label


def get_merge_ranges(df: pd.DataFrame) -> dict[tuple, str]:
    """
    Gets the ranges used to merge cells of same table title in the diagnostic
    summary excel.

    Parameters:
        df: pd.DataFrame
            Dataframe containing the diagnostic data.

    Returns:
        res: dict[tuple, str]
            Mapping between the ranges and name of cell used for merging the
            excel cells.
    """
    final_index = df.shape[0]
    df = df.dropna(subset="tables")["tables"]
    offset = 2
    res = []
    for i, (index, name) in enumerate(df.items()):
        start = index + offset
        if i + 1 >= len(df):
            end = final_index + offset - 1
        else:
            end = df.keys()[i + 1] + offset - 1
        res.append(((start, end), name))
    return res


source_map = {
    "batiment_construction": "IGN",
    "batiment_groupe": "INSEE",
    "batiment_groupe_merimee": "Base Mérimee",
    "batiment_groupe_logtype": "ADEME (arrêté 2012)",
    "batiment_groupe_dpe_representatif_logement": "ADEME",
    "batiment_groupe_ffo_bat": "Base des Fichiers Fonciers du CEREMA",
    "batiment_groupe_rnc": "Registre National des Copropriétés (RNC)",
    "proprietaire": "Base des Fichiers Fonciers du CEREMA",
}
