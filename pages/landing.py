import streamlit as st

from utils.navigation import go_to_page


def show_landing_page():
    st.markdown(
        """
        <div class="landing-container">
            <div class="main-title">
                ✨ Welcome to<br>
                PersonaLab! 
            </div>

            <div class="main-subtitle">
                Discover the visual impression your photo communicates.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    left, center, right = st.columns(
        [1, 2, 1]
    )

    with center:
        if st.button(
            "Start ✨",
            type="primary",
            use_container_width=True
        ):
            go_to_page("mode")