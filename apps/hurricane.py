import streamlit as st
import tropycal.tracks as tracks


@st.cache_data
def read_data(basin='north_atlantic', source='hurdat', include_btk=False):
    return tracks.TrackDataset(basin=basin, source=source, include_btk=include_btk)


def app():

    st.title("Hurricane Mapping")

    row1_col1, row1_col2 = st.columns([3, 1])

    with row1_col1:
        empty = st.empty()
        empty.image("https://i.imgur.com/Ec7qsR0.png")

    with row1_col2:

        checkbox = st.checkbox("Select from a list of hurricanes", value=False)
        if checkbox:
            if st.session_state.get('hurricane') is None:
                st.session_state['hurricane'] = read_data()

            years = st.slider(
                'Select a year', min_value=1950, max_value=2022, value=(2000, 2010)
            )
            storms = st.session_state['hurricane'].filter_storms(year_range=years)
            selected = st.selectbox('Select a storm', storms)
            storm = st.session_state['hurricane'].get_storm(selected)
            ax = storm.plot()
            fig = ax.get_figure()
            empty.pyplot(fig)
        else:

            name = st.text_input("Or enter a storm Name", "michael")
            if name:
                if st.session_state.get('hurricane') is None:
                    st.session_state['hurricane'] = read_data()
                basin = st.session_state['hurricane']
                years = basin.search_name(name)
                if len(years) > 0:
                    year = st.selectbox("Select a year", years)
                    storm = basin.get_storm((name, year))
                    ax = storm.plot()
                    fig = ax.get_figure()
                    empty.pyplot(fig)
                else:
                    empty.text("No storms found")
                    st.write("No storms found")
