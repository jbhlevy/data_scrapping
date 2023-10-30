from buildingdata.logger import logger
from buildingdata.io.merged import load_merged_data
from buildingdata.io.ppt import load_template, write_presentation
from buildingdata.slides.picture_extractor import extract_ppt_pictures
from .utils import load_addresses, images_available


def generate_slides(
    addresses: list[str] | None = None, street_view: bool = False
):
    """
    Generates the building identity slides for a given list of addresses. If
    the argument is None, the generation will be made over all available
    addresses.

    Parameters:
        addresses: list[str] | None, default None, optional
        List of addresses for which slides should be generated.

        street_view: bool, default False, optional
            Boolean to indicate which template to load between the regular and
            streetview one.
    """
    df = load_merged_data()
    df = df.iloc[df.isnull().sum(1).sort_values(ascending=1).index]
    df = df.reset_index()

    df = df.fillna("MISSING")
    if addresses is None:
        addresses = load_addresses(df)
    presentation = load_template(df, street_view)
    if not images_available():
        extract_ppt_pictures()

    if street_view:
        presentation.generate_slides_v1(addresses)
        write_presentation(
            presentation.prs, "vignettes_batiment_street_view.pptx"
        )
    else:
        presentation.generate_slides_v0(addresses)
        write_presentation(
            presentation.prs, "vignettes_batiment_no_street_view.pptx"
        )
    logger.info("Finished Generating slides")
