import fiona
import os
import pandas as pd
from pathlib import Path
from buildingdata import data_path
from buildingdata.logger import logger
from buildingdata.io.selection import load_bdtopo_selection


def extract_table(filename: Path, bdtopo_ids: list[str], table: str) -> None:
    """
    Extracts the BDTOPO records for a given list of ids in a given departement
    and stores them in a newly made shapefile. It iterates over the records
    present in the original BDTOPO shapefile and writes to the new file only
    the records that matches one of the input ids.

    Parameters:
        filename: Path
            Path to the original BDTOPO shapefile to extract the data from.
        bdtopo_ids: list[str]
            List of BDTOPO ids obtained from the BDNB database used to match
            the data to be extracted.
        table: str
            Table name, used to check if table directory exists and if not
            create it for the output files.

    Returns:
        None

    """
    logger.info(f"Extracting BDTOPO data for departement {table}")
    table_directory = Path(data_path["bdtopo extracted"], f"{table}")
    os.makedirs(table_directory, exist_ok=True)
    path = Path(table_directory, "extracted.shp")
    with fiona.open(filename, "r") as src:
        meta = src.meta
        with fiona.open(
            path,
            "w",
            **meta,
        ) as output:
            for record in src:
                if record["properties"]["ID"] in bdtopo_ids:
                    output.write(record)


def extract_departement_data(df: pd.DataFrame, table: str) -> None:
    """
    Extracts the BDTOPO records for a given departement. It creates the file
    path associated to this departement and calls the extract_table() function
    that performs the actual data extraction.

    Parameters:
        df: pd.DataFrame
            Dataframe object containing the corresponsance between addresses,
            BDNB ids and BDTOPO ids.
        table: str
            Name of the directory where the shapefile is located. Ued to
            create the filepath to the shapefile to be extracted.

    Returns:
        None

    """
    departement = int(table[table.rfind("_") + 1 :])
    local_df = df.loc[df["departement"] == departement]
    local_ids = local_df["bdtopo_bat_cleabs"].to_list()
    bdtopo_file = Path(data_path["bdtopo source"], f"{table}/BATIMENT.shp")
    extract_table(bdtopo_file, local_ids, table)


def extract_data(bdtopo_ids: pd.DataFrame) -> None:
    """
    Wrapper function for BDTOPO data extraction. Loads the relevant features to
    be extracted from BDTOPO files and extracts the data for all selected
    tables.

    Parameters:
        bdtopo_ids: pd.DataFrame
            Dataframe object containing the corresponsance between addresses,
            BDNB ids and BDTOPO ids.
    Returns:
        None

    """
    bdtopo_selection = load_bdtopo_selection()
    for table in list(bdtopo_selection.keys()):
        extract_departement_data(bdtopo_ids, table)
        logger.info(
            f"Sucessfully extracted BDTOPO data for departement {table}"
        )
