import ee
import os
import warnings
import datetime
import fiona
import geopandas as gpd
import folium
import streamlit as st
import geemap.colormaps as cm
import geemap.foliumap as geemap
from datetime import date
from shapely.geometry import Polygon

st.set_page_config(layout="wide")
warnings.filterwarnings("ignore")


@st.cache_data
def ee_authenticate(token_name="EARTHENGINE_TOKEN"):
    geemap.ee_initialize(token_name=token_name)


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

goes_rois = {
    "Creek Fire, CA (2020-09-05)": {
        "region": Polygon(
            [
                [-121.003418, 36.848857],
                [-121.003418, 39.049052],
                [-117.905273, 39.049052],
                [-117.905273, 36.848857],
                [-121.003418, 36.848857],
            ]
        ),
        "start_time": "2020-09-05T15:00:00",
        "end_time": "2020-09-06T02:00:00",
    },
    "Bomb Cyclone (2021-10-24)": {
        "region": Polygon(
            [
                [-159.5954, 60.4088],
                [-159.5954, 24.5178],
                [-114.2438, 24.5178],
                [-114.2438, 60.4088],
            ]
        ),
        "start_time": "2021-10-24T14:00:00",
        "end_time": "2021-10-25T01:00:00",
    },
    "Hunga Tonga Volcanic Eruption (2022-01-15)": {
        "region": Polygon(
            [
                [-192.480469, -32.546813],
                [-192.480469, -8.754795],
                [-157.587891, -8.754795],
                [-157.587891, -32.546813],
                [-192.480469, -32.546813],
            ]
        ),
        "start_time": "2022-01-15T03:00:00",
        "end_time": "2022-01-15T07:00:00",
    },
    "Hunga Tonga Volcanic Eruption Closer Look (2022-01-15)": {
        "region": Polygon(
            [
                [-178.901367, -22.958393],
                [-178.901367, -17.85329],
                [-171.452637, -17.85329],
                [-171.452637, -22.958393],
                [-178.901367, -22.958393],
            ]
        ),
        "start_time": "2022-01-15T03:00:00",
        "end_time": "2022-01-15T07:00:00",
    },
}


landsat_rois = {
    "Aral Sea": Polygon(
        [
            [57.667236, 43.834527],
            [57.667236, 45.996962],
            [61.12793, 45.996962],
            [61.12793, 43.834527],
            [57.667236, 43.834527],
        ]
    ),
    "Dubai": Polygon(
        [
            [54.541626, 24.763044],
            [54.541626, 25.427152],
            [55.632019, 25.427152],
            [55.632019, 24.763044],
            [54.541626, 24.763044],
        ]
    ),
    "Hong Kong International Airport": Polygon(
        [
            [113.825226, 22.198849],
            [113.825226, 22.349758],
            [114.085121, 22.349758],
            [114.085121, 22.198849],
            [113.825226, 22.198849],
        ]
    ),
    "Las Vegas, NV": Polygon(
        [
            [-115.554199, 35.804449],
            [-115.554199, 36.558188],
            [-113.903503, 36.558188],
            [-113.903503, 35.804449],
            [-115.554199, 35.804449],
        ]
    ),
    "Pucallpa, Peru": Polygon(
        [
            [-74.672699, -8.600032],
            [-74.672699, -8.254983],
            [-74.279938, -8.254983],
            [-74.279938, -8.600032],
        ]
    ),
    "Sierra Gorda, Chile": Polygon(
        [
            [-69.315491, -22.837104],
            [-69.315491, -22.751488],
            [-69.190006, -22.751488],
            [-69.190006, -22.837104],
            [-69.315491, -22.837104],
        ]
    ),
}

modis_rois = {
    "World": Polygon(
        [
            [-171.210938, -57.136239],
            [-171.210938, 79.997168],
            [177.539063, 79.997168],
            [177.539063, -57.136239],
            [-171.210938, -57.136239],
        ]
    ),
    "Africa": Polygon(
        [
            [-18.6983, 38.1446],
            [-18.6983, -36.1630],
            [52.2293, -36.1630],
            [52.2293, 38.1446],
        ]
    ),
    "USA": Polygon(
        [
            [-127.177734, 23.725012],
            [-127.177734, 50.792047],
            [-66.269531, 50.792047],
            [-66.269531, 23.725012],
            [-127.177734, 23.725012],
        ]
    ),
}

ocean_rois = {
    "Gulf of Mexico": Polygon(
        [
            [-101.206055, 15.496032],
            [-101.206055, 32.361403],
            [-75.673828, 32.361403],
            [-75.673828, 15.496032],
            [-101.206055, 15.496032],
        ]
    ),
    "North Atlantic Ocean": Polygon(
        [
            [-85.341797, 24.046464],
            [-85.341797, 45.02695],
            [-55.810547, 45.02695],
            [-55.810547, 24.046464],
            [-85.341797, 24.046464],
        ]
    ),
    "World": Polygon(
        [
            [-171.210938, -57.136239],
            [-171.210938, 79.997168],
            [177.539063, 79.997168],
            [177.539063, -57.136239],
            [-171.210938, -57.136239],
        ]
    ),
}


@st.cache_data
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
        fiona.drvsupport.supported_drivers["KML"] = "rw"
        gdf = gpd.read_file(file_path, driver="KML")
    else:
        gdf = gpd.read_file(file_path)

    return gdf


def app():

    today = date.today()

    st.title("Create Satellite Timelapse")

    st.markdown(
        """
        An interactive web app for creating [Landsat](https://developers.google.com/earth-engine/datasets/catalog/landsat)/[GOES](https://jstnbraaten.medium.com/goes-in-earth-engine-53fbc8783c16) timelapse for any location around the globe. 
        The app was built using [streamlit](https://streamlit.io), [geemap](https://geemap.org), and [Google Earth Engine](https://earthengine.google.com). For more info, check out my streamlit [blog post](https://blog.streamlit.io/creating-satellite-timelapse-with-streamlit-and-earth-engine). 
    """
    )

    row1_col1, row1_col2 = st.columns([2, 1])

    if st.session_state.get("zoom_level") is None:
        st.session_state["zoom_level"] = 4

    st.session_state["ee_asset_id"] = None
    st.session_state["bands"] = None
    st.session_state["palette"] = None
    st.session_state["vis_params"] = None

    with row1_col1:
        ee_authenticate(token_name="EARTHENGINE_TOKEN")
        m = geemap.Map(
            basemap="HYBRID",
            plugin_Draw=True,
            Draw_export=True,
            locate_control=True,
            plugin_LatLngPopup=False,
        )
        m.add_basemap("ROADMAP")

    with row1_col2:

        keyword = st.text_input("Search for a location:", "")
        if keyword:
            locations = geemap.geocode(keyword)
            if locations is not None and len(locations) > 0:
                str_locations = [str(g)[1:-1] for g in locations]
                location = st.selectbox("Select a location:", str_locations)
                loc_index = str_locations.index(location)
                selected_loc = locations[loc_index]
                lat, lng = selected_loc.lat, selected_loc.lng
                folium.Marker(location=[lat, lng], popup=location).add_to(m)
                m.set_center(lng, lat, 12)
                st.session_state["zoom_level"] = 12

        collection = st.selectbox(
            "Select a satellite image collection: ",
            [
                "Any Earth Engine ImageCollection",
                "Landsat TM-ETM-OLI Surface Reflectance",
                "Sentinel-2 MSI Surface Reflectance",
                "Geostationary Operational Environmental Satellites (GOES)",
                "MODIS Vegetation Indices (NDVI/EVI) 16-Day Global 1km",
                "MODIS Gap filled Land Surface Temperature Daily",
                "MODIS Ocean Color SMI",
                "USDA National Agriculture Imagery Program (NAIP)",
            ],
            index=1,
        )

        if collection in [
            "Landsat TM-ETM-OLI Surface Reflectance",
            "Sentinel-2 MSI Surface Reflectance",
        ]:
            roi_options = ["Uploaded GeoJSON"] + list(landsat_rois.keys())

        elif collection == "Geostationary Operational Environmental Satellites (GOES)":
            roi_options = ["Uploaded GeoJSON"] + list(goes_rois.keys())

        elif collection in [
            "MODIS Vegetation Indices (NDVI/EVI) 16-Day Global 1km",
            "MODIS Gap filled Land Surface Temperature Daily",
        ]:
            roi_options = ["Uploaded GeoJSON"] + list(modis_rois.keys())
        elif collection == "MODIS Ocean Color SMI":
            roi_options = ["Uploaded GeoJSON"] + list(ocean_rois.keys())
        else:
            roi_options = ["Uploaded GeoJSON"]

        if collection == "Any Earth Engine ImageCollection":
            keyword = st.text_input("Enter a keyword to search (e.g., MODIS):", "")
            if keyword:

                assets = geemap.search_ee_data(keyword)
                ee_assets = []
                for asset in assets:
                    if asset["ee_id_snippet"].startswith("ee.ImageCollection"):
                        ee_assets.append(asset)

                asset_titles = [x["title"] for x in ee_assets]
                dataset = st.selectbox("Select a dataset:", asset_titles)
                if len(ee_assets) > 0:
                    st.session_state["ee_assets"] = ee_assets
                    st.session_state["asset_titles"] = asset_titles
                    index = asset_titles.index(dataset)
                    ee_id = ee_assets[index]["id"]
                else:
                    ee_id = ""

                if dataset is not None:
                    with st.expander("Show dataset details", False):
                        index = asset_titles.index(dataset)
                        html = geemap.ee_data_html(st.session_state["ee_assets"][index])
                        st.markdown(html, True)
            # elif collection == "MODIS Gap filled Land Surface Temperature Daily":
            #     ee_id = ""
            else:
                ee_id = ""

            asset_id = st.text_input("Enter an ee.ImageCollection asset ID:", ee_id)

            if asset_id:
                with st.expander("Customize band combination and color palette", True):
                    try:
                        col = ee.ImageCollection.load(asset_id)
                        st.session_state["ee_asset_id"] = asset_id
                    except:
                        st.error("Invalid Earth Engine asset ID.")
                        st.session_state["ee_asset_id"] = None
                        return

                    img_bands = col.first().bandNames().getInfo()
                    if len(img_bands) >= 3:
                        default_bands = img_bands[:3][::-1]
                    else:
                        default_bands = img_bands[:]
                    bands = st.multiselect(
                        "Select one or three bands (RGB):", img_bands, default_bands
                    )
                    st.session_state["bands"] = bands

                    if len(bands) == 1:
                        palette_options = st.selectbox(
                            "Color palette",
                            cm.list_colormaps(),
                            index=2,
                        )
                        palette_values = cm.get_palette(palette_options, 15)
                        palette = st.text_area(
                            "Enter a custom palette:",
                            palette_values,
                        )
                        st.write(
                            cm.plot_colormap(cmap=palette_options, return_fig=True)
                        )
                        st.session_state["palette"] = eval(palette)

                    if bands:
                        vis_params = st.text_area(
                            "Enter visualization parameters",
                            "{'bands': ["
                            + ", ".join([f"'{band}'" for band in bands])
                            + "]}",
                        )
                    else:
                        vis_params = st.text_area(
                            "Enter visualization parameters",
                            "{}",
                        )
                    try:
                        st.session_state["vis_params"] = eval(vis_params)
                        st.session_state["vis_params"]["palette"] = st.session_state[
                            "palette"
                        ]
                    except Exception as e:
                        st.session_state["vis_params"] = None
                        st.error(
                            f"Invalid visualization parameters. It must be a dictionary."
                        )

        elif collection == "MODIS Gap filled Land Surface Temperature Daily":
            with st.expander("Show dataset details", False):
                st.markdown(
                    """
                See the [Awesome GEE Community Datasets](https://samapriya.github.io/awesome-gee-community-datasets/projects/daily_lst/).
                """
                )

            MODIS_options = ["Daytime (1:30 pm)", "Nighttime (1:30 am)"]
            MODIS_option = st.selectbox("Select a MODIS dataset:", MODIS_options)
            if MODIS_option == "Daytime (1:30 pm)":
                st.session_state[
                    "ee_asset_id"
                ] = "projects/sat-io/open-datasets/gap-filled-lst/gf_day_1km"
            else:
                st.session_state[
                    "ee_asset_id"
                ] = "projects/sat-io/open-datasets/gap-filled-lst/gf_night_1km"

            palette_options = st.selectbox(
                "Color palette",
                cm.list_colormaps(),
                index=90,
            )
            palette_values = cm.get_palette(palette_options, 15)
            palette = st.text_area(
                "Enter a custom palette:",
                palette_values,
            )
            st.write(cm.plot_colormap(cmap=palette_options, return_fig=True))
            st.session_state["palette"] = eval(palette)
        elif collection == "MODIS Ocean Color SMI":
            with st.expander("Show dataset details", False):
                st.markdown(
                    """
                See the [Earth Engine Data Catalog](https://developers.google.com/earth-engine/datasets/catalog/NASA_OCEANDATA_MODIS-Aqua_L3SMI).
                """
                )

            MODIS_options = ["Aqua", "Terra"]
            MODIS_option = st.selectbox("Select a satellite:", MODIS_options)
            st.session_state["ee_asset_id"] = MODIS_option
            # if MODIS_option == "Daytime (1:30 pm)":
            #     st.session_state[
            #         "ee_asset_id"
            #     ] = "projects/sat-io/open-datasets/gap-filled-lst/gf_day_1km"
            # else:
            #     st.session_state[
            #         "ee_asset_id"
            #     ] = "projects/sat-io/open-datasets/gap-filled-lst/gf_night_1km"

            band_dict = {
                "Chlorophyll a concentration": "chlor_a",
                "Normalized fluorescence line height": "nflh",
                "Particulate organic carbon": "poc",
                "Sea surface temperature": "sst",
                "Remote sensing reflectance at band 412nm": "Rrs_412",
                "Remote sensing reflectance at band 443nm": "Rrs_443",
                "Remote sensing reflectance at band 469nm": "Rrs_469",
                "Remote sensing reflectance at band 488nm": "Rrs_488",
                "Remote sensing reflectance at band 531nm": "Rrs_531",
                "Remote sensing reflectance at band 547nm": "Rrs_547",
                "Remote sensing reflectance at band 555nm": "Rrs_555",
                "Remote sensing reflectance at band 645nm": "Rrs_645",
                "Remote sensing reflectance at band 667nm": "Rrs_667",
                "Remote sensing reflectance at band 678nm": "Rrs_678",
            }

            band_options = list(band_dict.keys())
            band = st.selectbox(
                "Select a band",
                band_options,
                band_options.index("Sea surface temperature"),
            )
            st.session_state["band"] = band_dict[band]

            colors = cm.list_colormaps()
            palette_options = st.selectbox(
                "Color palette",
                colors,
                index=colors.index("coolwarm"),
            )
            palette_values = cm.get_palette(palette_options, 15)
            palette = st.text_area(
                "Enter a custom palette:",
                palette_values,
            )
            st.write(cm.plot_colormap(cmap=palette_options, return_fig=True))
            st.session_state["palette"] = eval(palette)

        sample_roi = st.selectbox(
            "Select a sample ROI or upload a GeoJSON file:",
            roi_options,
            index=0,
        )

        add_outline = st.checkbox(
            "Overlay an administrative boundary on timelapse", False
        )

        if add_outline:

            with st.expander("Customize administrative boundary", True):

                overlay_options = {
                    "User-defined": None,
                    "Continents": "continents",
                    "Countries": "countries",
                    "US States": "us_states",
                    "China": "china",
                }

                overlay = st.selectbox(
                    "Select an administrative boundary:",
                    list(overlay_options.keys()),
                    index=2,
                )

                overlay_data = overlay_options[overlay]

                if overlay_data is None:
                    overlay_data = st.text_input(
                        "Enter an HTTP URL to a GeoJSON file or an ee.FeatureCollection asset id:",
                        "https://raw.githubusercontent.com/giswqs/geemap/master/examples/data/countries.geojson",
                    )

                overlay_color = st.color_picker(
                    "Select a color for the administrative boundary:", "#000000"
                )
                overlay_width = st.slider(
                    "Select a line width for the administrative boundary:", 1, 20, 1
                )
                overlay_opacity = st.slider(
                    "Select an opacity for the administrative boundary:",
                    0.0,
                    1.0,
                    1.0,
                    0.05,
                )
        else:
            overlay_data = None
            overlay_color = "black"
            overlay_width = 1
            overlay_opacity = 1

    with row1_col1:

        with st.expander(
            "Steps: Draw a rectangle on the map -> Export it as a GeoJSON -> Upload it back to the app -> Click the Submit button. Expand this tab to see a demo 👉"
        ):
            video_empty = st.empty()

        data = st.file_uploader(
            "Upload a GeoJSON file to use as an ROI. Customize timelapse parameters and then click the Submit button 😇👇",
            type=["geojson", "kml", "zip"],
        )

        crs = "epsg:4326"
        if sample_roi == "Uploaded GeoJSON":
            if data is None:
                # st.info(
                #     "Steps to create a timelapse: Draw a rectangle on the map -> Export it as a GeoJSON -> Upload it back to the app -> Click Submit button"
                # )
                if collection in [
                    "Geostationary Operational Environmental Satellites (GOES)",
                    "USDA National Agriculture Imagery Program (NAIP)",
                ] and (not keyword):
                    m.set_center(-100, 40, 3)
                # else:
                #     m.set_center(4.20, 18.63, zoom=2)
        else:
            if collection in [
                "Landsat TM-ETM-OLI Surface Reflectance",
                "Sentinel-2 MSI Surface Reflectance",
            ]:
                gdf = gpd.GeoDataFrame(
                    index=[0], crs=crs, geometry=[landsat_rois[sample_roi]]
                )
            elif (
                collection
                == "Geostationary Operational Environmental Satellites (GOES)"
            ):
                gdf = gpd.GeoDataFrame(
                    index=[0], crs=crs, geometry=[goes_rois[sample_roi]["region"]]
                )
            elif collection == "MODIS Vegetation Indices (NDVI/EVI) 16-Day Global 1km":
                gdf = gpd.GeoDataFrame(
                    index=[0], crs=crs, geometry=[modis_rois[sample_roi]]
                )

        if sample_roi != "Uploaded GeoJSON":

            if collection in [
                "Landsat TM-ETM-OLI Surface Reflectance",
                "Sentinel-2 MSI Surface Reflectance",
            ]:
                gdf = gpd.GeoDataFrame(
                    index=[0], crs=crs, geometry=[landsat_rois[sample_roi]]
                )
            elif (
                collection
                == "Geostationary Operational Environmental Satellites (GOES)"
            ):
                gdf = gpd.GeoDataFrame(
                    index=[0], crs=crs, geometry=[goes_rois[sample_roi]["region"]]
                )
            elif collection in [
                "MODIS Vegetation Indices (NDVI/EVI) 16-Day Global 1km",
                "MODIS Gap filled Land Surface Temperature Daily",
            ]:
                gdf = gpd.GeoDataFrame(
                    index=[0], crs=crs, geometry=[modis_rois[sample_roi]]
                )
            elif collection == "MODIS Ocean Color SMI":
                gdf = gpd.GeoDataFrame(
                    index=[0], crs=crs, geometry=[ocean_rois[sample_roi]]
                )
            try:
                st.session_state["roi"] = geemap.gdf_to_ee(gdf, geodesic=False)
            except Exception as e:
                st.error(e)
                st.error("Please draw another ROI and try again.")
                return
            m.add_gdf(gdf, "ROI")

        elif data:
            gdf = uploaded_file_to_gdf(data)
            try:
                st.session_state["roi"] = geemap.gdf_to_ee(gdf, geodesic=False)
                m.add_gdf(gdf, "ROI")
            except Exception as e:
                st.error(e)
                st.error("Please draw another ROI and try again.")
                return

        m.to_streamlit(height=600)

    with row1_col2:

        if collection in [
            "Landsat TM-ETM-OLI Surface Reflectance",
            "Sentinel-2 MSI Surface Reflectance",
        ]:

            if collection == "Landsat TM-ETM-OLI Surface Reflectance":
                sensor_start_year = 1984
                timelapse_title = "Landsat Timelapse"
                timelapse_speed = 5
            elif collection == "Sentinel-2 MSI Surface Reflectance":
                sensor_start_year = 2015
                timelapse_title = "Sentinel-2 Timelapse"
                timelapse_speed = 5
            video_empty.video("https://youtu.be/VVRK_-dEjR4")

            with st.form("submit_landsat_form"):

                roi = None
                if st.session_state.get("roi") is not None:
                    roi = st.session_state.get("roi")
                out_gif = geemap.temp_file_path(".gif")

                title = st.text_input(
                    "Enter a title to show on the timelapse: ", timelapse_title
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
                        "SWIR2/NIR/SWIR1",
                        "SWIR1/NIR/SWIR2",
                    ],
                    index=9,
                )

                frequency = st.selectbox(
                    "Select a temporal frequency:",
                    ["year", "quarter", "month"],
                    index=0,
                )

                with st.expander("Customize timelapse"):

                    speed = st.slider("Frames per second:", 1, 30, timelapse_speed)
                    dimensions = st.slider(
                        "Maximum dimensions (Width*Height) in pixels", 768, 2000, 768
                    )
                    progress_bar_color = st.color_picker(
                        "Progress bar color:", "#0000ff"
                    )
                    years = st.slider(
                        "Start and end year:",
                        sensor_start_year,
                        today.year,
                        (sensor_start_year, today.year),
                    )
                    months = st.slider("Start and end month:", 1, 12, (1, 12))
                    font_size = st.slider("Font size:", 10, 50, 30)
                    font_color = st.color_picker("Font color:", "#ffffff")
                    apply_fmask = st.checkbox(
                        "Apply fmask (remove clouds, shadows, snow)", True
                    )
                    font_type = st.selectbox(
                        "Select the font type for the title:",
                        ["arial.ttf", "alibaba.otf"],
                        index=0,
                    )
                    fading = st.slider(
                        "Fading duration (seconds) for each frame:", 0.0, 3.0, 0.0
                    )
                    mp4 = st.checkbox("Save timelapse as MP4", True)

                empty_text = st.empty()
                empty_image = st.empty()
                empty_fire_image = st.empty()
                empty_video = st.container()
                submitted = st.form_submit_button("Submit")
                if submitted:

                    if sample_roi == "Uploaded GeoJSON" and data is None:
                        empty_text.warning(
                            "Steps to create a timelapse: Draw a rectangle on the map -> Export it as a GeoJSON -> Upload it back to the app -> Click the Submit button. Alternatively, you can select a sample ROI from the dropdown list."
                        )
                    else:

                        empty_text.text("Computing... Please wait...")

                        start_year = years[0]
                        end_year = years[1]
                        start_date = str(months[0]).zfill(2) + "-01"
                        end_date = str(months[1]).zfill(2) + "-30"
                        bands = RGB.split("/")

                        try:
                            if collection == "Landsat TM-ETM-OLI Surface Reflectance":
                                out_gif = geemap.landsat_timelapse(
                                    roi=roi,
                                    out_gif=out_gif,
                                    start_year=start_year,
                                    end_year=end_year,
                                    start_date=start_date,
                                    end_date=end_date,
                                    bands=bands,
                                    apply_fmask=apply_fmask,
                                    frames_per_second=speed,
                                    # dimensions=dimensions,
                                    dimensions=768,
                                    overlay_data=overlay_data,
                                    overlay_color=overlay_color,
                                    overlay_width=overlay_width,
                                    overlay_opacity=overlay_opacity,
                                    frequency=frequency,
                                    date_format=None,
                                    title=title,
                                    title_xy=("2%", "90%"),
                                    add_text=True,
                                    text_xy=("2%", "2%"),
                                    text_sequence=None,
                                    font_type=font_type,
                                    font_size=font_size,
                                    font_color=font_color,
                                    add_progress_bar=True,
                                    progress_bar_color=progress_bar_color,
                                    progress_bar_height=5,
                                    loop=0,
                                    mp4=mp4,
                                    fading=fading,
                                )
                            elif collection == "Sentinel-2 MSI Surface Reflectance":
                                out_gif = geemap.sentinel2_timelapse(
                                    roi=roi,
                                    out_gif=out_gif,
                                    start_year=start_year,
                                    end_year=end_year,
                                    start_date=start_date,
                                    end_date=end_date,
                                    bands=bands,
                                    apply_fmask=apply_fmask,
                                    frames_per_second=speed,
                                    dimensions=768,
                                    # dimensions=dimensions,
                                    overlay_data=overlay_data,
                                    overlay_color=overlay_color,
                                    overlay_width=overlay_width,
                                    overlay_opacity=overlay_opacity,
                                    frequency=frequency,
                                    date_format=None,
                                    title=title,
                                    title_xy=("2%", "90%"),
                                    add_text=True,
                                    text_xy=("2%", "2%"),
                                    text_sequence=None,
                                    font_type=font_type,
                                    font_size=font_size,
                                    font_color=font_color,
                                    add_progress_bar=True,
                                    progress_bar_color=progress_bar_color,
                                    progress_bar_height=5,
                                    loop=0,
                                    mp4=mp4,
                                    fading=fading,
                                )
                        except:
                            empty_text.error(
                                "An error occurred while computing the timelapse. Your probably requested too much data. Try reducing the ROI or timespan."
                            )
                            st.stop()

                        if out_gif is not None and os.path.exists(out_gif):

                            empty_text.text(
                                "Right click the GIF to save it to your computer👇"
                            )
                            empty_image.image(out_gif)

                            out_mp4 = out_gif.replace(".gif", ".mp4")
                            if mp4 and os.path.exists(out_mp4):
                                with empty_video:
                                    st.text(
                                        "Right click the MP4 to save it to your computer👇"
                                    )
                                    st.video(out_gif.replace(".gif", ".mp4"))

                        else:
                            empty_text.error(
                                "Something went wrong. You probably requested too much data. Try reducing the ROI or timespan."
                            )

        elif collection == "Geostationary Operational Environmental Satellites (GOES)":

            video_empty.video("https://youtu.be/16fA2QORG4A")

            with st.form("submit_goes_form"):

                roi = None
                if st.session_state.get("roi") is not None:
                    roi = st.session_state.get("roi")
                out_gif = geemap.temp_file_path(".gif")

                satellite = st.selectbox("Select a satellite:", ["GOES-17", "GOES-16"])
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
                        roi_start[:10], "%Y-%m-%d"
                    )
                    roi_end_date = datetime.datetime.strptime(roi_end[:10], "%Y-%m-%d")
                    roi_start_time = datetime.time(
                        int(roi_start[11:13]), int(roi_start[14:16])
                    )
                    roi_end_time = datetime.time(
                        int(roi_end[11:13]), int(roi_end[14:16])
                    )

                start_date = st.date_input("Select the start date:", roi_start_date)
                end_date = st.date_input("Select the end date:", roi_end_date)

                with st.expander("Customize timelapse"):

                    add_fire = st.checkbox("Add Fire/Hotspot Characterization", False)

                    scan_type = st.selectbox(
                        "Select a scan type:", ["Full Disk", "CONUS", "Mesoscale"]
                    )

                    start_time = st.time_input(
                        "Select the start time of the start date:", roi_start_time
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

                    speed = st.slider("Frames per second:", 1, 30, 5)
                    add_progress_bar = st.checkbox("Add a progress bar", True)
                    progress_bar_color = st.color_picker(
                        "Progress bar color:", "#0000ff"
                    )
                    font_size = st.slider("Font size:", 10, 50, 20)
                    font_color = st.color_picker("Font color:", "#ffffff")
                    fading = st.slider(
                        "Fading duration (seconds) for each frame:", 0.0, 3.0, 0.0
                    )
                    mp4 = st.checkbox("Save timelapse as MP4", True)

                empty_text = st.empty()
                empty_image = st.empty()
                empty_video = st.container()
                empty_fire_text = st.empty()
                empty_fire_image = st.empty()

                submitted = st.form_submit_button("Submit")
                if submitted:
                    if sample_roi == "Uploaded GeoJSON" and data is None:
                        empty_text.warning(
                            "Steps to create a timelapse: Draw a rectangle on the map -> Export it as a GeoJSON -> Upload it back to the app -> Click the Submit button. Alternatively, you can select a sample ROI from the dropdown list."
                        )
                    else:
                        empty_text.text("Computing... Please wait...")

                        geemap.goes_timelapse(
                            roi,
                            out_gif,
                            start_date=start,
                            end_date=end,
                            data=satellite,
                            scan=scan_type.replace(" ", "_").lower(),
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
                            overlay_data=overlay_data,
                            overlay_color=overlay_color,
                            overlay_width=overlay_width,
                            overlay_opacity=overlay_opacity,
                            mp4=mp4,
                            fading=fading,
                        )

                        if out_gif is not None and os.path.exists(out_gif):
                            empty_text.text(
                                "Right click the GIF to save it to your computer👇"
                            )
                            empty_image.image(out_gif)

                            out_mp4 = out_gif.replace(".gif", ".mp4")
                            if mp4 and os.path.exists(out_mp4):
                                with empty_video:
                                    st.text(
                                        "Right click the MP4 to save it to your computer👇"
                                    )
                                    st.video(out_gif.replace(".gif", ".mp4"))

                            if add_fire:
                                out_fire_gif = geemap.temp_file_path(".gif")
                                empty_fire_text.text(
                                    "Delineating Fire Hotspot... Please wait..."
                                )
                                geemap.goes_fire_timelapse(
                                    out_fire_gif,
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
                                if os.path.exists(out_fire_gif):
                                    empty_fire_image.image(out_fire_gif)
                        else:
                            empty_text.text(
                                "Something went wrong, either the ROI is too big or there are no data available for the specified date range. Please try a smaller ROI or different date range."
                            )

        elif collection == "MODIS Vegetation Indices (NDVI/EVI) 16-Day Global 1km":

            video_empty.video("https://youtu.be/16fA2QORG4A")

            satellite = st.selectbox("Select a satellite:", ["Terra", "Aqua"])
            band = st.selectbox("Select a band:", ["NDVI", "EVI"])

            with st.form("submit_modis_form"):

                roi = None
                if st.session_state.get("roi") is not None:
                    roi = st.session_state.get("roi")
                out_gif = geemap.temp_file_path(".gif")

                with st.expander("Customize timelapse"):

                    start = st.date_input(
                        "Select a start date:", datetime.date(2000, 2, 8)
                    )
                    end = st.date_input("Select an end date:", datetime.date.today())

                    start_date = start.strftime("%Y-%m-%d")
                    end_date = end.strftime("%Y-%m-%d")

                    speed = st.slider("Frames per second:", 1, 30, 5)
                    add_progress_bar = st.checkbox("Add a progress bar", True)
                    progress_bar_color = st.color_picker(
                        "Progress bar color:", "#0000ff"
                    )
                    font_size = st.slider("Font size:", 10, 50, 20)
                    font_color = st.color_picker("Font color:", "#ffffff")

                    font_type = st.selectbox(
                        "Select the font type for the title:",
                        ["arial.ttf", "alibaba.otf"],
                        index=0,
                    )
                    fading = st.slider(
                        "Fading duration (seconds) for each frame:", 0.0, 3.0, 0.0
                    )
                    mp4 = st.checkbox("Save timelapse as MP4", True)

                empty_text = st.empty()
                empty_image = st.empty()
                empty_video = st.container()

                submitted = st.form_submit_button("Submit")
                if submitted:
                    if sample_roi == "Uploaded GeoJSON" and data is None:
                        empty_text.warning(
                            "Steps to create a timelapse: Draw a rectangle on the map -> Export it as a GeoJSON -> Upload it back to the app -> Click the Submit button. Alternatively, you can select a sample ROI from the dropdown list."
                        )
                    else:

                        empty_text.text("Computing... Please wait...")

                        geemap.modis_ndvi_timelapse(
                            roi,
                            out_gif,
                            satellite,
                            band,
                            start_date,
                            end_date,
                            768,
                            speed,
                            overlay_data=overlay_data,
                            overlay_color=overlay_color,
                            overlay_width=overlay_width,
                            overlay_opacity=overlay_opacity,
                            mp4=mp4,
                            fading=fading,
                        )

                        geemap.reduce_gif_size(out_gif)

                        empty_text.text(
                            "Right click the GIF to save it to your computer👇"
                        )
                        empty_image.image(out_gif)

                        out_mp4 = out_gif.replace(".gif", ".mp4")
                        if mp4 and os.path.exists(out_mp4):
                            with empty_video:
                                st.text(
                                    "Right click the MP4 to save it to your computer👇"
                                )
                                st.video(out_gif.replace(".gif", ".mp4"))

        elif collection == "Any Earth Engine ImageCollection":

            with st.form("submit_ts_form"):
                with st.expander("Customize timelapse"):

                    title = st.text_input(
                        "Enter a title to show on the timelapse: ", "Timelapse"
                    )
                    start_date = st.date_input(
                        "Select the start date:", datetime.date(2020, 1, 1)
                    )
                    end_date = st.date_input(
                        "Select the end date:", datetime.date.today()
                    )
                    frequency = st.selectbox(
                        "Select a temporal frequency:",
                        ["year", "quarter", "month", "day", "hour", "minute", "second"],
                        index=0,
                    )
                    reducer = st.selectbox(
                        "Select a reducer for aggregating data:",
                        ["median", "mean", "min", "max", "sum", "variance", "stdDev"],
                        index=0,
                    )
                    data_format = st.selectbox(
                        "Select a date format to show on the timelapse:",
                        [
                            "YYYY-MM-dd",
                            "YYYY",
                            "YYMM-MM",
                            "YYYY-MM-dd HH:mm",
                            "YYYY-MM-dd HH:mm:ss",
                            "HH:mm",
                            "HH:mm:ss",
                            "w",
                            "M",
                            "d",
                            "D",
                        ],
                        index=0,
                    )

                    speed = st.slider("Frames per second:", 1, 30, 5)
                    add_progress_bar = st.checkbox("Add a progress bar", True)
                    progress_bar_color = st.color_picker(
                        "Progress bar color:", "#0000ff"
                    )
                    font_size = st.slider("Font size:", 10, 50, 30)
                    font_color = st.color_picker("Font color:", "#ffffff")
                    font_type = st.selectbox(
                        "Select the font type for the title:",
                        ["arial.ttf", "alibaba.otf"],
                        index=0,
                    )
                    fading = st.slider(
                        "Fading duration (seconds) for each frame:", 0.0, 3.0, 0.0
                    )
                    mp4 = st.checkbox("Save timelapse as MP4", True)

                empty_text = st.empty()
                empty_image = st.empty()
                empty_video = st.container()
                empty_fire_image = st.empty()

                roi = None
                if st.session_state.get("roi") is not None:
                    roi = st.session_state.get("roi")
                out_gif = geemap.temp_file_path(".gif")

                submitted = st.form_submit_button("Submit")
                if submitted:

                    if sample_roi == "Uploaded GeoJSON" and data is None:
                        empty_text.warning(
                            "Steps to create a timelapse: Draw a rectangle on the map -> Export it as a GeoJSON -> Upload it back to the app -> Click the Submit button. Alternatively, you can select a sample ROI from the dropdown list."
                        )
                    else:

                        empty_text.text("Computing... Please wait...")
                        try:
                            geemap.create_timelapse(
                                st.session_state.get("ee_asset_id"),
                                start_date=start_date.strftime("%Y-%m-%d"),
                                end_date=end_date.strftime("%Y-%m-%d"),
                                region=roi,
                                frequency=frequency,
                                reducer=reducer,
                                date_format=data_format,
                                out_gif=out_gif,
                                bands=st.session_state.get("bands"),
                                palette=st.session_state.get("palette"),
                                vis_params=st.session_state.get("vis_params"),
                                dimensions=768,
                                frames_per_second=speed,
                                crs="EPSG:3857",
                                overlay_data=overlay_data,
                                overlay_color=overlay_color,
                                overlay_width=overlay_width,
                                overlay_opacity=overlay_opacity,
                                title=title,
                                title_xy=("2%", "90%"),
                                add_text=True,
                                text_xy=("2%", "2%"),
                                text_sequence=None,
                                font_type=font_type,
                                font_size=font_size,
                                font_color=font_color,
                                add_progress_bar=add_progress_bar,
                                progress_bar_color=progress_bar_color,
                                progress_bar_height=5,
                                loop=0,
                                mp4=mp4,
                                fading=fading,
                            )
                        except:
                            empty_text.error(
                                "An error occurred while computing the timelapse. You probably requested too much data. Try reducing the ROI or timespan."
                            )

                        empty_text.text(
                            "Right click the GIF to save it to your computer👇"
                        )
                        empty_image.image(out_gif)

                        out_mp4 = out_gif.replace(".gif", ".mp4")
                        if mp4 and os.path.exists(out_mp4):
                            with empty_video:
                                st.text(
                                    "Right click the MP4 to save it to your computer👇"
                                )
                                st.video(out_gif.replace(".gif", ".mp4"))

        elif collection in [
            "MODIS Gap filled Land Surface Temperature Daily",
            "MODIS Ocean Color SMI",
        ]:

            with st.form("submit_ts_form"):
                with st.expander("Customize timelapse"):

                    title = st.text_input(
                        "Enter a title to show on the timelapse: ",
                        "Surface Temperature",
                    )
                    start_date = st.date_input(
                        "Select the start date:", datetime.date(2018, 1, 1)
                    )
                    end_date = st.date_input(
                        "Select the end date:", datetime.date(2020, 12, 31)
                    )
                    frequency = st.selectbox(
                        "Select a temporal frequency:",
                        ["year", "quarter", "month", "week", "day"],
                        index=2,
                    )
                    reducer = st.selectbox(
                        "Select a reducer for aggregating data:",
                        ["median", "mean", "min", "max", "sum", "variance", "stdDev"],
                        index=0,
                    )

                    vis_params = st.text_area(
                        "Enter visualization parameters",
                        "",
                        help="Enter a string in the format of a dictionary, such as '{'min': 23, 'max': 32}'",
                    )

                    speed = st.slider("Frames per second:", 1, 30, 5)
                    add_progress_bar = st.checkbox("Add a progress bar", True)
                    progress_bar_color = st.color_picker(
                        "Progress bar color:", "#0000ff"
                    )
                    font_size = st.slider("Font size:", 10, 50, 30)
                    font_color = st.color_picker("Font color:", "#ffffff")
                    font_type = st.selectbox(
                        "Select the font type for the title:",
                        ["arial.ttf", "alibaba.otf"],
                        index=0,
                    )
                    add_colorbar = st.checkbox("Add a colorbar", True)
                    colorbar_label = st.text_input(
                        "Enter the colorbar label:", "Surface Temperature (°C)"
                    )
                    fading = st.slider(
                        "Fading duration (seconds) for each frame:", 0.0, 3.0, 0.0
                    )
                    mp4 = st.checkbox("Save timelapse as MP4", True)

                empty_text = st.empty()
                empty_image = st.empty()
                empty_video = st.container()

                roi = None
                if st.session_state.get("roi") is not None:
                    roi = st.session_state.get("roi")
                out_gif = geemap.temp_file_path(".gif")

                submitted = st.form_submit_button("Submit")
                if submitted:

                    if sample_roi == "Uploaded GeoJSON" and data is None:
                        empty_text.warning(
                            "Steps to create a timelapse: Draw a rectangle on the map -> Export it as a GeoJSON -> Upload it back to the app -> Click the Submit button. Alternatively, you can select a sample ROI from the dropdown list."
                        )
                    else:

                        empty_text.text("Computing... Please wait...")
                        try:
                            if (
                                collection
                                == "MODIS Gap filled Land Surface Temperature Daily"
                            ):
                                out_gif = geemap.create_timelapse(
                                    st.session_state.get("ee_asset_id"),
                                    start_date=start_date.strftime("%Y-%m-%d"),
                                    end_date=end_date.strftime("%Y-%m-%d"),
                                    region=roi,
                                    bands=None,
                                    frequency=frequency,
                                    reducer=reducer,
                                    date_format=None,
                                    out_gif=out_gif,
                                    palette=st.session_state.get("palette"),
                                    vis_params=None,
                                    dimensions=768,
                                    frames_per_second=speed,
                                    crs="EPSG:3857",
                                    overlay_data=overlay_data,
                                    overlay_color=overlay_color,
                                    overlay_width=overlay_width,
                                    overlay_opacity=overlay_opacity,
                                    title=title,
                                    title_xy=("2%", "90%"),
                                    add_text=True,
                                    text_xy=("2%", "2%"),
                                    text_sequence=None,
                                    font_type=font_type,
                                    font_size=font_size,
                                    font_color=font_color,
                                    add_progress_bar=add_progress_bar,
                                    progress_bar_color=progress_bar_color,
                                    progress_bar_height=5,
                                    add_colorbar=add_colorbar,
                                    colorbar_label=colorbar_label,
                                    loop=0,
                                    mp4=mp4,
                                    fading=fading,
                                )
                            elif collection == "MODIS Ocean Color SMI":
                                if vis_params.startswith("{") and vis_params.endswith(
                                    "}"
                                ):
                                    vis_params = eval(vis_params)
                                else:
                                    vis_params = None
                                out_gif = geemap.modis_ocean_color_timelapse(
                                    st.session_state.get("ee_asset_id"),
                                    start_date=start_date.strftime("%Y-%m-%d"),
                                    end_date=end_date.strftime("%Y-%m-%d"),
                                    region=roi,
                                    bands=st.session_state["band"],
                                    frequency=frequency,
                                    reducer=reducer,
                                    date_format=None,
                                    out_gif=out_gif,
                                    palette=st.session_state.get("palette"),
                                    vis_params=vis_params,
                                    dimensions=768,
                                    frames_per_second=speed,
                                    crs="EPSG:3857",
                                    overlay_data=overlay_data,
                                    overlay_color=overlay_color,
                                    overlay_width=overlay_width,
                                    overlay_opacity=overlay_opacity,
                                    title=title,
                                    title_xy=("2%", "90%"),
                                    add_text=True,
                                    text_xy=("2%", "2%"),
                                    text_sequence=None,
                                    font_type=font_type,
                                    font_size=font_size,
                                    font_color=font_color,
                                    add_progress_bar=add_progress_bar,
                                    progress_bar_color=progress_bar_color,
                                    progress_bar_height=5,
                                    add_colorbar=add_colorbar,
                                    colorbar_label=colorbar_label,
                                    loop=0,
                                    mp4=mp4,
                                    fading=fading,
                                )
                        except:
                            empty_text.error(
                                "Something went wrong. You probably requested too much data. Try reducing the ROI or timespan."
                            )

                        if out_gif is not None and os.path.exists(out_gif):

                            geemap.reduce_gif_size(out_gif)

                            empty_text.text(
                                "Right click the GIF to save it to your computer👇"
                            )
                            empty_image.image(out_gif)

                            out_mp4 = out_gif.replace(".gif", ".mp4")
                            if mp4 and os.path.exists(out_mp4):
                                with empty_video:
                                    st.text(
                                        "Right click the MP4 to save it to your computer👇"
                                    )
                                    st.video(out_gif.replace(".gif", ".mp4"))

                        else:
                            st.error(
                                "Something went wrong. You probably requested too much data. Try reducing the ROI or timespan."
                            )

        elif collection == "USDA National Agriculture Imagery Program (NAIP)":

            with st.form("submit_naip_form"):
                with st.expander("Customize timelapse"):

                    title = st.text_input(
                        "Enter a title to show on the timelapse: ", "NAIP Timelapse"
                    )

                    years = st.slider(
                        "Start and end year:",
                        2003,
                        today.year,
                        (2003, today.year),
                    )

                    bands = st.selectbox(
                        "Select a band combination:", ["N/R/G", "R/G/B"], index=0
                    )

                    speed = st.slider("Frames per second:", 1, 30, 3)
                    add_progress_bar = st.checkbox("Add a progress bar", True)
                    progress_bar_color = st.color_picker(
                        "Progress bar color:", "#0000ff"
                    )
                    font_size = st.slider("Font size:", 10, 50, 30)
                    font_color = st.color_picker("Font color:", "#ffffff")
                    font_type = st.selectbox(
                        "Select the font type for the title:",
                        ["arial.ttf", "alibaba.otf"],
                        index=0,
                    )
                    fading = st.slider(
                        "Fading duration (seconds) for each frame:", 0.0, 3.0, 0.0
                    )
                    mp4 = st.checkbox("Save timelapse as MP4", True)

                empty_text = st.empty()
                empty_image = st.empty()
                empty_video = st.container()
                empty_fire_image = st.empty()

                roi = None
                if st.session_state.get("roi") is not None:
                    roi = st.session_state.get("roi")
                out_gif = geemap.temp_file_path(".gif")

                submitted = st.form_submit_button("Submit")
                if submitted:

                    if sample_roi == "Uploaded GeoJSON" and data is None:
                        empty_text.warning(
                            "Steps to create a timelapse: Draw a rectangle on the map -> Export it as a GeoJSON -> Upload it back to the app -> Click the Submit button. Alternatively, you can select a sample ROI from the dropdown list."
                        )
                    else:

                        empty_text.text("Computing... Please wait...")
                        try:
                            geemap.naip_timelapse(
                                roi,
                                years[0],
                                years[1],
                                out_gif,
                                bands=bands.split("/"),
                                palette=st.session_state.get("palette"),
                                vis_params=None,
                                dimensions=768,
                                frames_per_second=speed,
                                crs="EPSG:3857",
                                overlay_data=overlay_data,
                                overlay_color=overlay_color,
                                overlay_width=overlay_width,
                                overlay_opacity=overlay_opacity,
                                title=title,
                                title_xy=("2%", "90%"),
                                add_text=True,
                                text_xy=("2%", "2%"),
                                text_sequence=None,
                                font_type=font_type,
                                font_size=font_size,
                                font_color=font_color,
                                add_progress_bar=add_progress_bar,
                                progress_bar_color=progress_bar_color,
                                progress_bar_height=5,
                                loop=0,
                                mp4=mp4,
                                fading=fading,
                            )
                        except:
                            empty_text.error(
                                "Something went wrong. You either requested too much data or the ROI is outside the U.S."
                            )

                        if out_gif is not None and os.path.exists(out_gif):

                            empty_text.text(
                                "Right click the GIF to save it to your computer👇"
                            )
                            empty_image.image(out_gif)

                            out_mp4 = out_gif.replace(".gif", ".mp4")
                            if mp4 and os.path.exists(out_mp4):
                                with empty_video:
                                    st.text(
                                        "Right click the MP4 to save it to your computer👇"
                                    )
                                    st.video(out_gif.replace(".gif", ".mp4"))

                        else:
                            st.error(
                                "Something went wrong. You either requested too much data or the ROI is outside the U.S."
                            )


try:
    app()
except Exception as e:
    pass
