import pandas as pd

def cast_columns_to_string(df: pd.DataFrame, columns: list):
    """
    Cast specified columns of a DataFrame to string type.

    Args:
        df (pd.DataFrame): The DataFrame to modify.
        columns (list): List of column names to cast to string.

    Returns:
        pd.DataFrame: The modified DataFrame with specified columns cast to string.
    """
    for col in columns:
        if col in df.columns:
            df[col] = df[col].astype(str)
    return df

def cast_columns_to_int(df: pd.DataFrame, columns: list):
    """
    Cast specified columns of a DataFrame to integer type.

    Args:
        df (pd.DataFrame): The DataFrame to modify.
        columns (list): List of column names to cast to integer.

    Returns:
        pd.DataFrame: The modified DataFrame with specified columns cast to integer.
    """
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
    return df