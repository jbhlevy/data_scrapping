import pandas as pd
from buildingdata.extractor.bdnb import extract_data as extract_bdnb
from buildingdata.extractor.bdtopo import extract_data as extract_bdtopo
from buildingdata.extractor.ademe import extract_data as extract_ademe
from buildingdata.convert.bdnb import convert_bdnb_data
from buildingdata.convert.bdtopo import convert_bdtopo_data
from buildingdata.convert.ademe import convert_ademe_data
from buildingdata.convert.nexity import convert_nexity_data
from buildingdata.io.converted import cleanup_converted_dir
from buildingdata.io.ids import load_all_ids
from buildingdata.io.merged import load_merged_data, write_columns
from buildingdata.maps.maps import add_streetview_availability
from buildingdata.merge.database import (
    merge_base_to_nexity,
    merge_base_to_bdtopo,
    merge_base_to_ademe,
)
from buildingdata.merge.merge import merge_all_data, merge_diagnostics
from buildingdata.slides.generator import generate_slides
from .utils import (
    add_dpe_flag,
    write_diagnostic,
    run_diagnostic_converted_data,
)

# -----------------------------------------------------------------------------
# EXTRACTION
# -----------------------------------------------------------------------------


def run_bdnb_extraction(bdnb_ids: pd.DataFrame) -> None:
    """
    Runs extraction on the BDNB database.

    Parameters:
        bdnb_ids: pd.DataFrame
            Dataframe containing the mapping between ids and addresses.

    Returns:
        None
    """
    ids_list = bdnb_ids["id"].to_list()
    extract_bdnb(ids_list)


def run_bdtopo_extraction(bdtopo_ids: pd.DataFrame) -> None:
    """
    Runs extraction on the BDTOPO database.

    Parameters:
        bdtopo_ids: pd.DataFrame
            Dataframe containing the mapping between ids and addresses.

    Returns:
        None
    """
    extract_bdtopo(bdtopo_ids)


def run_ademe_extraction(ademe_ids: pd.DataFrame) -> None:
    """
    Runs extraction on the ADEME database.

    Parameters:
        ademe_ids: pd.DataFrame
            Dataframe containing the mapping between ids and addresses.

    Returns:
        None
    """
    ids_list = ademe_ids["dpe_id"].to_list()
    extract_ademe(ids_list)


def run_all_extractions() -> None:
    """
    Runs the extraction for all the available databases, that is:
    - BDNB
    - BDTOPO
    - ADEME

    Parameters:
        None

    Returns:
        None

    """
    bdnb_ids, bdtopo_ids, ademe_ids = load_all_ids()
    run_bdnb_extraction(bdnb_ids)
    run_bdtopo_extraction(bdtopo_ids)
    run_ademe_extraction(ademe_ids)


# -----------------------------------------------------------------------------
# CONVERSION
# -----------------------------------------------------------------------------


def run_bdnb_conversion() -> None:
    """
    Converts BDNB data to personalised structure and computes the volume of
    data presence.

    Parameters:
        None

    Returns:
        None
    """
    convert_bdnb_data()
    run_diagnostic_bdnb()


def run_bdtopo_conversion() -> None:
    """
    Converts BDTOPO data to personalised structure and computes the volume of
    data presence.

    Parameters:
        None

    Returns:
        None
    """
    convert_bdtopo_data()
    run_diagnostic_bdtopo()


def run_ademe_conversion() -> None:
    """
    Converts ADEME data to personalised structure and computes the volume of
    data presence.

    Parameters:
        None

    Returns:
        None
    """
    convert_ademe_data()
    run_diagnostic_ademe()


def run_nexity_conversion():
    """
    Converts Nexity data to personalised structure.

    Parameters:
        None

    Returns:
        None
    """
    convert_nexity_data()


def run_all_conversions() -> None:
    """
    Runs conversions for all databases

    Parameters:
        None

    Returns:
        None
    """
    cleanup_converted_dir()
    run_bdnb_conversion()
    run_bdtopo_conversion()
    run_ademe_conversion()
    run_nexity_conversion()


# -----------------------------------------------------------------------------
# MERGING
# -----------------------------------------------------------------------------


def merge_all_databases() -> None:
    """
    Merges data (duplicates, missing values, etc.) in each database before
    merging all sources into ones

    Parameters:
        None

    Returns:
        None
    """
    merge_base_to_nexity()
    merge_base_to_bdtopo()
    merge_base_to_ademe()
    merge_all_data()


# -----------------------------------------------------------------------------
# DIAGNOSTICS
# -----------------------------------------------------------------------------


def run_diagnostic_bdnb() -> None:
    """
    Runs the diagnostic on data presence extracted from the BDNB.

    Parameters:
        None

    Returns:
        None
    """
    run_diagnostic_converted_data("bdnb")


def run_diagnostic_bdtopo() -> None:
    """
    Runs the diagnostic on data presence extracted from the BDTOPO.

    Parameters:
        None

    Returns:
        None
    """
    run_diagnostic_converted_data("bdtopo")


def run_diagnostic_ademe() -> None:
    """
    Runs the diagnostic on data presence extracted from the ADEME.

    Parameters:
        None

    Returns:
        None
    """
    run_diagnostic_converted_data("ademe")


def run_diagnostic_final_db() -> None:
    """
    Runs the diagnostic on data presence after the merging of all databases.
    """
    df = load_merged_data()
    write_diagnostic(df, "final_diagnostic")


# -----------------------------------------------------------------------------
# GET COLUMNS
# -----------------------------------------------------------------------------


def get_columns(cols: list[str], name: str):
    """
    Getter function to extracted specific columns from the recolted data.

    Parameters:
        cols: list[str]
            Name of the columns to be extracted.
        name: str
            Name of the csv file where to save the columns (the file will be
            located in the data/merged folder).

    Returns:
        None
    """
    cols += ["addresse", "batiment_groupe_id"]
    df = load_merged_data()
    columns = [col for col in df.columns if col[1] in cols]
    df = df[columns]
    write_columns(df, name)


# -----------------------------------------------------------------------------
# MAIN PIPELINE
# -----------------------------------------------------------------------------


def main(street_view: bool = False) -> None:
    run_all_extractions()
    run_all_conversions()
    merge_all_databases()
    run_diagnostic_final_db()
    merge_diagnostics()
    add_streetview_availability()
    add_dpe_flag()
    generate_slides(street_view=street_view)


if __name__ == "__main__":
    main()
