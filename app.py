import streamlit as st

from utils.styles import load_styles
from utils.session import initialize_session_state

from pages.landing import show_landing_page
from pages.service_intro import show_service_intro_page
from pages.target import show_target_page
from pages.upload import show_upload_page
from pages.result import show_result_page
from pages.image_edit_result import show_image_edit_result_page
from pages.match_report import show_match_report_page
from pages.context import show_context_page
from pages.photo_editor import show_photo_editor_page

st.set_page_config(
    page_title="PersonaLab",
    page_icon="✨",
    layout="centered"
)


# 세션 상태 초기화
initialize_session_state()

# 현재 페이지 확인
current_page = st.session_state.get(
    "page",
    "landing"
)

# 공통 CSS + 현재 페이지 CSS 로드
load_styles(current_page)


# 페이지별 실행 함수
PAGE_ROUTES = {
    "landing": show_landing_page,
    "service_intro": show_service_intro_page,
    "target": show_target_page,
    "context": show_context_page,
    "upload": show_upload_page,
    "result": show_result_page,
    "image_edit_result": show_image_edit_result_page,
    "match_report": show_match_report_page,
    "photo_editor": show_photo_editor_page,
}


page_function = PAGE_ROUTES.get(current_page)

if page_function:
    page_function()

else:
    st.session_state["page"] = "landing"
    st.rerun()