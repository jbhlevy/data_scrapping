import google_streetview.api
import pandas as pd
from buildingdata.io.merged import load_merged_data, write_merged_data
from buildingdata import API_KEY, data_path
from pathlib import Path


def get_api_status(addr: str) -> tuple[str, str]:
    """
    Gets the availibility status and the link to download the streetview image
    for the input addresse by calling the google maps API.

    Parameters:
        addr: str
            Addresse for which the query will be made.

    Returns:
        status, link: tuple[str, str]
            Tuple containing the status and link obtained from the API call.


    """
    params = [{"size": "500x500", "location": addr, "key": API_KEY}]
    results = google_streetview.api.results(params)
    status, link = results.metadata[0]["status"], results.links[0]
    return status, link


def get_streetview_availability() -> None:
    """
    Gets the streetview data for all addresses in the database and stores it in
    a csv file.

    Parameters:
        None

    Returns:
        None

    """
    df = load_merged_data()
    addresses = df[("ID", "addresse")].to_list()
    status_link_list = [get_api_status(addr) for addr in addresses]
    status_link_tuple = ([], [])
    for couple in status_link_list:
        status_link_tuple[0].append(couple[0])
        status_link_tuple[1].append(couple[1])
    df = pd.DataFrame(
        data=list(zip(addresses, status_link_tuple[0], status_link_tuple[1])),
        columns=["addresse", "street_view status", "download_link"],
    )
    path = Path(data_path["maps"], "streetview_availability.csv")
    df.to_csv(path)


def add_streetview_availability() -> None:
    """
    Adds the streetview data to the merged database. Tries to read the csv file
    created by the get_streetview_availability() function and add columns to
    the database. Calls the said function if a FileNotFoundError is caught.

    Parameters:
        None

    Returns:
        None

    """
    df = load_merged_data()
    try:
        path = Path(data_path["maps"], "streetview_availability.csv")
        sw_df = pd.read_csv(path)
        df[("2.Donnees_general", "streetview status")] = sw_df[
            "street_view status"
        ]
        df[("street_view", "link")] = sw_df["download_link"]
        df = df.reset_index(drop=True)
        write_merged_data(df)
    except FileNotFoundError:
        get_streetview_availability()
        add_streetview_availability()


def query_image(addr: str) -> None:
    """
    Query the google maps streetview API to download the streetview image
    associated to the addr parameter. The function is only called if the image
    does not yet exist in the data/ppt/images/sw directory to avoid multiple
    calls for the same image.

    Parameters:
        addr: str
            Address for which streetview data is to be acquired.

    Returns:
        None
    """
    path = Path(data_path["street_view"] + f"/{addr}")
    params = [
        {
            "size": "500x500",
            "location": addr,
            "key": "AIzaSyAZMFl5AVClxzslrjrDUWY0yqQ32-0mqUo",
        }
    ]
    results = google_streetview.api.results(params)
    print("ATTENTION: Getting street view image...")
    results.preview()

    results.download_links(path)
