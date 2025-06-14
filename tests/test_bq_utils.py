# tests/test_bq_utils.py
import pytest
from unittest.mock import MagicMock, patch, ANY
import pandas as pd
from datetime import date
from google.api_core.exceptions import GoogleAPICallError
from google.cloud import bigquery # Added for QueryJobConfig

# Make sure bq_utils can be imported
# This assumes that pytest is run from the root directory or PYTHONPATH includes the root.
import bq_utils
import config # bq_utils imports config

@pytest.fixture
def mock_bq_client():
    return MagicMock()

def test_get_bigquery_client_success():
    # Test if client is returned (actual client creation is mocked)
    with patch('google.cloud.bigquery.Client') as mock_client_constructor:
        mock_instance = MagicMock()
        mock_client_constructor.return_value = mock_instance
        client = bq_utils.get_bigquery_client(project_id="test-project")
        assert client == mock_instance
        mock_client_constructor.assert_called_once_with(project="test-project")

def test_get_bigquery_client_failure():
    with patch('google.cloud.bigquery.Client', side_effect=GoogleAPICallError("Auth error")):
        client = bq_utils.get_bigquery_client(project_id="test-project")
        assert client is None

def test_fetch_locations_data_success(mock_bq_client):
    mock_query_job = MagicMock() # This is what client.query() returns
    mock_query_job.to_dataframe.return_value = pd.DataFrame({
        'location_id': ['LOC001', 'LOC002'],
        'latitude': [10.0, 20.0],
        'longitude': [-10.0, -20.0]
    })
    mock_bq_client.query.return_value = mock_query_job

    df = bq_utils.fetch_locations_data(mock_bq_client)

    expected_sql = f"SELECT location_id, latitude, longitude FROM `{config.BQ_PROJECT_ID}.{config.BQ_DATASET_ID}.{config.BQ_LOCATIONS_TABLE_ID}`"
    mock_bq_client.query.assert_called_once_with(expected_sql)
    assert not df.empty
    assert 'location_id' in df.columns
    assert len(df) == 2

def test_fetch_locations_data_query_fails(mock_bq_client):
    mock_bq_client.query.side_effect = GoogleAPICallError("Query failed")
    df = bq_utils.fetch_locations_data(mock_bq_client)
    assert df is None

def test_fetch_locations_data_no_results(mock_bq_client):
    mock_query_job = MagicMock()
    mock_query_job.to_dataframe.return_value = pd.DataFrame() # Empty DataFrame
    mock_bq_client.query.return_value = mock_query_job
    df = bq_utils.fetch_locations_data(mock_bq_client)
    assert df.empty

def test_fetch_historical_metrics_success(mock_bq_client):
    mock_query_job = MagicMock()
    mock_query_job.to_dataframe.return_value = pd.DataFrame({
        'timestamp': pd.to_datetime(['2023-01-01T10:00:00Z']), # Ensure it's a valid timestamp format
        'metric_value': [100.5]
    })
    mock_bq_client.query.return_value = mock_query_job

    df = bq_utils.fetch_historical_metrics(mock_bq_client, "LOC001", date(2023,1,1), date(2023,1,31))

    # Check that query was called with a QueryJobConfig object
    # The actual SQL string is the first argument, job_config is the keyword argument
    # We assert that it was called, and that job_config was an instance of QueryJobConfig
    mock_bq_client.query.assert_called_once()
    call_args = mock_bq_client.query.call_args
    assert isinstance(call_args.kwargs['job_config'], bigquery.QueryJobConfig)

    # Further check parameters within job_config if necessary
    job_config_params = {p.name: p.value for p in call_args.kwargs['job_config'].query_parameters}
    assert job_config_params['location_id'] == "LOC001"
    # The .value attribute of ScalarQueryParameter might return a date object if type is DATE
    assert job_config_params['start_date'] == date(2023, 1, 1)
    assert job_config_params['end_date'] == date(2023, 1, 31)

    assert not df.empty
    assert 'metric_value' in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df['timestamp'])

def test_fetch_historical_metrics_query_fails(mock_bq_client):
    mock_bq_client.query.side_effect = GoogleAPICallError("Query failed")
    df = bq_utils.fetch_historical_metrics(mock_bq_client, "LOC001", date(2023,1,1), date(2023,1,31))
    assert df is None

def test_fetch_historical_metrics_no_timestamp_column(mock_bq_client):
    mock_query_job = MagicMock()
    # Return data without a 'timestamp' column
    mock_query_job.to_dataframe.return_value = pd.DataFrame({'metric_value': [100.5, 200.0]})
    mock_bq_client.query.return_value = mock_query_job

    # Patch print to capture its output
    with patch('builtins.print') as mock_print:
        df = bq_utils.fetch_historical_metrics(mock_bq_client, "LOC001", date(2023,1,1), date(2023,1,31))
        mock_print.assert_any_call("Warning: 'timestamp' column not found in metrics data.")

    assert not df.empty # Data is still returned
    assert 'timestamp' not in df.columns # Ensure timestamp wasn't somehow added
    assert 'metric_value' in df.columns
