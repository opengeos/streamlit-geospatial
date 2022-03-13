import ee
import streamlit as st
import geemap.foliumap as geemap

WIDTH = 1060
HEIGHT = 600


def function():
    st.write("Not implemented yet.")
    Map = geemap.Map()
    Map.to_streamlit(WIDTH, HEIGHT)


def lulc_mrb_floodplain():

    Map = geemap.Map()

    State_boundaries = ee.FeatureCollection('users/giswqs/MRB/State_Boundaries')
    State_style = State_boundaries.style(
        **{'color': '808080', 'width': 1, 'fillColor': '00000000'}
    )

    MRB_boundary = ee.FeatureCollection('users/giswqs/MRB/MRB_Boundary')
    MRB_style = MRB_boundary.style(
        **{'color': '000000', 'width': 2, 'fillColor': '00000000'}
    )

    floodplain = ee.Image('users/giswqs/MRB/USGS_Floodplain')

    class_values = [34, 38, 46, 50, 62]
    class_palette = ['c500ff', '00ffc5', '00a9e6', '73004d', '004d73']

    img_1950 = ee.Image('users/giswqs/MRB/Major_Transitions_1941_1950')
    img_1950 = img_1950.set('b1_class_values', class_values)
    img_1950 = img_1950.set('b1_class_palette', class_palette)

    img_1960 = ee.Image('users/giswqs/MRB/Major_Transitions_1941_1960')
    img_1960 = img_1960.set('b1_class_values', class_values)
    img_1960 = img_1960.set('b1_class_palette', class_palette)

    img_1970 = ee.Image('users/giswqs/MRB/Major_Transitions_1941_1970')
    img_1970 = img_1970.set('b1_class_values', class_values)
    img_1970 = img_1970.set('b1_class_palette', class_palette)

    img_1980 = ee.Image('users/giswqs/MRB/Major_Transitions_1941_1980')
    img_1980 = img_1980.set('b1_class_values', class_values)
    img_1980 = img_1980.set('b1_class_palette', class_palette)

    img_1990 = ee.Image('users/giswqs/MRB/Major_Transitions_1941_1990')
    img_1990 = img_1990.set('b1_class_values', class_values)
    img_1990 = img_1990.set('b1_class_palette', class_palette)

    img_2000 = ee.Image('users/giswqs/MRB/Major_Transitions_1941_2000')
    img_2000 = img_2000.set('b1_class_values', class_values)
    img_2000 = img_2000.set('b1_class_palette', class_palette)

    Map.addLayer(floodplain, {'palette': ['cccccc']}, 'Floodplain', True, 0.5)
    Map.addLayer(img_2000, {}, 'Major Transitions 1941-2000')
    Map.addLayer(img_1990, {}, 'Major Transitions 1941-1990')
    Map.addLayer(img_1980, {}, 'Major Transitions 1941-1980')
    Map.addLayer(img_1970, {}, 'Major Transitions 1941-1970')
    Map.addLayer(img_1960, {}, 'Major Transitions 1941-1960')
    Map.addLayer(img_1950, {}, 'Major Transitions 1941-1950')

    Map.addLayer(State_style, {}, 'State Boundaries')
    Map.addLayer(MRB_style, {}, 'MRB Boundary')

    Map.to_streamlit(WIDTH, HEIGHT)


def global_mangrove_watch():
    """https://samapriya.github.io/awesome-gee-community-datasets/projects/mangrove/"""
    Map = geemap.Map()
    gmw2007 = ee.FeatureCollection("projects/sat-io/open-datasets/GMW/GMW_2007_v2")
    gmw2008 = ee.FeatureCollection("projects/sat-io/open-datasets/GMW/GMW_2008_v2")
    gmw2009 = ee.FeatureCollection("projects/sat-io/open-datasets/GMW/GMW_2009_v2")
    gmw2010 = ee.FeatureCollection("projects/sat-io/open-datasets/GMW/GMW_2010_v2")
    gmw2015 = ee.FeatureCollection("projects/sat-io/open-datasets/GMW/GMW_2015_v2")
    gmw2016 = ee.FeatureCollection("projects/sat-io/open-datasets/GMW/GMW_2016_v2")
    gmw1996 = ee.FeatureCollection("projects/sat-io/open-datasets/GMW/GMW_1996_v2")

    Map.addLayer(
        ee.Image().paint(gmw1996, 0, 3),
        {"palette": ["228B22"]},
        'Global Mangrove Watch 1996',
    )
    Map.addLayer(
        ee.Image().paint(gmw2007, 0, 3),
        {"palette": ["228B22"]},
        'Global Mangrove Watch 2007',
    )
    Map.addLayer(
        ee.Image().paint(gmw2008, 0, 3),
        {"palette": ["228B22"]},
        'Global Mangrove Watch 2008',
    )
    Map.addLayer(
        ee.Image().paint(gmw2009, 0, 3),
        {"palette": ["228B22"]},
        'Global Mangrove Watch 2009',
    )
    Map.addLayer(
        ee.Image().paint(gmw2010, 0, 3),
        {"palette": ["228B22"]},
        'Global Mangrove Watch 2010',
    )
    Map.addLayer(
        ee.Image().paint(gmw2015, 0, 3),
        {"palette": ["228B22"]},
        'Global Mangrove Watch 2015',
    )
    Map.addLayer(
        ee.Image().paint(gmw2016, 0, 3),
        {"palette": ["228B22"]},
        'Global Mangrove Watch 2015',
    )

    Map.to_streamlit(WIDTH, HEIGHT)


def app():

    st.title("Awesome GEE Community Datasets")

    st.markdown(
        """
    
    This app is for exploring the [Awesome GEE Community Datasets](https://samapriya.github.io/awesome-gee-community-datasets). Work in progress.
    
    """
    )

    datasets = {
        "Population & Socioeconomic": {
            "High Resolution Settlement Layer": "function()",
            "World Settlement Footprint (2015)": "function()",
            "Gridded Population of the World": "function()",
            "geoBoundaries Global Database": "function()",
            "West Africa Coastal Vulnerability Mapping": "function()",
            "Relative Wealth Index (RWI)": "function()",
            "Social Connectedness Index (SCI)": "function()",
            "Native Land (Indigenous Land Maps)": "function()",
        },
        "Geophysical, Biological & Biogeochemical": {
            "Geomorpho90m Geomorphometric Layers": "function()",
        },
        "Land Use and Land Cover": {
            "Global Mangrove Watch": "global_mangrove_watch()",
            "Mississippi River Basin Floodplain Land Use Change (1941-2000)": "lulc_mrb_floodplain()",
        },
        "Hydrology": {
            "Global Shoreline Dataset": "function()",
        },
        "Agriculture, Vegetation and Forestry": {
            "Landfire Mosaics LF v2.0.0": "function()",
        },
        "Global Utilities, Assets and Amenities Layers": {
            "Global Power": "function()",
        },
        "EarthEnv Biodiversity ecosystems & climate Layers": {
            "Global Consensus Landcover": "function()",
        },
        "Weather and Climate Layers": {
            "Global Reference Evapotranspiration Layers": "function()",
        },
        "Global Events Layers": {
            "Global Fire Atlas (2003-2016)": "function()",
        },
    }

    row1_col1, row1_col2, _ = st.columns([1.2, 1.8, 1])

    with row1_col1:
        category = st.selectbox("Select a category", datasets.keys(), index=2)
    with row1_col2:
        dataset = st.selectbox("Select a dataset", datasets[category].keys())

    Map = geemap.Map()

    if dataset:
        eval(datasets[category][dataset])

    else:
        Map = geemap.Map()
        Map.to_streamlit(WIDTH, HEIGHT)
