import os
import pandas as pd
import pydeck as pdk
import geopandas as gpd
import streamlit as st
import leafmap.colormaps as cm
import matplotlib.pyplot as plt
from leafmap.common import to_hex_colors, hex_to_rgb
import matplotlib as mpl

# Data source: https://www.realtor.com/research/data/
link_prefix = "https://econdata.s3-us-west-2.amazonaws.com/Reports/"

data_links = {
    "weekly": {
        "national": link_prefix + "Core/listing_weekly_core_aggregate_by_country.csv",
        "metro": link_prefix + "Core/listing_weekly_core_aggregate_by_metro.csv",
    },
    "monthly_current": {
        "national": link_prefix + "Core/RDC_Inventory_Core_Metrics_Country.csv",
        "state": link_prefix + "Core/RDC_Inventory_Core_Metrics_State.csv",
        "metro": link_prefix + "Core/RDC_Inventory_Core_Metrics_Metro.csv",
        "county": link_prefix + "Core/RDC_Inventory_Core_Metrics_County.csv",
        "zip": link_prefix + "Core/RDC_Inventory_Core_Metrics_Zip.csv",
    },
    "monthly_historical": {
        "national": link_prefix + "Core/RDC_Inventory_Core_Metrics_Country_History.csv",
        "state": link_prefix + "Core/RDC_Inventory_Core_Metrics_State_History.csv",
        "metro": link_prefix + "Core/RDC_Inventory_Core_Metrics_Metro_History.csv",
        "county": link_prefix + "Core/RDC_Inventory_Core_Metrics_County_History.csv",
        "zip": link_prefix + "Core/RDC_Inventory_Core_Metrics_Zip_History.csv",
    },
    "hotness": {
        "metro": link_prefix
        + "Hotness/RDC_Inventory_Hotness_Metrics_Metro_History.csv",
        "county": link_prefix
        + "Hotness/RDC_Inventory_Hotness_Metrics_County_History.csv",
        "zip": link_prefix + "Hotness/RDC_Inventory_Hotness_Metrics_Zip_History.csv",
    },
}


@st.cache
def get_inventory_data(url, index_col):
    df = pd.read_csv(url)
    if "County" in url:
        df[index_col] = df[index_col].map(str)
        df[index_col] = df[index_col].str.zfill(5)
    return df


def get_data_columns(df, category):
    if category == "county":
        del_cols = ["month_date_yyyymm", "county_fips", "county_name"]
        cols = df.columns.values.tolist()
        for col in cols:
            if col in del_cols:
                cols.remove(col)
        return cols[1:]


@st.cache
def get_geom_data(category):

    prefix = (
        "https://raw.githubusercontent.com/giswqs/streamlit-geospatial/master/data/"
    )
    links = {
        "national": prefix + "us_nation.geojson",
        "state": prefix + "us_states.geojson",
        "county": prefix + "us_counties.geojson",
        "metro": prefix + "us_metro_areas.geojson",
        "zip": prefix + "us_zip_codes.geojson",
    }

    gdf = gpd.read_file(links[category])
    return gdf


def join_attributes(gdf, df, category):

    new_gdf = None
    if category == "county":
        new_gdf = gdf.merge(df, left_on="GEOID",
                            right_on="county_fips", how="outer")

    return new_gdf


def select_non_null(gdf, col_name):
    new_gdf = gdf[~gdf[col_name].isna()]
    return new_gdf


def select_null(gdf, col_name):
    new_gdf = gdf[gdf[col_name].isna()]
    return new_gdf


def get_data_dict(name):
    in_csv = os.path.join(os.getcwd(), "data/realtor_data_dict.csv")
    df = pd.read_csv(in_csv)
    label = list(df[df["Name"] == name]["Label"])[0]
    desc = list(df[df["Name"] == name]["Description"])[0]
    return label, desc


def app():

    st.title("Real Estate Data and Market Trends")

    st.markdown(
        """
    Data source: <https://www.realtor.com/research/data>
    """
    )

    county_gdf = get_geom_data("county")
    inventory_df = get_inventory_data(
        data_links["monthly_current"]["county"], "county_fips"
    )

    data_cols = get_data_columns(inventory_df, "county")

    row1_col1, row1_col2, row1_col3, row1_col4, row1_col5 = st.columns([
                                                                       0.6, 0.8, 0.6, 1.4, 2])
    with row1_col1:
        frequency = st.selectbox("Monthly/weekly data", ["Monthly", "Weekly"])
    with row1_col2:
        st.selectbox("Current/historical data",
                     ["Current month data", "Historical data"])
    with row1_col3:
        st.selectbox("Scale", ["National", "State", "Metro",
                     "County", "Zip"], index=3)
    with row1_col4:
        selected_col = st.selectbox("Attribute", data_cols)
    with row1_col5:
        show_desc = st.checkbox("Show attribute description")
        if show_desc:
            label, desc = get_data_dict(selected_col.strip())
            markdown = f"""
            **{label}**: {desc}
            """
            st.markdown(markdown)

    row2_col1, row2_col2, row2_col3, row2_col4 = st.columns([1, 1, 2, 2])

    with row2_col1:
        palette = st.selectbox(
            "Color palette", cm.list_colormaps(), index=2)
    with row2_col2:
        n_colors = st.slider("Number of colors", min_value=2,
                             max_value=20, value=8)
    with row2_col3:
        show_colormaps = st.checkbox("Preview all color palettes")
        if show_colormaps:
            st.write(cm.plot_colormaps(return_fig=True))
    with row2_col4:
        show_nodata = st.checkbox("Show no data areas")

    county_gdf = join_attributes(county_gdf, inventory_df, "county")
    county_null_gdf = select_null(county_gdf, selected_col)
    county_gdf = select_non_null(county_gdf, selected_col)
    county_gdf = county_gdf.sort_values(by=selected_col, ascending=True)

    colors = cm.get_palette(palette, n_colors)
    colors = [hex_to_rgb(c) for c in colors]

    for i, ind in enumerate(county_gdf.index):
        index = int(i / (len(county_gdf)/len(colors)))
        if index >= len(colors):
            index = len(colors) - 1
        county_gdf.loc[ind, "R"] = colors[index][0]
        county_gdf.loc[ind, "G"] = colors[index][1]
        county_gdf.loc[ind, "B"] = colors[index][2]

    initial_view_state = pdk.ViewState(
        latitude=40, longitude=-100, zoom=3, max_zoom=16, pitch=0, bearing=0
    )

    min_value = county_gdf[selected_col].min()
    max_value = county_gdf[selected_col].max()
    color = "color"
    # color_exp = f"[({selected_col}-{min_value})/({max_value}-{min_value})*255, 0, 0]"
    color_exp = f"[R, G, B]"

    geojson = pdk.Layer(
        "GeoJsonLayer",
        county_gdf,
        pickable=True,
        opacity=0.5,
        stroked=True,
        filled=True,
        extruded=False,
        wireframe=True,
        # get_elevation="properties.ALAND/100000",
        # get_fill_color="color",
        get_fill_color=color_exp,
        get_line_color=[0, 0, 0],
        get_line_width=2,
        line_width_min_pixels=1,
    )

    geojson_null = pdk.Layer(
        "GeoJsonLayer",
        county_null_gdf,
        pickable=True,
        opacity=0.2,
        stroked=True,
        filled=True,
        extruded=False,
        wireframe=True,
        # get_elevation="properties.ALAND/100000",
        # get_fill_color="color",
        get_fill_color=[200, 200, 200],
        get_line_color=[0, 0, 0],
        get_line_width=2,
        line_width_min_pixels=1,
    )

    # tooltip = {"text": "Name: {NAME}"}

    # tooltip_value = f"<b>Value:</b> {median_listing_price}""
    tooltip = {
        "html": "<b>County:</b> {NAME}<br><b>Value:</b> {" + selected_col + "}",
        "style": {"backgroundColor": "steelblue", "color": "white"},
    }

    layers = [geojson]
    if show_nodata:
        layers.append(geojson_null)

    r = pdk.Deck(
        layers=layers,
        initial_view_state=initial_view_state,
        map_style="light",
        tooltip=tooltip,
    )

    row3_col1, row3_col2 = st.columns([6, 1])

    with row3_col1:
        st.pydeck_chart(r)
    with row3_col2:
        st.write(
            cm.create_colormap(
                palette,
                label=selected_col.replace("_", " ").title(),
                width=0.2,
                height=3.5,
                orientation="vertical",
                vmin=min_value,
                vmax=max_value,
                font_size=10
            )
        )
    row4_col1, row4_col2, _ = st.columns([1, 2, 3])
    with row4_col1:
        show_data = st.checkbox("Show raw data")
    with row4_col2:
        show_cols = st.multiselect("Select columns", data_cols)
    if show_data:
        st.dataframe(county_gdf[["STATEFP", "COUNTYFP", "NAME"] + show_cols])
