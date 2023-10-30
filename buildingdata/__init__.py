from pkg_resources import resource_filename
from pathlib import Path

data_path = {
    "bdnb source": resource_filename("buildingdata", "data/source/bdnb"),
    "bdnb extracted": resource_filename("buildingdata", "data/extracted/bdnb"),
    "bdtopo source": resource_filename("buildingdata", "data/source/bdtopo"),
    "bdtopo extracted": resource_filename(
        "buildingdata", "data/extracted/bdtopo"
    ),
    "ademe source": resource_filename("buildingdata", "data/source/ademe"),
    "ademe extracted": resource_filename(
        "buildingdata", "data/extracted/ademe"
    ),
    "selection": resource_filename("buildingdata", "data/selection"),
    "converted": resource_filename("buildingdata", "data/converted"),
    "ppt": resource_filename("buildingdata", "data/ppt"),
    "ids": resource_filename("buildingdata", "data/ids"),
    "addresses": resource_filename("buildingdata", "data/source/addresses"),
    "utils": resource_filename("buildingdata", "data/utils"),
    "merged": resource_filename("buildingdata", "data/merged"),
    "diagnostics": resource_filename("buildingdata", "data/diagnostics"),
    "images": resource_filename("buildingdata", "data/ppt/images"),
    "maps": resource_filename("buildingdata", "data/source/maps"),
    "street_view": resource_filename("buildingdata", "data/ppt/images/sw"),
}

API_KEY = "ADD_API_KEY"

PATH_TO_ADDRESSES = Path(data_path["addresses"], "ENTER FILE NAME")

BASE_DIR = Path(__file__).parent.expanduser().resolve()
log_dir = BASE_DIR / "logs"
