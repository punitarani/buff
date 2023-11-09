"""buff/utils.py"""


def safe_filename(doi: str) -> str:
    """
    Creates a safe filename from the DOI.
    Replace characters that are not allowed in filenames.

    Args:
        doi (str): DOI of the paper

    Returns:
        str: Safe filename of the paper
    """
    return "".join(c if c.isalnum() else "_" for c in doi)
