import datetime
import ee
import streamlit as st
import geemap.foliumap as geemap

st.set_page_config(layout="wide")

st.sidebar.info(
    """
    - Web App URL: <https://streamlit.geemap.org>
    - GitHub repository: <https://github.com/giswqs/streamlit-geospatial>
    """
)

st.sidebar.title("Contact")
st.sidebar.info(
    """
    Qiusheng Wu: <https://wetlands.io>
    [GitHub](https://github.com/giswqs) | [Twitter](https://twitter.com/giswqs) | [YouTube](https://www.youtube.com/c/QiushengWu) | [LinkedIn](https://www.linkedin.com/in/qiushengwu)
    """
)

st.title("Comparing Global Land Cover Maps")

col1, col2 = st.columns([4, 1])

Map = geemap.Map()
Map.add_basemap("ESA WorldCover 2020 S2 FCC")
Map.add_basemap("ESA WorldCover 2020 S2 TCC")
Map.add_basemap("HYBRID")

esa = ee.ImageCollection("ESA/WorldCover/v100").first()
esa_vis = {"bands": ["Map"]}


esri = ee.ImageCollection(
    "projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m"
).mosaic()
esri_vis = {
    "min": 1,
    "max": 10,
    "palette": [
        "#1A5BAB",
        "#358221",
        "#A7D282",
        "#87D19E",
        "#FFDB5C",
        "#EECFA8",
        "#ED022A",
        "#EDE9E4",
        "#F2FAFF",
        "#C8C8C8",
    ],
}


markdown = """
    - [Dynamic World Land Cover](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1?hl=en)
    - [ESA Global Land Cover](https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v100)
    - [ESRI Global Land Cover](https://samapriya.github.io/awesome-gee-community-datasets/projects/esrilc2020)

"""

with col2:

    longitude = st.number_input("Longitude", -180.0, 180.0, -89.3998)
    latitude = st.number_input("Latitude", -90.0, 90.0, 43.0886)
    zoom = st.number_input("Zoom", 0, 20, 11)

    Map.setCenter(longitude, latitude, zoom)

    start = st.date_input("Start Date for Dynamic World", datetime.date(2020, 1, 1))
    end = st.date_input("End Date for Dynamic World", datetime.date(2021, 1, 1))

    start_date = start.strftime("%Y-%m-%d")
    end_date = end.strftime("%Y-%m-%d")

    region = ee.Geometry.BBox(-179, -89, 179, 89)
    dw = geemap.dynamic_world(region, start_date, end_date, return_type="hillshade")

    layers = {
        "Dynamic World": geemap.ee_tile_layer(dw, {}, "Dynamic World Land Cover"),
        "ESA Land Cover": geemap.ee_tile_layer(esa, esa_vis, "ESA Land Cover"),
        "ESRI Land Cover": geemap.ee_tile_layer(esri, esri_vis, "ESRI Land Cover"),
    }

    options = list(layers.keys())
    left = st.selectbox("Select a left layer", options, index=1)
    right = st.selectbox("Select a right layer", options, index=0)

    left_layer = layers[left]
    right_layer = layers[right]

    Map.split_map(left_layer, right_layer)

    legend = st.selectbox("Select a legend", options, index=options.index(right))
    if legend == "Dynamic World":
        Map.add_legend(
            title="Dynamic World Land Cover",
            builtin_legend="Dynamic_World",
        )
    elif legend == "ESA Land Cover":
        Map.add_legend(title="ESA Land Cover", builtin_legend="ESA_WorldCover")
    elif legend == "ESRI Land Cover":
        Map.add_legend(title="ESRI Land Cover", builtin_legend="ESRI_LandCover")

    with st.expander("Data sources"):
        st.markdown(markdown)


with col1:
    Map.to_streamlit(height=750)
