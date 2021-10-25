import streamlit as st
from multiapp import MultiApp
from apps import (
    basemaps,
    census,
    deck,
    gee,
    gee_datasets,
    heatmap,
    home,
    housing,
    timelapse,
    upload,
    wms,
)

st.set_page_config(layout="wide")


apps = MultiApp()

# Add all your application here

apps.add_app("Home", home.app)
apps.add_app("U.S. Real Estate", housing.app)
apps.add_app("U.S. Census Data", census.app)
apps.add_app("Create Timelapse", timelapse.app)
apps.add_app("Upload Vector Data", upload.app)
apps.add_app("Search Basemaps", basemaps.app)
apps.add_app("Pydeck Gallery", deck.app)
apps.add_app("Heatmaps", heatmap.app)
apps.add_app("Add Web Map Service (WMS)", wms.app)
apps.add_app("Google Earth Engine (GEE)", gee.app)
apps.add_app("Awesome GEE Community Datasets", gee_datasets.app)

# The main app
apps.run()
