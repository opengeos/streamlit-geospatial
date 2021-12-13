import leafmap.foliumap as leafmap
import pandas as pd
import streamlit as st


def app():

    st.title("Add Points from XY")

    sample_url = "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/world_cities.csv"
    url = st.text_input("Enter URL:", sample_url)
    m = leafmap.Map(locate_control=True, plugin_LatLngPopup=False)

    if url:

        try:
            df = pd.read_csv(url)

            columns = df.columns.values.tolist()
            row1_col1, row1_col2, row1_col3 = st.columns([1, 1, 2])

            lon_index = 0
            lat_index = 0

            for col in columns:
                if col.lower() in ["lon", "longitude", "long", "lng"]:
                    lon_index = columns.index(col)
                elif col.lower() in ["lat", "latitude"]:
                    lat_index = columns.index(col)

            with row1_col1:
                x = st.selectbox("Select longitude column", columns, lon_index)

            with row1_col2:
                y = st.selectbox("Select latitude column", columns, lat_index)

            with row1_col3:
                popups = st.multiselect("Select popup columns", columns, columns)

            m.add_points_from_xy(df, x, y, popups)

        except Exception as e:
            st.error(e)

    m.to_streamlit()
