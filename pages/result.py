import streamlit as st

from pages.persona_result import (
    show_persona_result_page
)

from pages.color_result import (
    show_color_result_page
)


def show_result_page():

    analysis_type = st.session_state.get(
        "analysis_type",
        "persona"
    )

    if analysis_type == "personal_color":

        show_color_result_page()

    else:

        show_persona_result_page()