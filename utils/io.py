"""Functions for saving and loading data in various formats."""

import json

def save_json(data, path: str) -> None:
    """
    Save data to a JSON file.

    Args:
        data (dict): Data to be saved.
        path (str): Path to the JSON file.

    Returns:
        None
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_json(path: str):
    """
    Load JSON data from a file.
    
    Args:
        path (str): Path to the JSON file.

    Returns:
        dict: Loaded JSON data.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def export_dataframe_to_csv(df, filename: str) -> None:
    """
    Export a pandas DataFrame to a CSV file.

    Args:
        df (pd.DataFrame): DataFrame to be exported.
        filename (str): Name of the output CSV file. Default is "flights_data.csv

    Returns:
        None
    """
    df.to_csv(filename, index=False, encoding="utf-8-sig")
