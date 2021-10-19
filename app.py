import streamlit as st
from multiapp import MultiApp
from apps import basemaps, heatmap, home, census, deck, housing, upload

st.set_page_config(layout="wide")


apps = MultiApp()

# Add all your application here

apps.add_app("Home", home.app)
apps.add_app("U.S. Real Estate", housing.app)
apps.add_app("U.S. Census Data", census.app)
apps.add_app("Upload Vector Data", upload.app)
apps.add_app("Search Basemaps", basemaps.app)
apps.add_app("Pydeck Gallery", deck.app)
apps.add_app("Heatmaps", heatmap.app)

# The main app
apps.run()
