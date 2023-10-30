import pandas as pd
from .utils import add_bdnb_id, normalize_data
from buildingdata.logger import logger
from buildingdata.io.extracted import load_ademe_data
from buildingdata.io.converted import write_converted_data
from buildingdata.io.selection import load_ademe_selection


def convert_ademe_data() -> None:
    """
    Wrapper function to convert the ADEME data that has been previously
    extracted in a single .csv file. The function assumes the
    extracted data is located in the data/extracted/ademe directory.
    It loads the features to be extracted using the load_ademe_selection
    from the io.selection module.
    It then creates a pandas dataframe containing the features as columns and
    the datapoints as rows, in order to save the data in .csv format.
    Normalizes the data to match the initial number of BDNB ids.

    Parameters:
        None

    Returns:
        None

    """
    logger.info("Converting ADEME data.")
    ademe_selection = load_ademe_selection(convert=True)
    columns = list(ademe_selection.values())[0]
    df = pd.DataFrame(columns=columns)
    for table in ademe_selection:
        table_df = load_ademe_data(table)
        df = pd.concat([df, table_df])
    id_map = {"numero_dpe": "ademe_id"}
    df = df.rename(columns=id_map)
    return_df = pd.DataFrame()
    df = add_bdnb_id(df, "ademe")
    for col in df.columns:
        if col == "batiment_groupe_id":
            continue
        return_df = pd.concat([return_df, normalize_data(df[col])], axis=1)
    return_df.index.names = ["batiment_groupe_id"]
    logger.info("Sucessfully converted ADEME data.")
    write_converted_data(return_df, "ademe")
