import pandas as pd
import numpy as np
from buildingdata.io.ids import load_ids
from buildingdata.io.utils import load_roof_map
from buildingdata.merge.utils import merge_rows


def add_bdnb_id(df: pd.DataFrame, name: str) -> pd.DataFrame:
    """
    Adds the BDNB id to the dataframe containing the extracted data for
    future cross reference.

    Parameters:
        df: pd.DataFrame
            Dataframe object containing the data extracted from the BDTOPO.
        name: str
            Name of the database for which the conversion needs to be done.

    Returns:
        df: pd.DataFrame
            Dataframe object containing the newly added id correspondance.
    """
    id_name = "bdtopo_bat_cleabs" if name == "bdtopo" else "dpe_id"
    df1 = load_ids(name)
    bdtopo_ids = df[f"{name}_id"].to_list()
    for _id in bdtopo_ids:
        df.loc[df[f"{name}_id"] == _id, "batiment_groupe_id"] = df1.loc[
            df1[id_name] == _id
        ]["id"].values[0]
    df = df.set_index("batiment_groupe_id")
    return df


def add_bdnb_id_nexity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds the BDNB id to the dataframe containing the Nexity data for
    future cross reference.

    Parameters:
        df: pd.DataFrame
            Dataframe object containing the data from Nexity.

    Returns:
        df: pd.DataFrame
            Dataframe object containing the newly added id correspondance.


    """
    df1 = load_ids("bdnb")
    nexity_addresses = df1["addresse"].to_list()
    for addr in nexity_addresses:
        df.loc[
            df["Adresse Correspondante BDNB"] == addr, "batiment_groupe_id"
        ] = df1.loc[df1["addresse"] == addr]["id"].values[0]
    df = df.set_index("batiment_groupe_id")
    return df


def normalize_data(df: pd.Series) -> pd.DataFrame:
    """
    Normalizes the data extracted from non BDNB tables to match the number of
    rows extracted from the BDNB by adding empty rows for non-matched ids.
    This way the computations of data volume are made on the same base which is
    the original number of ids matching in the BDNB.

    Parameters:
        df: pd.Series
            A column of the dataframe that is being normalised, to which NaN
            values are added for all ids not in the original mapping.

    Returns:
        df: pd.DataFrame
            Dataframe object created from the modified series, to be
            concatenated with the rest of the original database outside of this
            function.
    """
    ids = load_ids("bdnb")["id"].to_list()
    index = df.index
    missing_ids = [e for e in ids if e not in index]
    nan_values = [np.NaN for _ in missing_ids]
    missing_series = pd.Series(
        nan_values, index=missing_ids, name=df.name, dtype=float
    )
    df = pd.concat([df, missing_series])
    df.index.names = ["batiment_groupe_id"]
    return df


def normalize_bdtopo_data(df: pd.DataFrame):
    """
    Normalizes BDTOPO data tables to match the number of rows extracted from
    the BDNB by adding empty rows for non-matched ids and merging duplicates
    ids. This way the computations of data volume are made on the same base
    which is the original number of ids matching in the BDNB.

    Parameters:
        df: pd.DataFrame
            Dataframe containing the concatenated BDTOPO data to be normalized.

    Returns:
        df: pd.DataFrame
            Dataframe object normalized to have as many rows as original ids
            found in the BDNB.
    """
    ids = df.loc[df.index.duplicated(keep=False)].index.values
    df = df.reset_index()
    for _id in ids:
        rows = df.loc[df["batiment_groupe_id"] == _id]
        df = merge_rows(rows, df)
    df = df.set_index("batiment_groupe_id")
    return_df = pd.DataFrame()
    for col in df.columns:
        if col == "batiment_groupe_id":
            continue
        return_df = pd.concat([return_df, normalize_data(df[col])], axis=1)
    return_df.index.names = ["batiment_groupe_id"]
    return return_df


def create_roof_map() -> dict[str, str]:
    """
    Creates the maping between roof code and description obtainined from the
    documentation of the BDTOPO. The mapping is stored in a excel file. The
    function performs some formatting of the keys to ensure good matching.

    Parameters:
        None

    Returns:
        dict[str, str]
            Mapping between string representation of BDTOPO codes and their
            corresponding descritpion of roof materials.
    """
    excel = load_roof_map()
    excel = excel.astype(str)
    roof_mapping = excel.set_index("Code").to_dict()["Value"]
    roof_mapping = {
        f"{int(key):02d}": value for key, value in roof_mapping.items()
    }
    roof_mapping["00"] = "MISSING"
    roof_mapping[None] = "MISSING"
    return roof_mapping
