import os
import geopandas as gpd
import streamlit as st
import geemap.foliumap as geemap
from datetime import date
from shapely.geometry import Polygon


@st.cache
def uploaded_file_to_gdf(data):
    import tempfile
    import os
    import uuid

    _, file_extension = os.path.splitext(data.name)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(tempfile.gettempdir(), f"{file_id}{file_extension}")

    with open(file_path, "wb") as file:
        file.write(data.getbuffer())

    if file_path.lower().endswith(".kml"):
        gpd.io.file.fiona.drvsupport.supported_drivers["KML"] = "rw"
        gdf = gpd.read_file(file_path, driver="KML")
    else:
        gdf = gpd.read_file(file_path)

    return gdf


def app():

    today = date.today()

    st.title("Create Landsat Timelapse")

    st.markdown(
        """
        An interactive web app for creating timelapse of annual Landsat imagery (1984-2021) for any location around the globe. 
        The app was built using [streamlit](https://streamlit.io), [geemap](https://geemap.org), and [Google Earth Engine](https://earthengine.google.com). 
        See a [video demo](https://youtu.be/VVRK_-dEjR4).
    """
    )

    row1_col1, row1_col2 = st.columns([2, 1])

    with row1_col1:
        m = geemap.Map(basemap="HYBRID", plugin_Draw=True, draw_export=True)
        m.add_basemap("ROADMAP")

        with st.expander("See a video demo"):
            st.video("https://youtu.be/VVRK_-dEjR4")

        data = st.file_uploader(
            "Draw a small ROI on the map, click the Export button to save it, and then upload it here. Customize timelapse parameters and then click the Submit button 😇👇",
            type=["geojson"],
        )

        if data:
            gdf = uploaded_file_to_gdf(data)
            st.session_state["roi"] = geemap.geopandas_to_ee(gdf)
            m.add_gdf(gdf, "ROI")
        else:
            polygon_geom = Polygon(
                [
                    [-74.672699, -8.600032],
                    [-74.672699, -8.254983],
                    [-74.279938, -8.254983],
                    [-74.279938, -8.600032],
                ]
            )
            crs = {"init": "epsg:4326"}
            gdf = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[polygon_geom])
            st.session_state["roi"] = geemap.geopandas_to_ee(gdf)
            m.add_gdf(gdf, "ROI", zoom_to_layer=True)
        m.to_streamlit(height=600)

    with row1_col2:
        with st.form("submit_form"):

            roi = None
            if st.session_state.get("roi") is not None:
                roi = st.session_state.get("roi")
            out_gif = geemap.temp_file_path(".gif")

            collection = st.selectbox(
                "Select a collection: ",
                [
                    "Landsat TM-ETM-OLI Surface Reflectance",
                ],
            )

            title = st.text_input("Title: ", "Landsat Timelapse")
            RGB = st.selectbox(
                "RGB band combination:",
                [
                    "Red/Green/Blue",
                    "NIR/Red/Green",
                    "SWIR2/SWIR1/NIR",
                    "NIR/SWIR1/Red",
                    "SWIR2/NIR/Red",
                    "SWIR2/SWIR1/Red",
                    "SWIR1/NIR/Blue",
                    "NIR/SWIR1/Blue",
                    "SWIR2/NIR/Green",
                    "SWIR1/NIR/Red",
                ],
                index=9,
            )

            with st.expander("Customize timelapse"):

                speed = st.slider("Frames/sec:", 1, 30, 10)
                progress_bar_color = st.color_picker("Progress bar color:", "#0000ff")
                years = st.slider(
                    "Start and end year:", 1984, today.year, (1984, today.year - 1)
                )
                months = st.slider("Start and end month:", 1, 12, (5, 10))
                font_size = st.slider("Font size:", 10, 50, 30)
                font_color = st.color_picker("Font color:", "#ffffff")
                apply_fmask = st.checkbox(
                    "Apply fmask (remove clouds, shadows, snow)", True
                )

            empty_text = st.empty()
            empty_image = st.empty()
            submitted = st.form_submit_button("Submit")
            if submitted:
                empty_text.text("Computing... Please wait...")

                start_year = years[0]
                end_year = years[1]
                start_date = str(months[0]).zfill(2) + "-01"
                end_date = str(months[1]).zfill(2) + "-30"
                bands = RGB.split("/")

                out_gif = geemap.landsat_ts_gif(
                    roi=roi,
                    out_gif=out_gif,
                    start_year=start_year,
                    end_year=end_year,
                    start_date=start_date,
                    end_date=end_date,
                    bands=bands,
                    apply_fmask=apply_fmask,
                )

                geemap.add_text_to_gif(
                    out_gif,
                    out_gif,
                    xy=("2%", "2%"),
                    text_sequence=start_year,
                    font_size=font_size,
                    font_color=font_color,
                    duration=int(1000 / speed),
                    add_progress_bar=True,
                    progress_bar_color=progress_bar_color,
                    progress_bar_height=5,
                )

                geemap.add_text_to_gif(
                    out_gif,
                    out_gif,
                    xy=("2%", "90%"),
                    text_sequence=title,
                    font_size=font_size,
                    font_color=font_color,
                    duration=int(1000 / speed),
                    add_progress_bar=True,
                    progress_bar_color=progress_bar_color,
                    progress_bar_height=5,
                )

                geemap.reduce_gif_size(out_gif)

                empty_text.text("Right click the image to save it to your computer👇")
                empty_image.image(out_gif)
