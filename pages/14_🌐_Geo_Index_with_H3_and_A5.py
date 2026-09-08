import streamlit_hexviz as shv
import pandas as pd
import streamlit as st

st.write("## Earthquakes")
st.subheader("Example for geo index and heatmaps with H3 and A5")


@st.cache_data
def load_data():
    return pd.read_csv("data/earthquakes.csv")


data = load_data()


geospatial_grid = st.selectbox(
    "Select geo spatial grid",
    ["H3 resolution 4", "H3 flexible", "A5 resolution 4", "A5 flexible"],
)
if geospatial_grid == "H3 resolution 4":
    shv.h3_map(
        df=data,
        lat="latitude",
        lon="longitude",
        use_sidebar_controls=False,
        key="h3",
        transform="log",
        colour_scale="reds",
        resolution=4,
    )
elif geospatial_grid == "H3 flexible":
    shv.h3_map(
        df=data,
        lat="latitude",
        lon="longitude",
        use_sidebar_controls=True,
        key="h3_flex",
    )
    st.info("use left side navigation for changing settings")
elif geospatial_grid == "A5 resolution 4":
    shv.a5_map(
        df=data,
        lat="latitude",
        lon="longitude",
        use_sidebar_controls=False,
        key="A5",
        transform="log",
        colour_scale="reds",
        resolution=4,
    )

elif geospatial_grid == "A5 flexible":
    shv.a5_map(
        df=data,
        lat="latitude",
        lon="longitude",
        use_sidebar_controls=True,
        key="a5_flex",
    )
    st.info("use left side navigation for changing settings")

st.write("Data sample")
st.dataframe(data.head(20))

with st.expander("See code"):
    st.code(
        """ pip install streamlit-hexviz[a5]
            """,
        language="bash",
    )

    st.code(
        """
    import streamlit_hexviz as shv
    import pandas as pd
    import streamlit as st

    @st.cache_data
    def load_data():
        return pd.read_csv("data/earthquakes.csv")


    data = load_data()


    geospatial_grid = st.selectbox(
        "Select geo spatial grid",
        ["H3 resolution 4", "H3 flexible", "A5 resolution 4", "A5 flexible"],
    )

    if geospatial_grid == "H3 resolution 4":
        shv.h3_map(
            df=data,
            lat="latitude",
            lon="longitude",
            use_sidebar_controls=False,
            key="h3",
            transform="log",
            colour_scale="reds",
            resolution=4,
        )
    elif geospatial_grid == "H3 flexible":
        shv.h3_map(
            df=data,
            lat="latitude",
            lon="longitude",
            use_sidebar_controls=True,
            key="h3_flex",
        )
        st.info("use left side navigation for changing settings")
    elif geospatial_grid == "A5 resolution 4":
        shv.a5_map(
            df=data,
            lat="latitude",
            lon="longitude",
            use_sidebar_controls=False,
            key="A5",
            transform="log",
            colour_scale="reds",
            resolution=4,
        )

    elif geospatial_grid == "A5 flexible":
        shv.a5_map(
            df=data,
            lat="latitude",
            lon="longitude",
            use_sidebar_controls=True,
            key="a5_flex",
        )
    st.info("use left side navigation for changing settings")


    st.dataframe(data.head(20))

    """,
        language="python",
    )


st.write("""
    ### H3

    H3 is a hierarchical geospatial indexing system developed by Uber that divides the Earth into hexagonal cells across 16 resolution levels. It is particularly useful for spatial aggregation, joins, neighborhood operations, and multi-resolution analysis.

    [H3 Core Documentation](https://h3geo.org/docs/) · [H3 GitHub](https://github.com/uber/h3)

    ### A5

    A5 is a global geospatial indexing system that uses pentagonal cells and is designed for low-distortion, equal-area spatial indexing. It provides a hierarchical grid suitable for spatial indexing, aggregation, joins, and multi-resolution analysis.

    [A5 Core Documentation](https://a5geo.org/docs/) · [A5 GitHub](https://github.com/felixpalmer/a5)

    **In short:** H3 uses hexagons and is widely adopted; A5 uses pentagonal cells with a focus on equal-area, low-distortion indexing.
         """)


st.markdown(
    "**streamlit-hexviz** · "
    "[GitHub](https://github.com/Robert-Ziegltrum/streamlit-hexviz) · "
    "[Streamlit Components Gallery](https://streamlit.io/components)"
)
