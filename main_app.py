import streamlit as st
import leafmap.foliumap as leafmap
import pandas as pd
import os
import datetime
import numpy as np
from bq_utils import fetch_locations_data, get_bigquery_client, fetch_historical_metrics
from vertex_utils import get_vertex_endpoint, get_prediction

st.set_page_config(layout="wide")

# --- Function Definitions for Data Loading and Callbacks ---
def load_and_display_schematic(location_id):
    if location_id:
        schematic_path = os.path.join("data", "schematics", f"{location_id}.png")
        if os.path.exists(schematic_path):
            st.session_state.current_schematic_path = schematic_path
        else:
            st.session_state.current_schematic_path = None
            # This warning will be displayed in the UI section if path is None
    else:
        st.session_state.current_schematic_path = None

def load_and_process_metrics(location_id, start_date, end_date):
    if not location_id: # Added check for location_id
        st.session_state.current_metrics_df = None
        st.session_state.current_outliers_df = None
        # st.info("Please select a location to load metrics.") # Info displayed in UI
        return

    if not st.session_state.get('bq_client'): # Check if bq_client exists and is not None
        st.error("BigQuery client not available.")
        st.session_state.current_metrics_df = None
        st.session_state.current_outliers_df = None
        return

    # BQ_PROJECT, BQ_DATASET, BQ_METRICS_TABLE are now defaulted in fetch_historical_metrics
    # by bq_utils.py pulling from config.py
    metrics_df = fetch_historical_metrics(st.session_state.bq_client, location_id, start_date, end_date)

    if metrics_df is None or metrics_df.empty:
        st.warning(f"Failed to fetch metrics for {location_id} from BigQuery or no data available. Using sample data.")
        sample_dates = pd.to_datetime(pd.date_range(start_date, end_date, periods=100))
        sample_values = np.random.rand(100) * 100
        if len(sample_values) >= 25: sample_values[20:25] *= 3
        if len(sample_values) >= 75: sample_values[70:75] *= 0.2
        metrics_df = pd.DataFrame({'timestamp': sample_dates, 'metric_value': sample_values, 'location_id': location_id})

    if metrics_df is not None and not metrics_df.empty: # Check added for metrics_df not being None
        metrics_df['timestamp'] = pd.to_datetime(metrics_df['timestamp'])
        # Ensure 'metric_value' column exists before processing
        if 'metric_value' in metrics_df.columns:
            mean_val = metrics_df['metric_value'].mean()
            std_val = metrics_df['metric_value'].std()
            if std_val == 0: # Avoid division by zero or issues with constant data
                upper_bound = mean_val
                lower_bound = mean_val
            else:
                upper_bound = mean_val + 2 * std_val
                lower_bound = mean_val - 2 * std_val
            metrics_df['is_outlier'] = (metrics_df['metric_value'] > upper_bound) | (metrics_df['metric_value'] < lower_bound)
            st.session_state.current_metrics_df = metrics_df
            st.session_state.current_outliers_df = metrics_df[metrics_df['is_outlier']]
        else:
            st.error("'metric_value' column missing from data.")
            st.session_state.current_metrics_df = metrics_df # Store even if no metric_value for inspection
            st.session_state.current_outliers_df = pd.DataFrame()
    else:
        st.session_state.current_metrics_df = None
        st.session_state.current_outliers_df = None

def handle_location_selection_change():
    new_location_id = st.session_state.unified_location_selector
    st.session_state.selected_location_id = new_location_id
    # Update dates from session state as they are the current source of truth for date pickers
    current_start_date = st.session_state.get('metrics_start_date', datetime.date(2023,1,1))
    current_end_date = st.session_state.get('metrics_end_date', datetime.date.today())
    load_and_display_schematic(new_location_id)
    load_and_process_metrics(new_location_id, current_start_date, current_end_date)

def handle_metrics_date_change():
    # Dates are directly bound to session state by the widgets' keys
    load_and_process_metrics(st.session_state.selected_location_id,
                             st.session_state.metrics_start_date,
                             st.session_state.metrics_end_date)

# --- Session State Initialization ---
if 'initialized' not in st.session_state:
    st.session_state.bq_client = get_bigquery_client()
    sample_loc_data = {
        'location_id': ['LOC001', 'LOC002', 'LOC003'],
        'latitude': [37.7749, 34.0522, 40.7128],
        'longitude': [-122.4194, -118.2437, -74.0060]
    }
    st.session_state.locations_data = pd.DataFrame(sample_loc_data)
    st.info("Using sample location data for initial setup.")

    st.session_state.selected_location_id = st.session_state.locations_data['location_id'].iloc[0] if not st.session_state.locations_data.empty else None
    # Initialize date keys for date_inputs
    st.session_state.metrics_start_date = datetime.date(2023, 1, 1)
    st.session_state.metrics_end_date = datetime.date.today()

    st.session_state.current_schematic_path = None
    st.session_state.current_metrics_df = None
    st.session_state.current_outliers_df = None
    st.session_state.initialized = True

    # Initial data load for the default selected location
    if st.session_state.selected_location_id:
        load_and_display_schematic(st.session_state.selected_location_id)
        load_and_process_metrics(st.session_state.selected_location_id, st.session_state.metrics_start_date, st.session_state.metrics_end_date)

# --- Sidebar ---
st.sidebar.title("Controls")
st.sidebar.header("Global Controls")
if st.session_state.locations_data is not None and not st.session_state.locations_data.empty:
    # Ensure default index is valid
    loc_list = st.session_state.locations_data['location_id'].tolist()
    default_idx = 0
    if st.session_state.selected_location_id in loc_list:
        default_idx = loc_list.index(st.session_state.selected_location_id)

    st.sidebar.selectbox(
        "Select Location:",
        options=loc_list,
        key='unified_location_selector', # This key will hold the selected value
        on_change=handle_location_selection_change,
        index=default_idx
    )
else:
    st.sidebar.info("No locations loaded.")

# --- Main App Layout ---
st.title("Advanced Streamlit GIS App")

# --- Map Display Section ---
st.header("Map Display")
if 'locations_data' in st.session_state and st.session_state.locations_data is not None and not st.session_state.locations_data.empty:
    df_map = st.session_state.locations_data
    if isinstance(df_map, pd.DataFrame) and 'latitude' in df_map.columns and 'longitude' in df_map.columns:
        if not df_map.empty:
            center_lat, center_lon = df_map['latitude'].mean(), df_map['longitude'].mean()
            zoom_start = 4
        else:
            center_lat, center_lon = 39.8283, -98.5795
            zoom_start = 3
        m = leafmap.Map(center=(center_lat, center_lon), zoom=zoom_start)
        m.add_points_from_xy(df_map, x="longitude", y="latitude", popups=["location_id"])
        m.to_streamlit(height=500)
    else:
        st.warning("Location data is available but missing 'latitude' or 'longitude' columns, or is not a DataFrame.")
else:
    st.info("No location data to display for the map.")

# --- Schematic Viewer Section ---
st.header("Schematic Viewer")
if st.session_state.get("current_schematic_path"):
    st.image(st.session_state.current_schematic_path, caption=f"Schematic for {st.session_state.get('selected_location_id', 'N/A')}")
elif st.session_state.get("selected_location_id"): # If a location is selected but path is None
    st.warning(f"Schematic not available for {st.session_state.selected_location_id}.")
else: # No location selected yet
    st.info("Select a location to view schematic.")

# --- Historical Metrics & Outlier Detection Section ---
st.header("Historical Metrics & Outlier Detection")
col1, col2 = st.columns(2)
with col1:
    st.date_input("Start Date", key='metrics_start_date', on_change=handle_metrics_date_change)
with col2:
    st.date_input("End Date", key='metrics_end_date', on_change=handle_metrics_date_change)

if st.session_state.get("selected_location_id"): # Only show metrics if a location is selected
    if st.session_state.get("current_metrics_df") is not None and not st.session_state.current_metrics_df.empty:
        current_metrics_df = st.session_state.current_metrics_df
        st.subheader(f"Metrics Chart for {st.session_state.selected_location_id}")
        if 'timestamp' in current_metrics_df.columns and 'metric_value' in current_metrics_df.columns:
            chart_display_df = current_metrics_df.set_index('timestamp')
            st.line_chart(chart_display_df['metric_value'])

            st.subheader("Summary Statistics")
            st.write(current_metrics_df['metric_value'].describe())

            st.subheader("Detected Outliers")
            current_outliers_df = st.session_state.get("current_outliers_df")
            if current_outliers_df is not None and not current_outliers_df.empty:
                st.dataframe(current_outliers_df[['timestamp', 'metric_value', 'is_outlier']])
            else:
                st.info("No outliers detected or data not processed for outliers.")
        else:
            st.warning("Metrics data is missing 'timestamp' or 'metric_value' columns.")

    elif st.session_state.get("selected_location_id"): # If selected_id exists but no metrics_df
        st.info(f"No metrics data loaded or available for {st.session_state.selected_location_id}. Try adjusting dates or ensure data source is available.")
else:
    st.info("Select a location to view metrics.")


# --- Vertex AI Prediction Section --- (Remains Unchanged from previous state)
st.header("Vertex AI Prediction")
feature1 = st.number_input("Feature 1 (numerical)", value=0.0)
feature2 = st.number_input("Feature 2 (numerical)", value=0.0)

if st.button("Get Prediction from Vertex AI"):
    # PROJECT_ID, LOCATION, ENDPOINT_ID are now defaulted in get_vertex_endpoint
    # by vertex_utils.py pulling from config.py
    st.info(f"Attempting to connect to Vertex AI using default configuration...")
    endpoint = get_vertex_endpoint()

    if endpoint:
        # The display_name attribute might not be populated if the endpoint is not fully fetched
        # or if there was an issue. endpoint.name is more reliable for the ID.
        st.write(f"Connected to Vertex AI endpoint (ID: {endpoint.name}).")
        instance = {"feature1": feature1, "feature2": feature2}
        st.write(f"Sending instance for prediction: {instance}")
        prediction = get_prediction(endpoint, instance_data=instance)

        if prediction is not None:
            st.success("Prediction received:")
            st.json(prediction)
        else:
            st.error("Failed to get prediction from Vertex AI. Check logs for details.")
    else:
        st.error("Failed to initialize Vertex AI endpoint. Check configuration, authentication, and endpoint ID.")
