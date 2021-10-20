import streamlit as st
import leafmap.foliumap as leafmap


def app():
    st.title("Home")

    st.header("Introduction")

    st.markdown(
        """
        This multi-page web app demonstrates various interative web apps created using [streamlit](https://streamlit.io) and open-source mapping libraries, 
        such as [leafmap](https://leafmap.org), [pydeck](https://deckgl.readthedocs.io), and [kepler.gl](https://docs.kepler.gl/docs/keplergl-jupyter).
        This is an open-source project and you are very welcome to contribute your comments, questions, resources, and apps as [issues](https://github.com/giswqs/streamlit-geospatial/issues) or 
        [pull requests](https://github.com/giswqs/streamlit-geospatial/pulls) to the [GitHub repository](https://github.com/giswqs/streamlit-geospatial).

        """
    )

    st.info("Click on the left sidebar menu to navigate to the different apps.")

    st.header("Demo")

    st.subheader("U.S. Real Estate Data and Market Trends")
    st.image("https://i.imgur.com/Z3dk6Tr.gif")
