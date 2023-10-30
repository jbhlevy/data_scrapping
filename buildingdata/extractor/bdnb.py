import pandas as pd
from buildingdata.io.selection import load_bdnb_selection
from buildingdata.io.extracted import write_bdnb_data
from buildingdata.io.source import load_bdnb_data
from buildingdata.logger import logger
from .utils import setup_proprietaire


def extract_table(
    tab: str, cols: list[str], building_ids: list[str]
) -> pd.DataFrame:
    """
    Extracts some data columns of a given BDNB table for the relevant addresses
    . Performs some preprocessing regarding certain BDNB tables not containing
    the correct id.
    Performs some checks in case of ids mismatch (if there is more/less lines
    in the dataframe corresponding to our ids). If it is the case, writes those
    ids to the logfile.

    Parameters:
        tab: str
            Name of the BDNB table to extract from.
        cols: list
            List of the columns in the BDNB table that need to be extracted.
        building_ids: list
            List of building ids to extract from BDNB database.

        Returns:
            df: pd.DataFrame
                Dataframe storing the extracted data
    """
    df = load_bdnb_data(tab, cols)
    if "proprietaire" in tab:
        df = setup_proprietaire(df)
    if isinstance(df, pd.DataFrame):
        logger.info(f"Sucessfully loaded {tab}.")
    else:
        logger.error(f"Could not load {tab}: not a Dataframe.")
    df = df.loc[df["batiment_groupe_id"].isin(building_ids)]
    df = df.drop_duplicates(subset="batiment_groupe_id")
    logger.info(f"Sucessfully extracted data from {tab}")
    return df


def extract_data(building_ids: list[str]) -> None:
    """
    Wrapper function for BDNB data extraction. Loads the tables and columns to
    be extracted by calling load_bdnb_selection of the io.selection module.
    Extracts the data columns in the selection for all the tables in the
    selection for all the addresses in building_ids.
    For each table writes the extracted data to a extracted/{table_name}.csv
    file.

    Parameters:
        building_ids: list
            List of building ids to extract from BDNB database.

    Returns:
        None

    """
    bdnb_selection = load_bdnb_selection()
    for tab, cols in bdnb_selection.items():
        df = extract_table(tab, cols, building_ids)
        write_bdnb_data(df, tab)
    logger.info("Successfully extracted data from BDNB")
