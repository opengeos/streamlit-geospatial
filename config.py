# config.py

# BigQuery Configuration
BQ_PROJECT_ID = "your-gcp-project-id-here"
BQ_DATASET_ID = "your-dataset-id-here"
BQ_LOCATIONS_TABLE_ID = "your-locations-table-id-here"
BQ_PIPELINE_METRICS_TABLE_ID = "your-pipeline-metrics-table-id-here"

# Vertex AI Configuration
VERTEX_AI_PROJECT_ID = "your-gcp-project-id-here" # Often same as BQ_PROJECT_ID
VERTEX_AI_LOCATION = "your-gcp-region-here" # e.g., "us-central1"
VERTEX_AI_ENDPOINT_ID = "your-vertex-ai-endpoint-id-here"

# Default Map Center (Example, if needed by main_app.py)
# DEFAULT_MAP_CENTER_LAT = 20.0
# DEFAULT_MAP_CENTER_LON = 0.0
# DEFAULT_MAP_ZOOM = 2
