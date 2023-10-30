import pandas as pd
from buildingdata.io.source import load_bdnb_data


def create_ids_proprietaire() -> dict[str, str]:
    """
    Creates the proprietaire id -> building id mapping. Reads in the
    relationship table and creates the corresponding dictionnary.

    Parameters:
        None

    Returns:
        res: dict
            Dictionnary mapping proprietaire id to building id.

    """
    df = load_bdnb_data(
        table="rel_batiment_groupe_proprietaire.csv",
        columns=["batiment_groupe_id", "personne_id"]
    )
    res = df.set_index("personne_id").to_dict()["batiment_groupe_id"]
    return res


def add_id_col(
    file_df: pd.DataFrame, keys_id: dict,
) -> pd.DataFrame:
    """
    Adds the batiment_groupe_id column to a Dataframe.

    Parameters:
        file_df: pd.DataFrame
            Dataframe object to which we wish to add the id column.
        keys_ids: dict
            Dictionnary mapping an existing key in the table to the building
            id.

    Returns:
        df: pd.DataFrame
            Newly maded dataframe containing the added id column.
    """

    df = pd.DataFrame()
    file_df["batiment_groupe_id"] = file_df["personne_id"].map(keys_id)
    df = pd.concat([df, file_df])
    return df


def setup_proprietaire(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds building ids to the proprietaire table of the BDNBD databse.
    First the function calls the create_ids_proprietaire() function to obtain
    a mapping towards the building ids. Then it adds them to the table.

    Parameters:
        df: pd.DataFrame
            Dataframe containing the proprietaire table of the BDNB

    Returns:
        df: pd.DataFrame
            Modified dataframe now containing the building id corresponding to
            each line.
    """
    prop_ids = create_ids_proprietaire()
    df = add_id_col(df, prop_ids)
    assert "batiment_groupe_id" in df.columns
    return df
