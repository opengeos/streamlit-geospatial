import os
import leafmap.foliumap as leafmap
import streamlit as st
import palettable


@st.cache_data
def load_cog_list():
    print(os.getcwd())
    in_txt = os.path.join(os.getcwd(), "data/cog_files.txt")
    with open(in_txt) as f:
        return [line.strip() for line in f.readlines()[1:]]


@st.cache_data
def get_palettes():
    palettes = dir(palettable.matplotlib)[:-16]
    return ["matplotlib." + p for p in palettes]


def app():

    st.title("Visualize Raster Datasets")
    st.markdown(
        """
    An interactive web app for visualizing local raster datasets and Cloud Optimized GeoTIFF ([COG](https://www.cogeo.org)). The app was built using [streamlit](https://streamlit.io), [leafmap](https://leafmap.org), and [localtileserver](https://github.com/banesullivan/localtileserver).


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

        data = st.file_uploader("Upload a raster dataset", type=["tif", "img"])

        if data:
            url = empty.text_input(
                "Enter a URL to a Cloud Optimized GeoTIFF (COG)",
                "",
            )

        add_palette = st.checkbox("Add a color palette")
        if add_palette:
            palette = st.selectbox("Select a color palette", get_palettes())
        else:
            palette = None

        submit = st.button("Submit")

    m = leafmap.Map(latlon_control=False)

    if submit:
        if data or url:
            try:
                if data:
                    file_path = leafmap.save_data(data)
                    m.add_local_tile(file_path, palette=palette, debug=True)
                elif url:
                    m.add_remote_tile(url, palette=palette, debug=True)
            except Exception as e:
                with row1_col2:
                    st.error("Work in progress. Try it again later.")

    with row1_col1:
        m.to_streamlit()
