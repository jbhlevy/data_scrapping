import pandas as pd
from pathlib import Path
from buildingdata.logger import logger
from buildingdata import data_path
from buildingdata.identification.identification import (
    create_bdnb_ids,
    create_bdtopo_ids,
    create_ademe_ids,
)
from buildingdata.identification.addresses import load_addresses

creation_table = {
    "bdnb": create_bdnb_ids,
    "bdtopo": create_bdtopo_ids,
    "ademe": create_ademe_ids,
}


def write_ids(df: pd.DataFrame, name: str) -> None:
    """
    Writes ids data to the data/ids directory using df.to_csv without index.

    Parameters:
        df: pd.DataFrame
            Dataframe to be written.
        name: str
            Name of the output file (no extesntion).

    Returns:
        None

    """
    path = Path(data_path["ids"], f"{name}_ids.csv")
    df.to_csv(path, index=False)
    logger.info(f"Created id file for {name}")


def load_ids(name: str) -> pd.DataFrame:
    """
    Loads the ids used to access the database corresponding to the input name.
    Tries to read the ids from an existing file in the data/ids directory.
    Catches the error if the file doesn't exist, then creates and stored the
    correspondance for future calls.

    Parameters:
        name: str
            Name of the database for which ids have to be loaded.

    Returns:
        df: pd.DataFrame
            Dataframe containing the relevant id mapping.

    """
    path = Path(data_path["ids"], f"{name}_ids.csv")
    try:
        df = pd.read_csv(path)
        logger.info(f"{name} id file already exists. Skipped id creation")

    except FileNotFoundError:
        logger.info(
            f"{name} id file does not exist. Will proceed to id creation"
        )
        if name == "bdnb":
            addresses = load_addresses()
            df = create_bdnb_ids(addresses)
        else:
            df = load_ids("bdnb")
            if name == "bdtopo":
                ids_addr = df.set_index("id").to_dict()["addresse"]
                df = creation_table[name](ids_addr)
            if name == "ademe":
                ids_addr = df.set_index("id").to_dict()["addresse"]
                df = creation_table[name](ids_addr)
        write_ids(df, name)
    logger.info(f"Loaded {name} ids.")
    return df


def load_all_ids() -> list[pd.DataFrame]:
    """
    Wrapper function to load the ids map for all the databases used by the
    project by calling the load_ids function.

    Parameters:
        None

    Returns:
        frames: list[pd.DataFrame]
            List of the dataframes containing the ids map for all databases.

    """
    names = ["bdnb", "bdtopo", "ademe"]
    frames = [load_ids(name) for name in names]
    return frames
