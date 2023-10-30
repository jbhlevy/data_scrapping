import pandas as pd
import numpy as np
from buildingdata.io.merged import load_merged_data, write_merged_data
from buildingdata.logger import logger
from buildingdata.io.selection import load_tables_names
from buildingdata.io.converted import load_converted_data
from buildingdata.io.diagnostics import write_diagnostic_data


def write_diagnostic(df: pd.DataFrame, name: str) -> None:
    """
    Execute a diagnostic to evaluate the amount of data present after all data
    treatements.

    Parameters:
        df: pd.DataFrame
            Dataframe on which the diagnostic should be performed.
        name: str
            Name of the file where to write the results of the diagnostic.

    Returns:
        None
    """
    logger.info(f"Running diagnostic on {name}")
    diagnostic = (df.shape[0] - df.isnull().sum()) / df.shape[0]
    if name == "final_diagnostic":
        diagnostic.index.names = ["tables", "columns"]
    else:
        diagnostic.index.names = ["column"]
    diagnostic = diagnostic.rename("perc")
    write_diagnostic_data(diagnostic, name)


def run_diagnostic_converted_data(name: str) -> None:
    """
    Runs the diagnostic on tables extracted from a databse stored in the
    converted folder. Used when computing the data volume in source databases
    before merging them.

    Parameters:
        name: str
            Name of the data base on which to perform the diagnostic.

    Returns:
        None

    """
    if name == "bdnb":
        tables = load_tables_names()
        for table in tables:
            df = load_converted_data(table)
            df = df.replace("MISSING", np.NaN)
            write_diagnostic(df, f"quality_{table}_data")
    else:
        df = load_converted_data(name)
        df = df.replace("MISSING", np.NaN)
        write_diagnostic(df, f"quality_{name}_data")


def add_dpe_flag():
    """
    Helper function to create a mask columns where True means the DPE is from
    2012 and false means it is from 2021.

    Parameters:
        None

    Returns:
        None
    """
    df = load_merged_data()
    df = df.replace(np.NaN, "MISSING")
    df[("3.Donnees_systeme", "flag DPE 2012")] = df[
        ("3.Donnees_systeme", "classe DPE")
    ].apply(lambda x: True if "2012" in x else False)
    write_merged_data(df)
