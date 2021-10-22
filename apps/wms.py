import streamlit as st
import leafmap.foliumap as leafmap


def app():
    st.title("Add Web Map Service (WMS)")
    st.markdown(
        """
    This app is a demonstration of loading Web Map Service (WMS) layers. Simply enter the URL of the WMS service 
    in the text box below and press Enter to retrieve the layers. Go to https://apps.nationalmap.gov/services to find 
    some WMS URLs if needed.
    """
    )

    row1_col1, row1_col2, _ = st.columns([2, 1, 0.5])
    width = 800
    height = 600
    layers = None

    with row1_col2:

        esa_landcover = "https://services.terrascope.be/wms/v2"
        url = st.text_input(
            "Enter a WMS URL:", value="https://services.terrascope.be/wms/v2"
        )
        empty = st.empty()

        if url:
            options = leafmap.get_wms_layers(url)

            default = None
            if url == esa_landcover:
                default = "WORLDCOVER_2020_MAP"
            layers = empty.multiselect(
                "Select WMS layers to add to the map:", options, default=default
            )

        with row1_col1:
            m = leafmap.Map(center=(36.3, 0), zoom=2)

            if layers is not None:
                for layer in layers:
                    m.add_wms_layer(
                        url, layers=layer, name=layer, attribution=" ", transparent=True
                    )

            if "WORLDCOVER_2020_MAP" in layers:
                m.add_legend(title="Land Cover", builtin_legend="ESA_WorldCover")
            m.to_streamlit(width, height)
