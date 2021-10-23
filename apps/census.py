import streamlit as st
import leafmap.foliumap as leafmap


def app():
    st.title("Using U.S. Census Data")
    st.markdown(
        """
    This app is a demonstration of using the [U.S. Census Bureau](https://www.census.gov/) TIGERweb Web Map Service (WMS). A complete list of WMS layers can be found [here](https://tigerweb.geo.census.gov/tigerwebmain/TIGERweb_wms.html). 
    """
    )

    if "first_index" not in st.session_state:
        st.session_state["first_index"] = 60
    else:
        st.session_state["first_index"] = 0

    row1_col1, row1_col2 = st.columns([3, 1])
    width = 800
    height = 600

    census_dict = leafmap.get_census_dict()
    with row1_col2:

        wms = st.selectbox("Select a WMS", list(census_dict.keys()), index=11)
        layer = st.selectbox(
            "Select a layer",
            census_dict[wms]["layers"],
            index=st.session_state["first_index"],
        )

        with row1_col1:
            m = leafmap.Map()
            m.add_census_data(wms, layer)
            m.to_streamlit(width, height)
