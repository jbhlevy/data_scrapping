import pandas as pd
from buildingdata.io.source import load_address_data
from .utils import treat_multiple


def expand_nexity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Expands the Nexity dataframe to remove multiple address and treat them as
    seperate rows. Relies on the treat_multiple function implemented in the
    utils module.

    Parameters:
        df: pd.DataFrame
            Nexity database, containing GOOD and MULTIPLE addresses.

    Returns:
        df: pd.DataFrame
            Concatenation of the GOOD database and the expanded MULTIPLE
            database.
    """
    multiple_df = df.loc[df["Statut Adresse"] == "MULTIPLE"]
    good_df = df.loc[df["Statut Adresse"] == "GOOD"]

    multiple_df = treat_multiple(multiple_df)

    df = pd.concat([good_df, multiple_df])
    df = df.drop_duplicates()

    return df


def load_addresses() -> list[str]:
    """
    Loads relevant Nexity addresses from a csv file. Performs checks on the
    addresse status (GOOD, MULTIPLE). If MULTIPLE, extracts the different
    addresses from the initial value so that each address corresponds to one
    line in the future id correspondance.

    Parameters:
        None

    Returns:
        res: list
            The list of addresses extracted from the original csv file.
    """
    cols = [
        "Statut Adresse",
        "Adresse Correspondante BDNB",
        "Adresse Présente BDNB",
    ]

    df = load_address_data(cols)
    df = expand_nexity(df)

    df.loc[df["Adresse Présente BDNB"] == "oui"]
    res = df["Adresse Correspondante BDNB"].to_list()

    return res
