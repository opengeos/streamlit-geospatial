import datetime
import os
import pathlib
import requests
import zipfile
import pandas as pd
import pydeck as pdk
import geopandas as gpd
import streamlit as st
import leafmap.colormaps as cm
from leafmap.common import hex_to_rgb


STREAMLIT_STATIC_PATH = pathlib.Path(st.__path__[0]) / "static"
# We create a downloads directory within the streamlit static asset directory
# and we write output files to it
DOWNLOADS_PATH = STREAMLIT_STATIC_PATH / "downloads"
if not DOWNLOADS_PATH.is_dir():
    DOWNLOADS_PATH.mkdir()

# Data source: https://www.realtor.com/research/data/
# link_prefix = "https://econdata.s3-us-west-2.amazonaws.com/Reports/"
link_prefix = "https://raw.githubusercontent.com/giswqs/data/main/housing/"

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


def get_data_columns(df, category, frequency="monthly"):
    if frequency == "monthly":
        if category.lower() == "county":
            del_cols = ["month_date_yyyymm", "county_fips", "county_name"]
        elif category.lower() == "state":
            del_cols = ["month_date_yyyymm", "state", "state_id"]
        elif category.lower() == "national":
            del_cols = ["month_date_yyyymm", "country"]
        elif category.lower() == "metro":
            del_cols = ["month_date_yyyymm", "cbsa_code", "cbsa_title", "HouseholdRank"]
        elif category.lower() == "zip":
            del_cols = ["month_date_yyyymm", "postal_code", "zip_name", "flag"]
    elif frequency == "weekly":
        if category.lower() == "national":
            del_cols = ["week_end_date", "geo_country"]
        elif category.lower() == "metro":
            del_cols = ["week_end_date", "cbsa_code", "cbsa_title", "hh_rank"]

    cols = df.columns.values.tolist()

    for col in cols:
        if col.strip() in del_cols:
            cols.remove(col)
    if category.lower() == "metro":
        return cols[2:]
    else:
        return cols[1:]


@st.cache
def get_inventory_data(url):
    df = pd.read_csv(url)
    url = url.lower()
    if "county" in url:
        df["county_fips"] = df["county_fips"].map(str)
        df["county_fips"] = df["county_fips"].str.zfill(5)
    elif "state" in url:
        df["STUSPS"] = df["state_id"].str.upper()
    elif "metro" in url:
        df["cbsa_code"] = df["cbsa_code"].map(str)
    elif "zip" in url:
        df["postal_code"] = df["postal_code"].map(str)
        df["postal_code"] = df["postal_code"].str.zfill(5)

    if "listing_weekly_core_aggregate_by_country" in url:
        columns = get_data_columns(df, "national", "weekly")
        for column in columns:
            if column != "median_days_on_market_by_day_yy":
                df[column] = df[column].str.rstrip("%").astype(float) / 100
    if "listing_weekly_core_aggregate_by_metro" in url:
        columns = get_data_columns(df, "metro", "weekly")
        for column in columns:
            if column != "median_days_on_market_by_day_yy":
                df[column] = df[column].str.rstrip("%").astype(float) / 100
        df["cbsa_code"] = df["cbsa_code"].str[:5]
    return df


def filter_weekly_inventory(df, week):
    df = df[df["week_end_date"] == week]
    return df


def get_start_end_year(df):
    start_year = int(str(df["month_date_yyyymm"].min())[:4])
    end_year = int(str(df["month_date_yyyymm"].max())[:4])
    return start_year, end_year


def get_periods(df):
    return [str(d) for d in list(set(df["month_date_yyyymm"].tolist()))]


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
        "zip": "https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_zcta510_500k.zip",
    }

    if category.lower() == "zip":
        r = requests.get(links[category])
        out_zip = os.path.join(DOWNLOADS_PATH, "cb_2018_us_zcta510_500k.zip")
        with open(out_zip, "wb") as code:
            code.write(r.content)
        zip_ref = zipfile.ZipFile(out_zip, "r")
        zip_ref.extractall(DOWNLOADS_PATH)
        gdf = gpd.read_file(out_zip.replace("zip", "shp"))
    else:
        gdf = gpd.read_file(links[category])
    return gdf


def join_attributes(gdf, df, category):

    new_gdf = None
    if category == "county":
        new_gdf = gdf.merge(df, left_on="GEOID", right_on="county_fips", how="outer")
    elif category == "state":
        new_gdf = gdf.merge(df, left_on="STUSPS", right_on="STUSPS", how="outer")
    elif category == "national":
        if "geo_country" in df.columns.values.tolist():
            df["country"] = None
            df.loc[0, "country"] = "United States"
        new_gdf = gdf.merge(df, left_on="NAME", right_on="country", how="outer")
    elif category == "metro":
        new_gdf = gdf.merge(df, left_on="CBSAFP", right_on="cbsa_code", how="outer")
    elif category == "zip":
        new_gdf = gdf.merge(df, left_on="GEOID10", right_on="postal_code", how="outer")
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


def get_weeks(df):
    seq = list(set(df[~df["week_end_date"].isnull()]["week_end_date"].tolist()))
    weeks = [
        datetime.date(int(d.split("/")[2]), int(d.split("/")[0]), int(d.split("/")[1]))
        for d in seq
    ]
    weeks.sort()
    return weeks


def get_saturday(in_date):
    idx = (in_date.weekday() + 1) % 7
    sat = in_date + datetime.timedelta(6 - idx)
    return sat


def app():

    st.title("U.S. Real Estate Data and Market Trends")
    st.markdown(
        """**Introduction:** This interactive dashboard is designed for visualizing U.S. real estate data and market trends at multiple levels (i.e., national,
         state, county, and metro). The data sources include [Real Estate Data](https://www.realtor.com/research/data) from realtor.com and 
         [Cartographic Boundary Files](https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html) from U.S. Census Bureau.
         Several open-source packages are used to process the data and generate the visualizations, e.g., [streamlit](https://streamlit.io),
          [geopandas](https://geopandas.org), [leafmap](https://leafmap.org), and [pydeck](https://deckgl.readthedocs.io).
    """
    )

    with st.expander("See a demo"):
        st.image("https://i.imgur.com/Z3dk6Tr.gif")

    row1_col1, row1_col2, row1_col3, row1_col4, row1_col5 = st.columns(
        [0.6, 0.8, 0.6, 1.4, 2]
    )
    with row1_col1:
        frequency = st.selectbox("Monthly/weekly data", ["Monthly", "Weekly"])
    with row1_col2:
        types = ["Current month data", "Historical data"]
        if frequency == "Weekly":
            types.remove("Current month data")
        cur_hist = st.selectbox(
            "Current/historical data",
            types,
        )
    with row1_col3:
        if frequency == "Monthly":
            scale = st.selectbox(
                "Scale", ["National", "State", "Metro", "County"], index=3
            )
        else:
            scale = st.selectbox("Scale", ["National", "Metro"], index=1)

    gdf = get_geom_data(scale.lower())

    if frequency == "Weekly":
        inventory_df = get_inventory_data(data_links["weekly"][scale.lower()])
        weeks = get_weeks(inventory_df)
        with row1_col1:
            selected_date = st.date_input("Select a date", value=weeks[-1])
            saturday = get_saturday(selected_date)
            selected_period = saturday.strftime("%-m/%-d/%Y")
            if saturday not in weeks:
                st.error(
                    "The selected date is not available in the data. Please select a date between {} and {}".format(
                        weeks[0], weeks[-1]
                    )
                )
                selected_period = weeks[-1].strftime("%-m/%-d/%Y")
        inventory_df = get_inventory_data(data_links["weekly"][scale.lower()])
        inventory_df = filter_weekly_inventory(inventory_df, selected_period)

    if frequency == "Monthly":
        if cur_hist == "Current month data":
            inventory_df = get_inventory_data(
                data_links["monthly_current"][scale.lower()]
            )
            selected_period = get_periods(inventory_df)[0]
        else:
            with row1_col2:
                inventory_df = get_inventory_data(
                    data_links["monthly_historical"][scale.lower()]
                )
                start_year, end_year = get_start_end_year(inventory_df)
                periods = get_periods(inventory_df)
                with st.expander("Select year and month", True):
                    selected_year = st.slider(
                        "Year",
                        start_year,
                        end_year,
                        value=start_year,
                        step=1,
                    )
                    selected_month = st.slider(
                        "Month",
                        min_value=1,
                        max_value=12,
                        value=int(periods[0][-2:]),
                        step=1,
                    )
                selected_period = str(selected_year) + str(selected_month).zfill(2)
                if selected_period not in periods:
                    st.error("Data not available for selected year and month")
                    selected_period = periods[0]
                inventory_df = inventory_df[
                    inventory_df["month_date_yyyymm"] == int(selected_period)
                ]

    data_cols = get_data_columns(inventory_df, scale.lower(), frequency.lower())

    with row1_col4:
        selected_col = st.selectbox("Attribute", data_cols)
    with row1_col5:
        show_desc = st.checkbox("Show attribute description")
        if show_desc:
            try:
                label, desc = get_data_dict(selected_col.strip())
                markdown = f"""
                **{label}**: {desc}
                """
                st.markdown(markdown)
            except:
                st.warning("No description available for selected attribute")

    row2_col1, row2_col2, row2_col3, row2_col4, row2_col5, row2_col6 = st.columns(
        [0.6, 0.68, 0.7, 0.7, 1.5, 0.8]
    )

    palettes = cm.list_colormaps()
    with row2_col1:
        palette = st.selectbox("Color palette", palettes, index=palettes.index("Blues"))
    with row2_col2:
        n_colors = st.slider("Number of colors", min_value=2, max_value=20, value=8)
    with row2_col3:
        show_nodata = st.checkbox("Show nodata areas", value=True)
    with row2_col4:
        show_3d = st.checkbox("Show 3D view", value=False)
    with row2_col5:
        if show_3d:
            elev_scale = st.slider(
                "Elevation scale", min_value=1, max_value=1000000, value=1, step=10
            )
            with row2_col6:
                st.info("Press Ctrl and move the left mouse button.")
        else:
            elev_scale = 1

    gdf = join_attributes(gdf, inventory_df, scale.lower())
    gdf_null = select_null(gdf, selected_col)
    gdf = select_non_null(gdf, selected_col)
    gdf = gdf.sort_values(by=selected_col, ascending=True)

    colors = cm.get_palette(palette, n_colors)
    colors = [hex_to_rgb(c) for c in colors]

    for i, ind in enumerate(gdf.index):
        index = int(i / (len(gdf) / len(colors)))
        if index >= len(colors):
            index = len(colors) - 1
        gdf.loc[ind, "R"] = colors[index][0]
        gdf.loc[ind, "G"] = colors[index][1]
        gdf.loc[ind, "B"] = colors[index][2]

    initial_view_state = pdk.ViewState(
        latitude=40, longitude=-100, zoom=3, max_zoom=16, pitch=0, bearing=0
    )

    min_value = gdf[selected_col].min()
    max_value = gdf[selected_col].max()
    color = "color"
    # color_exp = f"[({selected_col}-{min_value})/({max_value}-{min_value})*255, 0, 0]"
    color_exp = f"[R, G, B]"

    geojson = pdk.Layer(
        "GeoJsonLayer",
        gdf,
        pickable=True,
        opacity=0.5,
        stroked=True,
        filled=True,
        extruded=show_3d,
        wireframe=True,
        get_elevation=f"{selected_col}",
        elevation_scale=elev_scale,
        # get_fill_color="color",
        get_fill_color=color_exp,
        get_line_color=[0, 0, 0],
        get_line_width=2,
        line_width_min_pixels=1,
    )

    geojson_null = pdk.Layer(
        "GeoJsonLayer",
        gdf_null,
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
        "html": "<b>Name:</b> {NAME}<br><b>Value:</b> {"
        + selected_col
        + "}<br><b>Date:</b> "
        + selected_period
        + "",
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
                height=3,
                orientation="vertical",
                vmin=min_value,
                vmax=max_value,
                font_size=10,
            )
        )
    row4_col1, row4_col2, row4_col3 = st.columns([1, 2, 3])
    with row4_col1:
        show_data = st.checkbox("Show raw data")
    with row4_col2:
        show_cols = st.multiselect("Select columns", data_cols)
    with row4_col3:
        show_colormaps = st.checkbox("Preview all color palettes")
        if show_colormaps:
            st.write(cm.plot_colormaps(return_fig=True))
    if show_data:
        if scale == "National":
            st.dataframe(gdf[["NAME", "GEOID"] + show_cols])
        elif scale == "State":
            st.dataframe(gdf[["NAME", "STUSPS"] + show_cols])
        elif scale == "County":
            st.dataframe(gdf[["NAME", "STATEFP", "COUNTYFP"] + show_cols])
        elif scale == "Metro":
            st.dataframe(gdf[["NAME", "CBSAFP"] + show_cols])
        elif scale == "Zip":
            st.dataframe(gdf[["GEOID10"] + show_cols])
