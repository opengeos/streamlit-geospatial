import leafmap.foliumap as leafmap
import streamlit as st
import os


def save_uploaded_file(file_content, file_name):
    """
    Save the uploaded file to a temporary directory
    """
    import tempfile
    import os
    import uuid

    _, file_extension = os.path.splitext(file_name)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(tempfile.gettempdir(), f"{file_id}{file_extension}")

    with open(file_path, "wb") as file:
        file.write(file_content.getbuffer())

    return file_path


def app():

    st.title("Upload Vector Data")

    row1_col1, row1_col2 = st.columns([2, 1])
    width = 950
    height = 600

    with row1_col2:

        backend = st.selectbox("Select a plotting backend", ["folium", "kepler.gl"])

        if backend == "folium":
            import leafmap.foliumap as leafmap
        elif backend == "kepler.gl":
            import leafmap.kepler as leafmap

        data = st.file_uploader(
            "Upload a vector dataset", type=["geojson", "kml", "zip"]
        )

        if data:
            # st.write(data.name)
            file_path = save_uploaded_file(data, data.name)
            # st.write(f"Saved to {file_path}")

            with row1_col1:
                m = leafmap.Map(draw_export=True)
                m.add_vector(file_path, layer_name=os.path.splitext(data.name)[0])
                m.to_streamlit(width=width, height=height)

        else:
            with row1_col1:
                m = leafmap.Map(draw_export=width)
                m.to_streamlit(width=width, height=height)
