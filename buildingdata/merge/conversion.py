import pandas as pd

from buildingdata.merge.utils import add_data, check_presence_df, compare_data
from buildingdata.logger import logger


def merge_columns(
    df: pd.DataFrame,
    receiving_column: str,
    data_to_merge: pd.Series,
) -> pd.DataFrame:
    """
    Compare the data extracted from the BDNB to other source for specific
    columns to reduce the number of missing values.
    Depending on wether the data is present in one, both or none of the
    databases, either adds the data from the second column, writes an error log
    saying the data is inavailable, or comapres the values from both databases,
    writes an warning log if the values do not match.

    Parameters:
        df: pd.DataFrame
            Dataframe containing the data extracted from the BDNB.
        receiving_column: str
            Name of the column to receive new data.
        data_to_merge: pd.Series
            Series containing the data to be merged.

    Returns:
        df: pd.DataFrame
            The dataframe updated with second column values if possible.
    """
    count_added, count_both, count_different = 0, 0, 0
    for i, row in df.iterrows():
        in_df, value_df = check_presence_df(row[receiving_column])
        try:
            in_to_add_df, value_to_add_df = check_presence_df(
                data_to_merge.loc[i]
            )
        except KeyError:
            in_to_add_df, value_to_add_df = False, "MISSING"

        if not in_df and not in_to_add_df:
            continue

        elif not in_to_add_df and in_df:
            continue

        elif in_to_add_df and not in_df:
            df = add_data(df, i, receiving_column, value_to_add_df)
            count_added += 1

        elif in_to_add_df and in_df:
            count_both += 1
            count_different += compare_data(value_df, value_to_add_df)

    logger.info(
        f"For column {receiving_column}, added {count_added}\
 values from {data_to_merge.name}"
    )
    logger.info(
        f"For column {receiving_column},{count_different}\
 different values for {count_both} values in both databases"
    )
    logger.info(
        f"Sucessfully merged {data_to_merge.name} into {receiving_column}"
    )
    return df
