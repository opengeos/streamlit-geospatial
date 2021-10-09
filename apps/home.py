import streamlit as st
import leafmap.foliumap as leafmap


def app():
    st.title("Home")

    st.header("Introduction")
    st.write(
        "This web app demonstrates how to create interactive maps using streamlit and open-source mapping libraries."
    )

    st.markdown("Source code: <https://github.com/giswqs/streamlit-geospatial>")
    st.markdown("Web app: <https://gishub.org/streamlit-geospatial>")

    st.header("Example")

    filepath = "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/us_cities.csv"
    m = leafmap.Map(tiles="stamentoner")
    m.add_heatmap(
        filepath,
        latitude="latitude",
        longitude="longitude",
        value="pop_max",
        name="Heat map",
        radius=20,
    )
    m.to_streamlit(width=700, height=500)
