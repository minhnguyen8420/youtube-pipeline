import logging

from google.cloud import bigquery

logger = logging.getLogger(__name__)

def load_dataframe_to_bigquery(df, table_id, write_disposition="WRITE_APPEND"):
    """
    Loads a pandas DataFrame into a BigQuery table.

    Args:
        df (pd.DataFrame): The DataFrame to load.
        table_id (str): The BigQuery table ID in the format 'project.dataset.table'.
        write_disposition (str): Specifies the action that occurs if the destination table already exists. 
                                 Options are "WRITE_TRUNCATE", "WRITE_APPEND", or "WRITE_EMPTY". 
                                 Default is "WRITE_APPEND".
    """
    try:
        client = bigquery.Client()
        job_config = bigquery.LoadJobConfig(write_disposition=write_disposition)
        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()
        logger.info(f"Data loaded successfully into {table_id}.")
    except Exception as e:
        logger.error(f"An error occurred while loading data into BigQuery: {e}")

if __name__ == "__main__":
    # Example usage
    import pandas as pd

    # Create a sample DataFrame
    data = {
        "column1": [1, 2, 3],
        "column2": ["A", "B", "C"]
    }
    df = pd.DataFrame(data)

    # Specify your BigQuery table ID
    table_id = "focal-grin-255308.YOUTUBE_DATA.test_table"

    # Load the DataFrame into BigQuery
    load_dataframe_to_bigquery(df, table_id)