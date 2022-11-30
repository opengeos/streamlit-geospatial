import os
import fiona
import geopandas as gpd
import streamlit as st


def save_uploaded_file(file_content, file_name):
    """
    Save the uploaded file to a temporary directory
    """
    import tempfile
    import os
    import uuid

    _, file_extension = os.path.splitext(file_name)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(tempfile.gettempdir(), f"{file_id}{file_extension}")

    with open(file_path, "wb") as file:
        file.write(file_content.getbuffer())

    return file_path


def app():

    st.title("Upload Vector Data")

    row1_col1, row1_col2 = st.columns([2, 1])
    width = 950
    height = 600

    with row1_col2:

        backend = st.selectbox(
            "Select a plotting backend", ["folium", "kepler.gl", "pydeck"], index=2
        )

        if backend == "folium":
            import leafmap.foliumap as leafmap
        elif backend == "kepler.gl":
            import leafmap.kepler as leafmap
        elif backend == "pydeck":
            import leafmap.deck as leafmap

        url = st.text_input(
            "Enter a URL to a vector dataset",
            "https://github.com/giswqs/streamlit-geospatial/raw/master/data/us_states.geojson",
        )

        data = st.file_uploader(
            "Upload a vector dataset", type=["geojson", "kml", "zip", "tab"]
        )

        container = st.container()

        if data or url:
            if data:
                file_path = save_uploaded_file(data, data.name)
                layer_name = os.path.splitext(data.name)[0]
            elif url:
                file_path = url
                layer_name = url.split("/")[-1].split(".")[0]

            with row1_col1:
                if file_path.lower().endswith(".kml"):
                    fiona.drvsupport.supported_drivers["KML"] = "rw"
                    gdf = gpd.read_file(file_path, driver="KML")
                else:
                    gdf = gpd.read_file(file_path)
                lon, lat = leafmap.gdf_centroid(gdf)
                if backend == "pydeck":

                    column_names = gdf.columns.values.tolist()
                    random_column = None
                    with container:
                        random_color = st.checkbox("Apply random colors", True)
                        if random_color:
                            random_column = st.selectbox(
                                "Select a column to apply random colors", column_names
                            )

                    m = leafmap.Map(center=(lat, lon))
                    m.add_gdf(gdf, random_color_column=random_column)
                    st.pydeck_chart(m)

                else:
                    m = leafmap.Map(center=(lat, lon), draw_export=True)
                    m.add_gdf(gdf, layer_name=layer_name)
                    # m.add_vector(file_path, layer_name=layer_name)
                    if backend == "folium":
                        m.zoom_to_gdf(gdf)
                    m.to_streamlit(width=width, height=height)

        else:
            with row1_col1:
                m = leafmap.Map()
                st.pydeck_chart(m)
