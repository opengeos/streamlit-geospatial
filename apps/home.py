import streamlit as st
import leafmap.foliumap as leafmap


def app():
    st.title("Streamlit for Geospatial Applications")

    st.markdown(
        """
        This multi-page web app demonstrates various interactive web apps created using [streamlit](https://streamlit.io) and open-source mapping libraries, 
        such as [leafmap](https://leafmap.org), [geemap](https://geemap.org), [pydeck](https://deckgl.readthedocs.io), and [kepler.gl](https://docs.kepler.gl/docs/keplergl-jupyter).
        This is an open-source project and you are very welcome to contribute your comments, questions, resources, and apps as [issues](https://github.com/giswqs/streamlit-geospatial/issues) or 
        [pull requests](https://github.com/giswqs/streamlit-geospatial/pulls) to the [GitHub repository](https://github.com/giswqs/streamlit-geospatial).

        """
    )

    st.info("Click on the left sidebar menu to navigate to the different apps.")

    st.subheader("Timelapse of Satellite Imagery")
    st.markdown(
        """
        The following timelapse animations were created using the Timelapse web app. Click `Create Timelapse` on the left sidebar menu to create your own timelapse for any location around the globe.
    """
    )

    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.image("https://github.com/giswqs/data/raw/main/timelapse/spain.gif")
        st.image("https://github.com/giswqs/data/raw/main/timelapse/las_vegas.gif")

    with row1_col2:
        st.image("https://github.com/giswqs/data/raw/main/timelapse/goes.gif")
        st.image("https://github.com/giswqs/data/raw/main/timelapse/fire.gif")
