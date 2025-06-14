import pandas as pd
from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError
import config


def get_bigquery_client(project_id=config.BQ_PROJECT_ID):
    """
    Initializes and returns a google.cloud.bigquery.Client.

    Args:
        project_id (str, optional): The GCP project ID. Defaults to config.BQ_PROJECT_ID.

    Returns:
        google.cloud.bigquery.Client: The BigQuery client.
        None: If there's an authentication issue.
    """
    try:
        client = bigquery.Client(project=project_id)
        return client
    except GoogleCloudError as e:
        print(f"BigQuery authentication failed for project '{project_id}': {e}")
        return None
    except Exception as e:
        print(
            f"An unexpected error occurred during BigQuery client initialization for project '{project_id}': {e}"
        )
        return None


def fetch_locations_data(
    client,
    project_id=config.BQ_PROJECT_ID,
    dataset_id=config.BQ_DATASET_ID,
    table_id=config.BQ_LOCATIONS_TABLE_ID,
):
    """
    Fetches location data from a BigQuery table.

    Args:
        client (google.cloud.bigquery.Client): The BigQuery client.
        project_id (str, optional): The Google Cloud project ID. Defaults to config.BQ_PROJECT_ID.
        dataset_id (str, optional): The BigQuery dataset ID. Defaults to config.BQ_DATASET_ID.
        table_id (str, optional): The BigQuery table ID. Defaults to config.BQ_LOCATIONS_TABLE_ID.

    Returns:
        pandas.DataFrame: DataFrame containing location data (location_id, latitude, longitude).
        None: If query execution fails or table is not found.
    """
    if not client:
        print("BigQuery client is not available.")
        return None

    query = f"SELECT location_id, latitude, longitude FROM `{project_id}.{dataset_id}.{table_id}`"
    try:
        query_job = client.query(query)
        df = query_job.to_dataframe()
        return df
    except GoogleCloudError as e:
        print(f"BigQuery query failed: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during data fetching: {e}")
        return None


def fetch_historical_metrics(
    client,
    location_id,
    start_date,
    end_date,
    project_id=config.BQ_PROJECT_ID,
    dataset_id=config.BQ_DATASET_ID,
    table_id=config.BQ_PIPELINE_METRICS_TABLE_ID,
):
    """
    Fetches historical metrics for a specific location and date range from BigQuery.

    Args:
        client (google.cloud.bigquery.Client): The BigQuery client.
        location_id (str): The specific location_id to filter metrics for.
        start_date (datetime.date): The start date for the metrics.
        end_date (datetime.date): The end date for the metrics.
        project_id (str, optional): The Google Cloud project ID. Defaults to config.BQ_PROJECT_ID.
        dataset_id (str, optional): The BigQuery dataset ID. Defaults to config.BQ_DATASET_ID.
        table_id (str, optional): The BigQuery table ID for metrics. Defaults to config.BQ_PIPELINE_METRICS_TABLE_ID.

    Returns:
        pandas.DataFrame: DataFrame with 'timestamp' (as datetime) and 'metric_value'.
        None: If query execution fails or table is not found.
    """
    if not client:
        print("BigQuery client is not available.")
        return None

    query = f"""
        SELECT timestamp, metric_value
        FROM `{project_id}.{dataset_id}.{table_id}`
        WHERE location_id = @location_id
          AND timestamp >= @start_date
          AND timestamp <= @end_date
        ORDER BY timestamp
    """

    # Define query parameters
    # Ensure dates are in a format BigQuery understands (YYYY-MM-DD strings)
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("location_id", "STRING", location_id),
            bigquery.ScalarQueryParameter(
                "start_date", "DATE", start_date.strftime("%Y-%m-%d")
            ),
            bigquery.ScalarQueryParameter(
                "end_date", "DATE", end_date.strftime("%Y-%m-%d")
            ),
        ]
    )

    try:
        query_job = client.query(query, job_config=job_config)
        df = query_job.to_dataframe()
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        else:
            print("Warning: 'timestamp' column not found in metrics data.")
        return df
    except GoogleCloudError as e:
        print(f"BigQuery historical metrics query failed: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during historical metrics fetching: {e}")
        return None
