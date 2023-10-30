import logging
from buildingdata import log_dir


def create_logger():
    logger = logging.getLogger("Log")
    logger.setLevel(logging.INFO)
    log_dir.mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(log_dir / "main.log", mode="w")
    fmt = "%(asctime)s - %(name)s - {%(filename)s:%(lineno)d} - %(levelname)s\
 - %(message)s"
    formatter = logging.Formatter(fmt)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


logger = create_logger()
