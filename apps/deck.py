import os
import streamlit as st
import pydeck as pdk
import pandas as pd


def globe_view():

    """
    GlobeView
    =========

    Over 33,000 power plants of the world plotted by their production capacity (given by height)
    and fuel type (green if renewable) on an experimental deck.gl GlobeView.
    """

    COUNTRIES = "https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_50m_admin_0_scale_rank.geojson"
    POWER_PLANTS = "https://raw.githubusercontent.com/ajduberstein/geo_datasets/master/global_power_plant_database.csv"

    df = pd.read_csv(POWER_PLANTS)

    def is_green(fuel_type):
        """Return a green RGB value if a facility uses a renewable fuel type"""
        if fuel_type.lower() in (
            "nuclear",
            "water",
            "wind",
            "hydro",
            "biomass",
            "solar",
            "geothermal",
        ):
            return [10, 230, 120]
        return [230, 158, 10]

    df["color"] = df["primary_fuel"].apply(is_green)

    view_state = pdk.ViewState(latitude=51.47, longitude=0.45, zoom=2, min_zoom=2)

    # Set height and width variables
    view = pdk.View(type="_GlobeView", controller=True, width=1000, height=700)

    layers = [
        pdk.Layer(
            "GeoJsonLayer",
            id="base-map",
            data=COUNTRIES,
            stroked=False,
            filled=True,
            get_fill_color=[200, 200, 200],
        ),
        pdk.Layer(
            "ColumnLayer",
            id="power-plant",
            data=df,
            get_elevation="capacity_mw",
            get_position=["longitude", "latitude"],
            elevation_scale=100,
            pickable=True,
            auto_highlight=True,
            radius=20000,
            get_fill_color="color",
        ),
    ]

    r = pdk.Deck(
        views=[view],
        initial_view_state=view_state,
        tooltip={"text": "{name}, {primary_fuel} plant, {country}"},
        layers=layers,
        # Note that this must be set for the globe to be opaque
        parameters={"cull": True},
    )

    return r


def geojson_layer():

    """
    GeoJsonLayer
    ===========

    Property values in Vancouver, Canada, adapted from the deck.gl example pages. Input data is in a GeoJSON format.
    """

    DATA_URL = "https://raw.githubusercontent.com/visgl/deck.gl-data/master/examples/geojson/vancouver-blocks.json"
    LAND_COVER = [
        [[-123.0, 49.196], [-123.0, 49.324], [-123.306, 49.324], [-123.306, 49.196]]
    ]

    INITIAL_VIEW_STATE = pdk.ViewState(
        latitude=49.254, longitude=-123.13, zoom=11, max_zoom=16, pitch=45, bearing=0
    )

    polygon = pdk.Layer(
        "PolygonLayer",
        LAND_COVER,
        stroked=False,
        # processes the data as a flat longitude-latitude pair
        get_polygon="-",
        get_fill_color=[0, 0, 0, 20],
    )

    geojson = pdk.Layer(
        "GeoJsonLayer",
        DATA_URL,
        opacity=0.8,
        stroked=False,
        filled=True,
        extruded=True,
        wireframe=True,
        get_elevation="properties.valuePerSqm / 20",
        get_fill_color="[255, 255, properties.growth * 255]",
        get_line_color=[255, 255, 255],
    )

    r = pdk.Deck(layers=[polygon, geojson], initial_view_state=INITIAL_VIEW_STATE)
    return r


def terrain():

    """
    TerrainLayer
    ===========

    Extruded terrain using AWS Open Data Terrain Tiles and Mapbox Satellite imagery
    """

    # Import Mapbox API Key from environment
    MAPBOX_API_KEY = os.environ["MAPBOX_API_KEY"]

    # AWS Open Data Terrain Tiles
    TERRAIN_IMAGE = (
        "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
    )

    # Define how to parse elevation tiles
    ELEVATION_DECODER = {
        "rScaler": 256,
        "gScaler": 1,
        "bScaler": 1 / 256,
        "offset": -32768,
    }

    SURFACE_IMAGE = f"https://api.mapbox.com/v4/mapbox.satellite/{{z}}/{{x}}/{{y}}@2x.png?access_token={MAPBOX_API_KEY}"

    terrain_layer = pdk.Layer(
        "TerrainLayer",
        elevation_decoder=ELEVATION_DECODER,
        texture=SURFACE_IMAGE,
        elevation_data=TERRAIN_IMAGE,
    )

    view_state = pdk.ViewState(
        latitude=46.24, longitude=-122.18, zoom=11.5, bearing=140, pitch=60
    )

    r = pdk.Deck(terrain_layer, initial_view_state=view_state)
    return r


def app():

    st.title("Pydeck Gallery")

    options = ["GeoJsonLayer", "GlobeView", "TerrainLayer"]

    option = st.selectbox("Select a pydeck layer type", options)

    if option == "GeoJsonLayer":
        st.header("Property values in Vancouver, Canada")
        st.pydeck_chart(geojson_layer())
    # elif option == "GlobeView":
    #     st.pydeck_chart(globe_view())
    elif option == "TerrainLayer":
        st.pydeck_chart(terrain())
