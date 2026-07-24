import streamlit as st

from pages.landing import show_landing_page
from pages.mode import show_mode_page
from pages.target import show_target_page
from pages.upload import show_upload_page
from pages.result import show_result_page
from pages.image_edit_result import show_image_edit_result_page
#퍼컬용
from pages.personal_color import show_personal_color_page
from utils.session import initialize_session_state


st.set_page_config(
    page_title="PersonaLab",
    page_icon="✨",
    layout="centered"
)


def load_css():
    """
    외부 CSS 파일을 읽어 Streamlit에 적용합니다.
    """
    try:
        with open(
            "styles/style.css",
            "r",
            encoding="utf-8"
        ) as css_file:
            css = css_file.read()

        st.markdown(
            f"<style>{css}</style>",
            unsafe_allow_html=True
        )

    except FileNotFoundError:
        st.warning("CSS 파일을 찾지 못했습니다.")


load_css()
initialize_session_state()

current_page = st.session_state["page"]


if current_page == "landing":
    show_landing_page()

elif current_page == "mode":
    show_mode_page()

elif current_page == "target":
    show_target_page()

elif current_page == "upload":
    show_upload_page()

elif current_page == "result":
    show_result_page()

elif current_page == "personal_color":
    show_personal_color_page()

elif current_page == "image_edit_result":
    show_image_edit_result_page()

else:
    st.session_state["page"] = "landing"
    st.rerun()