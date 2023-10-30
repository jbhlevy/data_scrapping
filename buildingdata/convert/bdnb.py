import glob
import pandas as pd
from buildingdata import data_path
from buildingdata.logger import logger
from buildingdata.convert.utils import normalize_data
from buildingdata.io.extracted import load_bdnb_data
from buildingdata.io.converted import load_converted_data, write_converted_data
from buildingdata.io.selection import create_database_mapping
from buildingdata.merge.conversion import merge_columns


def convert_bdnb_table(name: str, db_map: dict[tuple, tuple]) -> None:
    """
    Converts BDNB table to the structure defined in parameter db_map by copying
    the columns to new dataframes and saving/appending to newly named csv file.
    Normalizes the data to match the initial number of BDNB ids and to format
    some of the input data.

    Parameters:
        name: str
            Name of the extracted BDNB table to convert.
        db_map: dict[tuple, tuple]
            Mapping between current (bdnb_table, column) to new (column, table)
            name.

    Returns:
        None

    """
    df = load_bdnb_data(name)
    cols = df.columns.to_list()
    for col in cols:
        if col == "personne_id":
            continue
        if col == "mat_toit_txt":
            df = df.replace("INDETERMINE", "MISSING")
        if col == "classe_conso_energie_arrete_2012":
            df[col] = df[col].apply(
                lambda x: x + " (dpe 2012)" if isinstance(x, str) else x
            )
        if (name, col) not in db_map:
            logger.error(
                f"{(name, col)} not present in the mapping. Could not create\
 the corresponding columns in converted BDNB data."
            )
        new_tab, new_col = db_map[(name, col)]
        logger.info(f"Converting {name} to {new_tab}: {new_col}.")
        to_add_df = df[col]
        to_add_df.name = new_col
        try:
            table_df = load_converted_data(new_tab)
            if new_col in table_df.columns:
                table_df = merge_columns(table_df, new_col, to_add_df)
                write_converted_data(table_df, new_tab)
                continue
            table_df = pd.concat([table_df, to_add_df], axis=1)
            write_converted_data(table_df, new_tab)
        except FileNotFoundError:
            to_add_df = normalize_data(to_add_df)
            write_converted_data(to_add_df, new_tab)


def convert_bdnb_data() -> None:
    """
    Wrapper function to convert all the BDNB data that has been previously
    extracted. The function assumes the extracted data is located in the
    data/extracted/bdnb directory. It creates the mapping between databases
    structure using the create_database_ampping from the io.selection mdoule.
    It then selects all the extracted tables using glob and performs the
    conversion for each table.

    Parameters:
        None

    Returns:
        None

    """
    db_map = create_database_mapping()
    bdnb_files = glob.glob(data_path["bdnb extracted"] + "/*.csv")
    for file in bdnb_files:
        name_index = file.rfind("\\") + 1
        name = file[name_index:-4]
        convert_bdnb_table(name, db_map)
    logger.info("Sucessfully converted BDNB data.")
