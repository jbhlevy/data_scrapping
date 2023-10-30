from buildingdata.io.converted import load_converted_data, write_converted_data
from buildingdata.io.selection import create_merge_map
from buildingdata.merge.conversion import merge_columns
from buildingdata.logger import logger


def merge_second_source_to_base(name: str) -> None:
    """
    Wrapper function to merge BDNB and other data. Use the create_merge_map()
    from the .utils file to select columns to be compared.

    Parameters:
        name: str
            Name of the second database to be merged.

    Returns:
        None
    """
    logger.info(f"Merging {name} to BDNB data.")
    merge_map = create_merge_map(name)
    to_merge_df = load_converted_data(name)
    for to_merge_col, (table, column) in merge_map.items():
        df = load_converted_data(table)
        data_to_merge = to_merge_df[to_merge_col]
        df = merge_columns(df, column, data_to_merge)
        write_converted_data(df, table)
    logger.info(f"Sucessfully merged {name} to BDNB data.")


def merge_base_to_nexity():
    """
    Wrapper function to merge nexity data.

    Parameters:
        None

    Returns:
        None
    """
    merge_second_source_to_base("nexity")


def merge_base_to_bdtopo():
    """
    Wrapper function to merge BDTOPO data.

    Parameters:
        None

    Returns:
        None
    """
    merge_second_source_to_base("bdtopo")


def merge_base_to_ademe():
    """
    Wrapper function to merge ADEME data.

    Parameters:
        None

    Returns:
        None
    """
    merge_second_source_to_base("ademe")
