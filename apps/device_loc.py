import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
import leafmap.foliumap as leafmap


def app():

    loc_button = Button(label="Get Device Location", max_width=150)
    loc_button.js_on_event(
        "button_click",
        CustomJS(
            code="""
        navigator.geolocation.getCurrentPosition(
            (loc) => {
                document.dispatchEvent(new CustomEvent("GET_LOCATION", {detail: {lat: loc.coords.latitude, lon: loc.coords.longitude}}))
            }
        )
        """
        ),
    )
    result = streamlit_bokeh_events(
        loc_button,
        events="GET_LOCATION",
        key="get_location",
        refresh_on_update=False,
        override_height=75,
        debounce_time=0,
    )

    if result:
        if "GET_LOCATION" in result:
            loc = result.get("GET_LOCATION")
            lat = loc.get("lat")
            lon = loc.get("lon")
            st.write(f"Lat, Lon: {lat}, {lon}")

            m = leafmap.Map(center=(lat, lon), zoom=16)
            m.add_basemap("ROADMAP")
            popup = f"lat, lon: {lat}, {lon}"
            m.add_marker(location=(lat, lon), popup=popup)
            m.to_streamlit()
