"""scripts/get_downloaded_work_ids.py"""

import json

import pandas as pd

from config import DATA_DIR, PAPERS_DIR

PAPERS_TXT_DIR = PAPERS_DIR.joinpath("txt")
WORKS_FP = DATA_DIR.joinpath("works.json")
NAMES_FP = DATA_DIR.joinpath("sanitized_names.csv")


def load_data():
    """
    Load the works and names data from JSON and CSV files.

    Returns:
        tuple: A tuple containing the works DataFrame and names DataFrame.
    """
    with open(WORKS_FP, "r", encoding="utf-8") as f:
        works_dict = json.load(f)
        works_df = pd.DataFrame(works_dict.items(), columns=["work_id", "doi"])

    with open(NAMES_FP, "r", encoding="utf-8") as f:
        names_df = pd.read_csv(f)

    return works_df, names_df


def print_downloaded_work_ids(works_df: pd.DataFrame, names_df: pd.DataFrame):
    """
    Print the work IDs of the downloaded files.

    Args:
        works_df (DataFrame): The DataFrame containing the works data.
        names_df (DataFrame): The DataFrame containing the sanitized names data.
    """
    if not PAPERS_TXT_DIR.exists():
        print("The 'txt' directory does not exist.")
        return

    txt_files = PAPERS_TXT_DIR.glob("*.txt")
    work_ids = [file.stem for file in txt_files]

    if len(work_ids) == 0:
        print("No downloaded work IDs found.")
    else:
        print("Downloaded work IDs:")
        for work_id in work_ids:
            doi = names_df[names_df.columns[0]][names_df[names_df.columns[1]] == work_id].values[0]
            wid = works_df[works_df["doi"] == doi]["work_id"].values[0]
            print(wid)


if __name__ == "__main__":
    _works_df, _names_df = load_data()
    print_downloaded_work_ids(_works_df, _names_df)
