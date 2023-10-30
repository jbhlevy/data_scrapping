import pandas as pd
import numpy as np
from buildingdata.io.converted import load_frames_columns
from buildingdata.io.selection import load_tables_names
from buildingdata.logger import logger
from buildingdata.io.ids import load_ids
from buildingdata.io.selection import (
    create_source_map,
    create_second_source_map,
)
from .utils import (
    create_table_columns,
    format_data,
    format_toiture,
    format_vitrage,
    merge_rows,
)
from buildingdata.io.merged import write_merged_data
from buildingdata.io.diagnostics import (
    read_diagnostic,
    write_diagnostic_data,
    clean_diagnostics,
)


def get_percentage(table: str, column: str) -> float:
    """
    Gets the percentage of data present in a source database by reading the
    diagnostic previously perfomed on this database.

    Parameters:
        table: str
            Table of the source databse from which the column has been
            extracted.
        column: str
            Name of the column for which the percentage is being acquired.

    Returns:
        perc: float
            Percentage of data pressence of <column> in <table>

    """
    source_percentage = read_diagnostic(f"quality_{table}_data")
    perc = source_percentage.loc[source_percentage["column"] == column][
        "perc"
    ].values[0]
    return perc


def merge_diagnostics():
    """
    Merge all diagnostics to display the presence in the final collected
    database, and the presence in each source base.
    Loads the diagnostic data and retrieves the availibility of each source to
    merge them. Writes the newly made diagnostic in the same excel file.

    Parameters:
        None

    Returns:
        None
    """
    logger.info("Merging diagnostic into single spreadsheet.")
    df = read_diagnostic("final_diagnostic")
    tables, columns = (
        df["tables"].to_list()[2:],
        df["columns"].to_list()[2:],
    )
    bdnb_mapping = create_source_map(columns)
    second_source_mapping = create_second_source_map()
    sources_1, source_2 = [np.NaN for _ in range(2)], [
        np.NaN for _ in range(2)
    ]
    source_1_percentages, source_2_percentages = [np.NaN for _ in range(2)], [
        np.NaN for _ in range(2)
    ]
    current_table = tables[0]
    for table, column in zip(tables, columns):
        if isinstance(table, str):
            current_table = table
        source_table = bdnb_mapping[column]
        sources_1.append(source_table)
        source_1_percentages.append(get_percentage(current_table, column))
        if column in second_source_mapping.keys():
            source_table, source_column = second_source_mapping[column]
            source_2.append(source_table)
            source_2_percentages.append(
                get_percentage(source_table, source_column)
            )
        else:
            source_2.append(np.NaN)
            source_2_percentages.append(np.NaN)
    df["Source 1"] = sources_1
    df["Dispo source 1"] = source_1_percentages
    df["Source 2"] = source_2
    df["Dispo source 2"] = source_2_percentages
    df = df.reset_index(drop=True)
    logger.info("Sucessfully merged diagnostic into single spreadsheet.")
    write_diagnostic_data(df, "final_diagnostic", False)
    clean_diagnostics()


# -----------------------------------------------------------------------------


def create_index(tables: list[str], columns: list[list[str]]) -> pd.MultiIndex:
    """
    Creates a multi-index object used for pandas indexing using the table names
    and the names of their respective columns.

    Parameters:
        tables: list[str]
            List of table names to be merged.
        columns: list[list[str]]
            List of list containing the columns of each tables (there are as
            many lists as there are tables).

    Returns:
        index: pd.MultiIndex
            Multi-index pandas object usedd for dataframe column indexing.
    """
    logger.info("Creating pandas multi-index.")
    arrays = [[], []]
    for table, table_cols in zip(tables, columns):
        for column in table_cols:
            arrays[0].append(table)
            arrays[1].append(column)

    tuples = list(zip(*arrays))

    index = pd.MultiIndex.from_tuples(tuples, names=["table", "column"])
    return index


def create_data_dic(
    frame: pd.DataFrame,
    ids: list,
    data: dict[str, list],
) -> dict[str, list]:
    """
    Adds to the data dictionnary the data values of the current dataframe being
    treates. Adds the list of value if the id is present in the dataframe,
    otherwise adds MISSING values.

    Parameters:
        frame: pd.DataFrame
            Dataframe object being treated to be merged with others.
        ids: list
            List of the ids corresponding to the addresses being treated.
        data: dict[str, list]:
            Dictionnary mapping each id to a list corresponding to its row in
            the merged dataframe.

    Returns:
        data: dict[str, list]
            Dictionnary containing the newly added data values from the input
            dataframe for each id.
    """
    for _id in ids:
        if _id in frame.index:
            data[_id] += list(frame.loc[_id].to_dict().values())
        else:
            data[_id] += ["MISSING" for _ in range(frame.shape[1])]
    return data


def add_addresse(ids: list, data: dict, dic_ids: dict) -> dict[str, list]:
    """
    Adds to the data dictionnary the addresse corresponding to each id so that
    the address is part of the first table called "ID".

    Parameters:
        ids: list
            List of the ids corresponding to the addresses being treated.
        data: dict[str, list]
            Dictionnary mapping each id to a list corresponding to its row in
            the merged dataframe.
        dic_ids: dict
            Dictionnary containing the mapping between id and addresses.

    Returns:
        data: dict[str, list]
            Dictionnary containing the newly added address values from the
            input id <=> address mapping.
    """
    for _id in ids:
        data[_id] = [dic_ids[_id]] + data[_id]
    return data


def merge_same_address(df: pd.DataFrame) -> pd.DataFrame:
    """
    Merges the rows of the final dataframe that concern similar addresses.
    Multiple rows were kept during data extraction to gather as much data as
    possible. They are merged by keeping the row with the least amount of
    missing values.

    Parameters:
        df: pd.DataFrame
            Dataframe for which rows containing the same addresse value have to
            be merged.

    Returns:
        df: pd.DatFrame
            The resulting merged dataframe.

    Note
    ====
    A future strategy would be to merge them column by column to keep as much
    data as possible.
    """
    logger.info("Merging duplicates addresses.")
    df = df.replace("MISSING", np.NaN)
    duplicates = df[df.duplicated(subset=("ID", "addresse"), keep=False)]
    addresses = duplicates.drop_duplicates(("ID", "addresse"))[
        ("ID", "addresse")
    ].to_list()
    for addr in addresses:
        rows = duplicates.loc[duplicates[("ID", "addresse")] == addr]
        df = merge_rows(rows, df)
    return df


def format_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies some formatting to the dataframe to obtain nice and clean values
    using helper functions defined in the utils.py file.

    Parameters:
        df: pd.DataFrame
            Dataframe to be formated.

    Returns:
        df: pd.DataFrame
            Formated dataframe.

    """
    logger.info("Formatting dataframe.")
    df = df.replace(np.NaN, "MISSING")
    df = df.astype(str)
    df = df.applymap(format_data)
    df[("5.Donnees_menuiseries", "traitement vitrage")] = df[
        ("5.Donnees_menuiseries", "traitement vitrage")
    ].map(format_vitrage)
    df[("5.Donnees_menuiseries", "materiaux toiture")] = df[
        ("5.Donnees_menuiseries", "materiaux toiture")
    ].map(format_toiture)
    return df


def merge_all_data() -> None:
    """
    Merges table contained in all the tables of the data/converted directory
    into one dataframe and exports the resulting frame to the data/merged
    directory.
    Loads all the frames to be merged, creates the ulti-index used in the final
    frame, merged the data and finally writes the output.
    """
    logger.info("Merging all data into final structure.")
    bdnb_tables = load_tables_names()
    frames, columns = load_frames_columns(bdnb_tables)
    bdnb_tables, columns = create_table_columns(bdnb_tables, columns)
    index = create_index(bdnb_tables, columns)

    dic_ids = load_ids("bdnb").set_index("id")["addresse"].to_dict()
    ids = list(dic_ids.keys())

    data = {_id: [_id] for _id in ids}
    for frame in frames:
        data = create_data_dic(frame, ids, data)
    data = add_addresse(ids, data, dic_ids)

    data_list = list(data.values())
    df = pd.DataFrame(data_list, columns=index)
    df = merge_same_address(df)
    df = df.reset_index(drop=True)
    df = format_dataframe(df)
    logger.info("Sucessfullty merged all data into final structure.")

    write_merged_data(df)
