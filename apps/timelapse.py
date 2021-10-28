import os
import datetime
import geopandas as gpd
import streamlit as st
import geemap.foliumap as geemap
from datetime import date
from shapely.geometry import Polygon
from .rois import goes_rois, landsat_rois


@st.cache
def uploaded_file_to_gdf(data):
    import tempfile
    import os
    import uuid

    _, file_extension = os.path.splitext(data.name)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(tempfile.gettempdir(),
                             f"{file_id}{file_extension}")

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

    st.title("Create Landsat/GOES Timelapse")

    st.markdown(
        """
        An interactive web app for creating [Landsat](https://developers.google.com/earth-engine/datasets/catalog/landsat)/[GOES](https://jstnbraaten.medium.com/goes-in-earth-engine-53fbc8783c16) timelapse for any location around the globe. 
        The app was built using [streamlit](https://streamlit.io), [geemap](https://geemap.org), and [Google Earth Engine](https://earthengine.google.com). 
    """
    )

    row1_col1, row1_col2 = st.columns([2, 1])

    with row1_col2:

        collection = st.selectbox(
            "Select a satellite image collection: ",
            [
                "Landsat TM-ETM-OLI Surface Reflectance",
                "Geostationary Operational Environmental Satellites (GOES)",
            ],
            index=0,
        )

        if collection == "Landsat TM-ETM-OLI Surface Reflectance":
            roi_options = ["Uploaded GeoJSON"] + list(landsat_rois.keys())

        elif collection == "Geostationary Operational Environmental Satellites (GOES)":

            roi_options = ["Uploaded GeoJSON"] + list(goes_rois.keys())

        sample_roi = st.selectbox(
            "Select a sample ROI or upload a GeoJSON file:", roi_options, index=0,
        )

    with row1_col1:
        m = geemap.Map(basemap="HYBRID", plugin_Draw=True, draw_export=True)
        m.add_basemap("ROADMAP")

        with st.expander("See a video demo"):
            video_empty = st.empty()

        data = st.file_uploader(
            "Draw a small ROI on the map, click the Export button to save it, and then upload it here. Customize timelapse parameters and then click the Submit button 😇👇",
            type=["geojson"],
        )

        crs = {"init": "epsg:4326"}
        if sample_roi == "Uploaded GeoJSON":
            if data is None:
                st.info(
                    "Steps to create a timelapse: Draw a rectangle on the map -> Export it as a GeoJSON -> Upload it back to the app -> Click Submit button")
                if collection == "Landsat TM-ETM-OLI Surface Reflectance":
                    try:
                        # lat, lon = geemap.get_current_latlon()
                        m.set_center(4.20, 18.63, zoom=2)
                    except:
                        pass
        else:
            if collection == "Landsat TM-ETM-OLI Surface Reflectance":
                gdf = gpd.GeoDataFrame(
                    index=[0], crs=crs, geometry=[landsat_rois[sample_roi]])
            elif collection == "Geostationary Operational Environmental Satellites (GOES)":
                gdf = gpd.GeoDataFrame(
                    index=[0], crs=crs, geometry=[goes_rois[sample_roi]["region"]])

        if sample_roi != "Uploaded GeoJSON":

            if collection == "Landsat TM-ETM-OLI Surface Reflectance":
                gdf = gpd.GeoDataFrame(
                    index=[0], crs=crs, geometry=[landsat_rois[sample_roi]])
            elif collection == "Geostationary Operational Environmental Satellites (GOES)":
                gdf = gpd.GeoDataFrame(
                    index=[0], crs=crs, geometry=[goes_rois[sample_roi]["region"]])
            st.session_state["roi"] = geemap.geopandas_to_ee(gdf)
            m.add_gdf(gdf, "ROI")
        elif data:
            gdf = uploaded_file_to_gdf(data)
            st.session_state["roi"] = geemap.geopandas_to_ee(gdf)
            m.add_gdf(gdf, "ROI")

        m.to_streamlit(height=600)

    with row1_col2:

        if collection == "Landsat TM-ETM-OLI Surface Reflectance":

            video_empty.video("https://youtu.be/VVRK_-dEjR4")

            with st.form("submit_landsat_form"):

                roi = None
                if st.session_state.get("roi") is not None:
                    roi = st.session_state.get("roi")
                out_gif = geemap.temp_file_path(".gif")

                title = st.text_input(
                    "Enter a title to show on the timelapse: ", "Landsat Timelapse"
                )
                RGB = st.selectbox(
                    "Select an RGB band combination:",
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

                    speed = st.slider("Frames per second:", 1, 30, 10)
                    progress_bar_color = st.color_picker(
                        "Progress bar color:", "#0000ff"
                    )
                    years = st.slider(
                        "Start and end year:", 1984, today.year, (
                            1984, today.year - 1)
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

                    if sample_roi == "Uploaded GeoJSON" and data is None:
                        empty_text.warning(
                            "Steps to create a timelapse: Draw a rectangle on the map -> Export it as a GeoJSON -> Upload it back to the app -> Click the Submit button. Alternatively, you can select a sample ROI from the dropdown list.")
                    else:

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

                        empty_text.text(
                            "Right click the GIF to save it to your computer👇")
                        empty_image.image(out_gif)

        elif collection == "Geostationary Operational Environmental Satellites (GOES)":

            video_empty.video("https://youtu.be/16fA2QORG4A")

            with st.form("submit_goes_form"):

                roi = None
                if st.session_state.get("roi") is not None:
                    roi = st.session_state.get("roi")
                out_gif = geemap.temp_file_path(".gif")

                satellite = st.selectbox("Select a satellite:", [
                                         "GOES-17", "GOES-16"])
                earliest_date = datetime.date(2017, 7, 10)
                latest_date = datetime.date.today()

                if sample_roi == "Uploaded GeoJSON":
                    roi_start_date = today - datetime.timedelta(days=2)
                    roi_end_date = today - datetime.timedelta(days=1)
                    roi_start_time = datetime.time(14, 00)
                    roi_end_time = datetime.time(1, 00)
                else:
                    roi_start = goes_rois[sample_roi]["start_time"]
                    roi_end = goes_rois[sample_roi]["end_time"]
                    roi_start_date = datetime.datetime.strptime(
                        roi_start[:10], "%Y-%m-%d")
                    roi_end_date = datetime.datetime.strptime(
                        roi_end[:10], "%Y-%m-%d")
                    roi_start_time = datetime.time(
                        int(roi_start[11:13]), int(roi_start[14:16]))
                    roi_end_time = datetime.time(
                        int(roi_end[11:13]), int(roi_end[14:16]))

                start_date = st.date_input(
                    "Select the start date:", roi_start_date)
                end_date = st.date_input("Select the end date:", roi_end_date)

                with st.expander("Customize timelapse"):

                    scan_type = st.selectbox(
                        "Select a scan type:", [
                            "Full Disk", "CONUS", "Mesoscale"]
                    )

                    start_time = st.time_input(
                        "Select the start time of the start date:",
                        roi_start_time
                    )

                    end_time = st.time_input(
                        "Select the end time of the end date:", roi_end_time
                    )

                    start = (
                        start_date.strftime("%Y-%m-%d")
                        + "T"
                        + start_time.strftime("%H:%M:%S")
                    )
                    end = (
                        end_date.strftime("%Y-%m-%d")
                        + "T"
                        + end_time.strftime("%H:%M:%S")
                    )

                    speed = st.slider("Frames per second:", 1, 30, 10)
                    add_progress_bar = st.checkbox("Add a progress bar", True)
                    progress_bar_color = st.color_picker(
                        "Progress bar color:", "#0000ff"
                    )
                    font_size = st.slider("Font size:", 10, 50, 20)
                    font_color = st.color_picker("Font color:", "#ffffff")
                empty_text = st.empty()
                empty_image = st.empty()
                submitted = st.form_submit_button("Submit")
                if submitted:
                    if sample_roi == "Uploaded GeoJSON" and data is None:
                        empty_text.warning(
                            "Steps to create a timelapse: Draw a rectangle on the map -> Export it as a GeoJSON -> Upload it back to the app -> Click the Submit button. Alternatively, you can select a sample ROI from the dropdown list.")
                    else:
                        empty_text.text("Computing... Please wait...")

                        geemap.goes_timelapse(
                            out_gif,
                            start_date=start,
                            end_date=end,
                            data=satellite,
                            scan=scan_type.replace(" ", "_").lower(),
                            region=roi,
                            dimensions=768,
                            framesPerSecond=speed,
                            date_format="YYYY-MM-dd HH:mm",
                            xy=("3%", "3%"),
                            text_sequence=None,
                            font_type="arial.ttf",
                            font_size=font_size,
                            font_color=font_color,
                            add_progress_bar=add_progress_bar,
                            progress_bar_color=progress_bar_color,
                            progress_bar_height=5,
                            loop=0,
                        )

                        if os.path.exists(out_gif):
                            empty_text.text(
                                "Right click the GIF to save it to your computer👇"
                            )
                            empty_image.image(out_gif)
                        else:
                            empty_text.text(
                                "Something went wrong, either the ROI is too big or there are no data available for the specified date range. Please try a smaller ROI or different date range."
                            )
