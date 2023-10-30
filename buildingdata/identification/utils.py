import re
import pandas as pd
from unidecode import unidecode

from buildingdata.logger import logger


def clean_address(address: str) -> str:
    """
    Converts an address in string format to the representation matching the
    original input using regular expressions.

    Parameters:
        address: str
            Address to be converted in string format.

    Returns:
        cleaned_address: str
            The newly cleaned address.
    """
    cleaned_address = re.sub(r"\W+", " ", address)
    cleaned_address = unidecode(cleaned_address)
    return cleaned_address


def change_addresses(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts the BDNB addresses to the format of the original addresses trying
    to be matched using the clean_address function.

    Parameters:
        df: pd.DataFrame
            BDNB dataframe (table batiment_groupe_address) containing both the
            address and building id to be extracted.

    Returns:
        df: pd.DataFrame
            The modified BDND dataframe containing the newly standardised
            addresses.
    """
    df.dropna(inplace=True)
    df["libelle_adr_principale_ban"] = (
        df["libelle_adr_principale_ban"].apply(clean_address).str.lower()
    )
    return df


def extract_departement(string) -> str:
    """
    Extracts postal code from a string address using regular expressions.

    Parameters:
        string: str
            String representation of the address containing the postal code.

    Returns:
        match: str
            String representation of the postal code.

    """
    pattern = r"\b\d{5}\b"  # Matches 5 consecutive digits
    match = re.findall(pattern, string)[0]
    return match[:2]


def treat(address: str) -> list:
    """
    Treats an address in string format to extract the other addresses it refers
    to.
    To extract addresses we proceed as follows:
        Identify the index of the first comma.
        If it is at an arbitrarily large position (>10) we are in case two:
        Seperate the two lanes the address refers to.
        Otherwise, while there are commas in the address:
        Extract the numbers X, Y, Z seprated by the commas to a list.
        Create an address for each number and append it to the results list.

    Parameters:
        address: str
            Original address in format refering to multiple buildings.

    Returns;
        res: list
            List of addresses that have been extracted from the original
            address string.

    """
    res = []
    nums = []
    index = address.find(",")
    if index == -1:
        res = [address]

    if index >= 10:
        res.append(address[:index])
        res.append(address[index + 2 :])
    else:
        while index != -1:
            nums.append(address[:index] + " ")
            address = address[index + 1 :].strip()
            index = address.find(",")
            if index == -1:
                i = 0
                char = address[i]
                while char.isdigit():
                    i += 1
                    char = address[i]
                nums.append(address[: i + 1])
                address = address[i + 1 :].strip()
        for num in nums:
            res.append(num + address)

    return res


def treat_multiple(df: pd.DataFrame) -> pd.DataFrame:
    """
    Treates the case of MULTIPLE addresses according to the following patterns:
        If same lane: X, Y, Z,... <lane_name>
        If two lanes for same building group: X <lane_name_1>, 7 <lane_name_2>

    Parameters:
        df: pd.DataFrame
            Dataframe containing only addresses with status MULTIPLE

    Returns:
        df: pd.DataFrame
            Modified dataframe containing only GOOD addresses according to the
            rule explained above.
    """
    new_addresses = []
    logger.info(f"Treating multiple for {df.shape[0]} addresses")
    addresses = df["Adresse Correspondante BDNB"].to_list()
    for addr in addresses:
        new_addresses = treat(addr)
        row = df.loc[df["Adresse Correspondante BDNB"] == addr]
        if len(new_addresses) == 1:
            continue
        i = row.index
        df.drop(i)
        for new_addr in new_addresses:
            df = pd.concat([df, row])
            df.loc[
                df["Adresse Correspondante BDNB"] == addr,
                "Adresse Correspondante BDNB",
            ] = new_addr
    logger.info(f"New size of multiple df: {df.shape[0]}")
    return df
