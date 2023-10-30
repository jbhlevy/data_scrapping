import glob
import os
import pandas as pd
from buildingdata import data_path
from pathlib import Path

from buildingdata.io.utils import get_merge_ranges


def write_diagnostic_data(
    df: pd.DataFrame, name: str, index: bool = True
) -> None:
    """
    Writes the diagnosis data to the data/diagnostics directory using
    df.to_excel.
    Uses an ExcelWriter object to automatically handle the formating of the
    output data, that is setting numbers to percentages and applying a color
    scheme. The scheme is detailed below:

        x >= 75%: Dark Green
        65% <= x < 75%: Light Green
        50% <= x <65%: Dark Orange
        35% <= x < 50%: Light Orange
        25% < x < 35%: Light Red
        x <= 25%: Dark Red

    Parameters:
        df: pd.DataFrame
            Dataframe to be written.
        name: str
            Name of the output file (no extesntion).

    Returns:
        None

    """
    path = Path(data_path["diagnostics"], f"{name}.xlsx")
    df.to_excel(path, index=index)
    df = pd.read_excel(path)
    number_row = len(df.index) + 1
    writer = pd.ExcelWriter(path, "xlsxwriter")
    df.to_excel(writer, index=False, sheet_name="summary")
    workbook = writer.book
    worksheet = writer.sheets["summary"]
    percent_fmt = workbook.add_format({"num_format": "0%"})
    merge_fmt = workbook.add_format(
        {
            "bold": 1,
            "border": 2,
            "align": "center",
            "valign": "vcenter",
        }
    )

    if name == "final_diagnostic":
        worksheet.set_column("C:C", 12, percent_fmt)
        worksheet.set_column("E:E", 12, percent_fmt)
        worksheet.set_column("G:G", 12, percent_fmt)
        color_range = f"C2:C{number_row}"
        extension_range = f" E2:E{number_row} G2:G{number_row}"
        merge_ranges_names = get_merge_ranges(df)
        for (start, end), name in merge_ranges_names:
            worksheet.merge_range(f"A{start}:A{end}", name, merge_fmt)
    else:
        worksheet.set_column("B:B", 12, percent_fmt)
        color_range = f"B2:B{number_row}"
        extension_range = ""

    format1 = workbook.add_format({"bg_color": "#FF0000"})
    format2 = workbook.add_format(
        {"bg_color": "#FFC7CE", "font_color": "#9C0006"}
    )
    format3 = workbook.add_format(
        {"bg_color": "#FFEB9C", "font_color": "#9C5700"}
    )
    format4 = workbook.add_format({"bg_color": "#FF9933"})
    format5 = workbook.add_format(
        {"bg_color": "#C6EFCE", "font_color": "#006100"}
    )
    format6 = workbook.add_format({"bg_color": "#00B050"})
    format_blank = workbook.add_format({"bg_color": "#FFFFFF"})

    worksheet.conditional_format(
        color_range,
        {
            "type": "blanks",
            "format": format_blank,
            "multi_range": color_range + extension_range,
        },
    )

    worksheet.conditional_format(
        color_range,
        {
            "type": "cell",
            "criteria": ">=",
            "value": "0.75",
            "format": format6,
            "multi_range": color_range + extension_range,
        },
    )
    worksheet.conditional_format(
        color_range,
        {
            "type": "cell",
            "criteria": "between",
            "minimum": "0.65",
            "maximum": "0.75",
            "format": format5,
            "multi_range": color_range + extension_range,
        },
    )
    worksheet.conditional_format(
        color_range,
        {
            "type": "cell",
            "criteria": "between",
            "minimum": "0.5",
            "maximum": "0.65",
            "format": format4,
            "multi_range": color_range + extension_range,
        },
    )
    worksheet.conditional_format(
        color_range,
        {
            "type": "cell",
            "criteria": "between",
            "minimum": "0.35",
            "maximum": "0.5",
            "format": format3,
            "multi_range": color_range + extension_range,
        },
    )
    worksheet.conditional_format(
        color_range,
        {
            "type": "cell",
            "criteria": "between",
            "minimum": "0.25",
            "maximum": "0.35",
            "format": format2,
            "multi_range": color_range + extension_range,
        },
    )
    worksheet.conditional_format(
        color_range,
        {
            "type": "cell",
            "criteria": "<=",
            "value": "0.25",
            "format": format1,
            "multi_range": color_range + extension_range,
        },
    )
    writer.close()


def read_diagnostic(name: str) -> pd.DataFrame:
    """
    Reads in an Excel file containing the diagnostic data for a given table.

    Parameters:
        name: str
            Name of the diagnostic table to be loaded.

    Returns:
        df: pd.DataFrame
            Dataframe containing the loaded data.
    """
    path = Path(data_path["diagnostics"], f"{name}.xlsx")
    df = pd.read_excel(path)
    return df


def clean_diagnostics() -> None:
    """
    Cleans the diagnostic folder to remove unecessary spreadsheets after they
    have all been merged into one.

    Parameters:
        None

    Returns:
        None

    """
    files_to_remove = glob.glob(data_path["diagnostics"] + "/quality_*")
    for file in files_to_remove:
        os.remove(file)
