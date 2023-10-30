from buildingdata.convert.utils import add_bdnb_id_nexity
from buildingdata.identification.addresses import expand_nexity
from buildingdata.io.source import load_address_data
from buildingdata.io.converted import write_converted_data
from buildingdata.logger import logger


def convert_nexity_data():
    """
    Converts nexity data to keep only the time of construction used to fill
    missing values when merging databases.
    Expands the multiple addresses present in the nexity data before extracting
    the relevant columns and writting the data in the data/converted folder.

    Parameters:
        None

    Returns:
        None
    """
    cols = [
        "Statut Adresse",
        "Adresse Correspondante BDNB",
        "Adresse Présente BDNB",
        "Période de construction",
    ]
    logger.info("Converting Nexity data.")
    nexity_df = load_address_data(cols)
    nexity_df = expand_nexity(nexity_df)
    nexity_df = add_bdnb_id_nexity(nexity_df)
    nexity_df = nexity_df.groupby(nexity_df.index).first()
    logger.info("Sucessfully converted Nexity data.")
    write_converted_data(nexity_df, "nexity")
