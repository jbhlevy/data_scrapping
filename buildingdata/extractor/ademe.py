import pandas as pd
from buildingdata.logger import logger
from buildingdata.io.source import load_ademe_data
from buildingdata.io.selection import load_ademe_selection
from buildingdata.io.extracted import write_ademe_data


def extract_table(
    tab: str, cols: list[str], ademe_ids: list[str]
) -> pd.DataFrame:
    """
    Extracts some data columns of a given ADEME table for the relevant
    addresses.
    Performs some checks in case of ids mismatch (if there is more/less lines
    in the dataframe corresponding to our ids). If it is the case, writes those
    ids to the logfile.

    Parameters:
        tab: str
            Departement number of the ADEME table to extract from.
        cols: list
            List of the columns in the ADEME table that need to be extracted.
        ademe_ids: list
            List of dpe ids to extract from ADEME database.

        Returns:
            df: pd.DataFrame
                Dataframe storing the extracted data
    """
    logger.info(f"Extracting ADEME data for departement {tab}")
    df = load_ademe_data(tab, cols)
    df = df.loc[df["numero_dpe"].isin(ademe_ids)]
    df = df.drop_duplicates(subset="numero_dpe")
    return df


def extract_data(ademe_ids: list[str]) -> None:
    """
    Wrapper function for ADEME data extraction. Loads the tables and columns to
    be extracted by calling load_ademe_selection of the io.selection module.
    Extracts the data columns in the selection for all the tables in the
    selection for all the addresses in building_ids.
    For each table writes the extracted data to a
    {table_name}/dpe_extracted.csv file.

    Parameters:
        ademe_ids: list
            List of dpe ids to extract from ADEME database.

    Returns:
        None

    """
    ademe_selection = load_ademe_selection()
    for tab, cols in ademe_selection.items():
        df = extract_table(tab, cols, ademe_ids)
        write_ademe_data(df, "dpe_extracted", tab)
        logger.info(f"Sucessfully extracted ADEME data for departement {tab}.")
