import pandas as pd
from buildingdata.io.source import load_bdnb_data
from .utils import change_addresses, extract_departement


def create_bdnb_ids(addresses: list[str]) -> pd.DataFrame:
    """
    Creates mapping between input addresses and BDNB ids. Loads the relevant
    table from the BDNB, convert the addresses to match the input format of
    strings and extract the ids corresponding to the addresses in a pandas
    dataframe.Examines if some addresses point to multiple or empty rows.

    Parameters:
        addresses: list[str]
            The list of original addresses to be matched with building id.

    Returns:
        df: pd.Dataframe
            Dataframe containing addresse and ids columns.

    """
    df = load_bdnb_data(
        table="batiment_groupe_adresse.csv",
        columns=["libelle_adr_principale_ban", "batiment_groupe_id"],
    )
    if isinstance(df, pd.DataFrame):
        pass
        # Logger info here
    df = change_addresses(df)
    df = df.drop_duplicates()
    df = df.loc[df["libelle_adr_principale_ban"].isin(addresses)]
    # Add a checker for missing values, send info to logger
    new_names = {
        "libelle_adr_principale_ban": "addresse",
        "batiment_groupe_id": "id",
    }
    df = df.rename(columns=new_names)
    return df


def create_departement_indexed_ids(
        ids_addr: dict[str, str],
        table: str,
        cols: list[str]
) -> pd.DataFrame:
    """
    Creates a mapping between input BDNB ids and another database organised in
    by departements. Loads the relevanat table from thr BDNB, extracts the
    corresponding ids in a pandas dataframe, as well as addresses and
    departement number, used to access the new database data in the extractor.
    Examines if some addresses point to multiple or empty rows.

    Parameters:
        ids_addr: dict[str, str]
            Dictionnary representation of the BDNB ids dataframe.
        table: str
            Name of the BDNB table where the relation between database ids can
            be found.
        cols: list[str]
            Names of the columns to be extracted: batiment_groupe_id
            <other_database_id>.

    Returns:
        df: pd.DataFrame
            Dataframe containing addresse, BDNB ids, other database ids and
            departement columns.

    """
    ids = list(ids_addr.keys())
    df = load_bdnb_data(table, cols)
    df = df.loc[df["batiment_groupe_id"].isin(ids)][cols]
    # Add a checker for missing values, send info to logger
    for _id, addr in ids_addr.items():
        df.loc[df["batiment_groupe_id"] == _id, "addresse"] = addr
        df.loc[
            df["batiment_groupe_id"] == _id, "departement"
        ] = extract_departement(addr)
    return df


def create_bdtopo_ids(ids_addr: dict[str, str]) -> pd.DataFrame:
    """
    Wrapper function to create BDTOPO ids, calls the generic function to make
    departement indexd ids.

    Parameters:
        ids_addr: dict[str, str]
            Dictionnary representation of the BDNB ids dataframe.

    Returns:
        df: pd.Dataframe
            Dataframe containing addresse, BDNB ids, BDTOPO ids and departement
            columns.

    """
    df = create_departement_indexed_ids(
        ids_addr,
        "rel_batiment_groupe_bdtopo_bat.csv",
        ["batiment_groupe_id", "bdtopo_bat_cleabs"]
    )
    new_names = {"batiment_groupe_id": "id"}
    df = df.rename(columns=new_names)
    return df


def create_ademe_ids(ids_addr: list[str]) -> pd.DataFrame:
    """
    Wrapper function to create ADEME ids, calls the generic function to make
    departement indexd ids.

    Parameters:
        ids_addr: dict[str, str]
            Dictionnary representation of the BDNB ids dataframe.

    Returns:
        df: pd.Dataframe
            Dataframe containing addresse, BDNB ids, ADEME ids and departement
            columns.

    """
    df = create_departement_indexed_ids(
        ids_addr,
        "batiment_groupe_dpe_representatif_logement.csv",
        ["batiment_groupe_id", "identifiant_dpe"]
    )
    new_names = {"batiment_groupe_id": "id", "identifiant_dpe": "dpe_id"}
    df = df.rename(columns=new_names)

    return df
