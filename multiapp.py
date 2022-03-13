"""Frameworks for running multiple Streamlit applications as a single app.
"""
import streamlit as st

# app_state = st.experimental_get_query_params()
# app_state = {k: v[0] if isinstance(v, list) else v for k, v in app_state.items()} # fetch the first item in each query string as we don't have multiple values for each query string key in this example


class MultiApp:
    """Framework for combining multiple streamlit applications.
    Usage:
        def foo():
            st.title("Hello Foo")
        def bar():
            st.title("Hello Bar")
        app = MultiApp()
        app.add_app("Foo", foo)
        app.add_app("Bar", bar)
        app.run()
    It is also possible keep each application in a separate file.
        import foo
        import bar
        app = MultiApp()
        app.add_app("Foo", foo.app)
        app.add_app("Bar", bar.app)
        app.run()
    """

    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        """Adds a new application.
        Parameters
        ----------
        func:
            the python function to render this app.
        title:
            title of the app. Appears in the dropdown in the sidebar.
        """
        self.apps.append({"title": title, "function": func})

    def run(self):
        app_state = st.experimental_get_query_params()
        app_state = {
            k: v[0] if isinstance(v, list) else v for k, v in app_state.items()
        }  # fetch the first item in each query string as we don't have multiple values for each query string key in this example

        # st.write('before', app_state)

        titles = [a["title"] for a in self.apps]
        functions = [a["function"] for a in self.apps]
        default_radio = titles.index(app_state["page"]) if "page" in app_state else 0

        st.sidebar.title("Navigation")

        title = st.sidebar.radio("Go To", titles, index=default_radio, key="radio")

        app_state["page"] = st.session_state.radio
        # st.write('after', app_state)

        st.experimental_set_query_params(**app_state)
        # st.experimental_set_query_params(**st.session_state.to_dict())
        functions[titles.index(title)]()

        st.sidebar.title("Contribute")
        st.sidebar.info(
            "This is an open source project and you are very welcome to contribute your "
            "comments, questions, resources and apps as "
            "[issues](https://github.com/giswqs/streamlit-geospatial/issues) or "
            "[pull requests](https://github.com/giswqs/streamlit-geospatial/pulls) "
            "to the [source code](https://github.com/giswqs/streamlit-geospatial). "
        )
        st.sidebar.title("About")
        st.sidebar.info(
            """
            This web [app](https://share.streamlit.io/giswqs/streamlit-geospatial/app.py) is maintained by [Qiusheng Wu](https://wetlands.io). You can follow me on social media:
             [GitHub](https://github.com/giswqs) | [Twitter](https://twitter.com/giswqs) | [YouTube](https://www.youtube.com/c/QiushengWu) | [LinkedIn](https://www.linkedin.com/in/qiushengwu).
            This web app URL: <https://streamlit.geemap.org>
        """
        )
