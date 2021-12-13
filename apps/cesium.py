import leafmap
import streamlit as st


def app():
    st.title("Cesium 3D Map")
    html = "data/html/sfo_buildings.html"
    leafmap.cesium_to_streamlit(html, height=800)
