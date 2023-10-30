from pptx import Presentation
from buildingdata.io.ppt import load_solar_presentation, write_image
from buildingdata.identification.utils import clean_address


def get_addresse(title: str) -> str:
    """
    Gets the addresse from a title in the SolarProb presentation.

    Parameters:
        title: str
            Text present in the slide.

    Returns:
        res: str
            Address extracted from the text.

    """
    res = clean_address(title[title.find("ment") + 5 :]).lower()
    return res


def picture_names_generator(presentation: Presentation):
    """
    Yields the picture associated to an addresse using a generator.

    Parameters:
        presentation: pptx.Presentation object containing the relevant pictures

    Yields:
        shape, name: Tuple containing:
            0: image shape
            1: string representation of the address used as image name.
    """
    for slide in presentation.slides:
        name = "no_addresse"
        for shape in slide.shapes:
            if shape.name[-1] == "2":
                name = get_addresse(shape.text)

            if shape.name[-1] == "3":
                yield (shape, name)


def extract_ppt_pictures() -> None:
    """
    Wrapper function to extract pictures from SolarBot imagery presentation.

    Parameters:
        None

    Returns:
        None
    """
    prs = load_solar_presentation()
    for picture, name in picture_names_generator(prs):
        image = picture.image
        image_bytes = image.blob
        write_image(image_bytes, name)
