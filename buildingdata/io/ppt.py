import pandas as pd
from pptx import Presentation
from pathlib import Path
from buildingdata import data_path
from buildingdata.slides.PresentationChurn import PresentationChurn


def load_presentation(name: str) -> Presentation:
    """
    Loads a pptx Presentation from the data/ppt directory.

    Parameters:
        name: str
            Name of the presentation file to be loaded (with extension).

    Returns:
        prs: Presentation
            pptx.Presentation object.
    """
    path = Path(data_path["ppt"], f"source/{name}")
    prs = Presentation(path)
    return prs


def load_solar_presentation() -> Presentation:
    """
    Loads the SolarBot imagery presentation by calling the load_presentation
    function.

    Parameters:
        None

    Returns:
        None
    """
    return load_presentation("satellite_imagery_slides_nexity_second.pptx")


def load_template(
    df: pd.DataFrame, street_view: bool = False
) -> PresentationChurn:
    """
    Loads template ppt in personalised class used for slide generation.

    Parameters:
        df: pd.DataFrame
            Dataframe containing the building data that will be displayed in
            the slides.
        street_view: bool, default False, optional
            Boolean to indicate which template to load between the regular and
            streetview one.

    Returns:
        prs: PresentationChurn
            Presentation object inherited from pptx.Presentation used for slide
            generation.

    """
    if street_view:
        path = Path(data_path["ppt"], "source", "template_sw.pptx")
    else:
        path = Path(data_path["ppt"], "source", "template.pptx")
    prs = PresentationChurn(path, df)
    return prs


def write_presentation(prs: Presentation, name: str) -> None:
    """
    Write a presentation to the data/ppt directory.

    Parameters:
        prs: Presentation
            pptx.Presentation object to be saved.

    Returns:
        None

    """
    path = Path(data_path["ppt"], name)
    prs.save(path)


def write_image(image, name: str) -> None:
    """
    Write an image in blob (bytes) format to the data/ppt/image/solar directory
    . Used to extract satellites images from the SolarBot imagery presentation.
    Images are name with their address.

    Parameters:
        image: bytes
            Image extracted from a presentation to be saved.
        name: str
            Name to use when saving the file (address of the satellite image).

    Returns:
        None

    """
    path = Path(data_path["images"], f"solar/{name}.jpg")
    with open(path, "wb") as file:
        file.write(image)
