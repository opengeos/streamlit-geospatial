import os
import leafmap.foliumap as leafmap
import leafmap.colormaps as cm
import streamlit as st

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


@st.cache_data
def load_cog_list():
    print(os.getcwd())
    in_txt = os.path.join(os.getcwd(), "data/cog_files.txt")
    with open(in_txt) as f:
        return [line.strip() for line in f.readlines()[1:]]


@st.cache_data
def get_palettes():
    return list(cm.palettes.keys())
    # palettes = dir(palettable.matplotlib)[:-16]
    # return ["matplotlib." + p for p in palettes]


st.title("Visualize Raster Datasets")
st.markdown(
    """
An interactive web app for visualizing local raster datasets and Cloud Optimized GeoTIFF ([COG](https://www.cogeo.org)). The app was built using [streamlit](https://streamlit.io), [leafmap](https://leafmap.org), and [Titiler](https://developmentseed.org/titiler/).


"""
)

row1_col1, row1_col2 = st.columns([2, 1])

with row1_col1:
    cog_list = load_cog_list()
    cog = st.selectbox("Select a sample Cloud Opitmized GeoTIFF (COG)", cog_list)

with row1_col2:
    empty = st.empty()

    url = empty.text_input(
        "Enter a HTTP URL to a Cloud Optimized GeoTIFF (COG)",
        cog,
    )

    if url:
        try:
            options = leafmap.cog_bands(url)
        except Exception as e:
            st.error(e)
        if len(options) > 3:
            default = options[:3]
        else:
            default = options[0]
        bands = st.multiselect("Select bands to display", options, default=options)

        if len(bands) == 1 or len(bands) == 3:
            pass
        else:
            st.error("Please select one or three bands")

    add_params = st.checkbox("Add visualization parameters")
    if add_params:
        vis_params = st.text_area("Enter visualization parameters", "{}")
    else:
        vis_params = {}

    if len(vis_params) > 0:
        try:
            vis_params = eval(vis_params)
        except Exception as e:
            st.error(
                f"Invalid visualization parameters. It should be a dictionary. Error: {e}"
            )
            vis_params = {}

    submit = st.button("Submit")

m = leafmap.Map(latlon_control=False)

if submit:
    if url:
        try:
            m.add_cog_layer(url, bands=bands, **vis_params)
        except Exception as e:
            with row1_col2:
                st.error(e)
                st.error("Work in progress. Try it again later.")

with row1_col1:
    m.to_streamlit()
