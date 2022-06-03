import streamlit as st
from multiapp import MultiApp
from apps import (
    basemaps,
    census,
    cesium,
    deck,
    device_loc,
    gee,
    gee_datasets,
    heatmap,
    home,
    housing,
    # hurricane,
    plotly_maps,
    raster,
    timelapse,
    vector,
    wms,
    xy,
)

st.set_page_config(layout="wide")


apps = MultiApp()

# Add all your application here

apps.add_app("Home", home.app)
apps.add_app("Create Timelapse", timelapse.app)
# apps.add_app("Hurricane Mapping", hurricane.app)
apps.add_app("U.S. Real Estate Data", housing.app)
apps.add_app("U.S. Census Data", census.app)
apps.add_app("Visualize Raster Data", raster.app)
apps.add_app("Visualize Vector Data", vector.app)
apps.add_app("Search Basemaps", basemaps.app)
apps.add_app("Pydeck Gallery", deck.app)
apps.add_app("Heatmaps", heatmap.app)
apps.add_app("Add Points from XY", xy.app)
apps.add_app("Add Web Map Service (WMS)", wms.app)
apps.add_app("Google Earth Engine (GEE)", gee.app)
apps.add_app("Awesome GEE Community Datasets", gee_datasets.app)
apps.add_app("Geolocation", device_loc.app)
apps.add_app("Cesium 3D Map", cesium.app)
apps.add_app("Plotly", plotly_maps.app)

# The main app
apps.run()
