import fiona
import pandas as pd
from pathlib import Path
from buildingdata import data_path
from buildingdata.logger import logger
from buildingdata.io.selection import load_bdtopo_selection
from buildingdata.io.converted import write_converted_data
from .utils import add_bdnb_id, normalize_bdtopo_data, create_roof_map


def get_roof_name(df: pd.DataFrame) -> pd.DataFrame:
    """
    Getter function to create and access the mapping between number values
    extracted from the BDTOPO and their corresponding name.

    Parameters:
        df: pd.DataFrame
            Dataframe containing the column where the roof_map should be
            applied.

    Returns:
        df: pd.DataFrame
            The modified dataframe.
    """
    roof_mapping = create_roof_map()
    df["MAT_TOITS"] = df["MAT_TOITS"].map(lambda x: roof_mapping[x])
    return df


def convert_bdtopo_columms(columns: list[str], table: str) -> list[list[str]]:
    """
    Extracts relevant columns wanted from a given BDTOPO table file. Opens the
    shapefile with fiona and reads in the records. Appends the records present
    in the columns argument to a result list.

    Parameters:
        colums: list
            List of names of properties stored in BDTOPO shapefile to be
            extracted.
        departement: int | str
            Departement number used to create the filename. Specific case for
            departements 1 and 3 where it is previously converted to a string
            for formatting issues: 1 -> "01", 3 -> "03"

    Returns:
        data: list[list]
            List containing a list of the extracted data for all entries in the
            shapefile being treated. Used for dataframe creation later.

    """
    logger.info(f"Converting BDTOPO data: table {table}")
    data = []
    path = Path(data_path["bdtopo extracted"], f"{table}/extracted.shp")
    with fiona.open(path, "r") as src:
        for record in src:
            properties = record["properties"]
            res = [properties["ID"]]
            for column in columns:
                res.append(properties[column])
            data.append(res)
    return data


def convert_bdtopo_data() -> None:
    """
    Wrapper function to convert the BDTOPO data that has been previously
    extracted and keep only relevant features. The function assumes the
    extracted data is located in the data/extracted/bdtopo directory.
    It loads the features to be extracted using the load_bdtopo_selection
    from the io.selection module.
    It then creates a pandas dataframe containing the features as columns and
    the datapoints as rows, in order to save the data in .csv format.

    Parameters:
        None

    Returns:
        None

    """
    bdtopo_selection = load_bdtopo_selection(convert=True)
    data = []
    columns = list(bdtopo_selection.values())[0]
    for table in bdtopo_selection:
        data += convert_bdtopo_columms(columns, table)
    columns = ["bdtopo_id"] + columns
    df = pd.DataFrame(data, columns=columns)
    df = get_roof_name(df)
    df = add_bdnb_id(df, "bdtopo")
    df = normalize_bdtopo_data(df)
    logger.info("Sucessfully converted BDTOPO data to one csv file.")
    write_converted_data(df, "bdtopo")
