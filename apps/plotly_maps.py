import streamlit as st
import leafmap.plotlymap as leafmap


def app():

    st.title("Plotly Maps")
    m = leafmap.Map(basemap="street", height=650)
    m.add_mapbox_layer(style="streets")

    basemaps = list(leafmap.basemaps.keys())
    basemap = st.selectbox(
        "Select a basemap", basemaps, basemaps.index("Stamen.Terrain")
    )
    m.add_basemap(basemap)

    st.plotly_chart(m, use_container_width=True)
