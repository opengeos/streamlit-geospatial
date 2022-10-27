import streamlit as st
import leafmap.foliumap as leafmap


def app():
    st.title("Searching Basemaps")
    st.markdown(
        """
    This app is a demonstration of searching and loading basemaps from [xyzservices](https://github.com/geopandas/xyzservices) and [Quick Map Services (QMS)](https://github.com/nextgis/quickmapservices). Selecting from 1000+ basemaps with a few clicks.  
    """
    )

    with st.expander("See demo"):
        st.image("https://i.imgur.com/0SkUhZh.gif")

    row1_col1, row1_col2 = st.columns([3, 1])
    width = 800
    height = 600
    tiles = None

    with row1_col2:

        checkbox = st.checkbox("Search Quick Map Services (QMS)")
        keyword = st.text_input("Enter a keyword to search and press Enter:")
        empty = st.empty()

        if keyword:
            options = leafmap.search_xyz_services(keyword=keyword)
            if checkbox:
                qms = leafmap.search_qms(keyword=keyword)
                if qms is not None:
                    options = options + qms

            tiles = empty.multiselect(
                "Select XYZ tiles to add to the map:", options)

        with row1_col1:
            m = leafmap.Map()

            if tiles is not None:
                for tile in tiles:
                    m.add_xyz_service(tile)

            m.to_streamlit(width, height)
