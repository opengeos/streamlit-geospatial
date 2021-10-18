import streamlit as st
from multiapp import MultiApp
from apps import home, census, deck, housing, upload

st.set_page_config(layout="wide")


apps = MultiApp()

# Add all your application here

apps.add_app("U.S. Real Estate", housing.app)
apps.add_app("U.S. Census Data", census.app)
apps.add_app("Upload Vector Data", upload.app)
apps.add_app("Pydeck", deck.app)
apps.add_app("Home", home.app)

# The main app
apps.run()
