import streamlit as st


DEFAULT_PERSONA = {
    "Warm": 25.0,
    "Confident": 25.0,
    "Professional": 25.0,
    "Approachable": 25.0
}


def initialize_session_state():
    """
    앱에서 사용하는 session_state 값을 초기화합니다.
    """

    if "page" not in st.session_state:
        st.session_state["page"] = "landing"

    if "selected_mode" not in st.session_state:
        st.session_state["selected_mode"] = "First Date"

    if "target_persona" not in st.session_state:
        st.session_state[
            "target_persona"
        ] = DEFAULT_PERSONA.copy()

    if "target_slider_values" not in st.session_state:
        st.session_state["target_slider_values"] = {
            "Warm": 25,
            "Confident": 25,
            "Professional": 25,
            "Approachable": 25
        }

    # 업로드된 여러 사진
    if "uploaded_images" not in st.session_state:
        st.session_state["uploaded_images"] = []

    # 얼굴 Persona 종합 분석 결과
    if "analysis_result" not in st.session_state:
        st.session_state["analysis_result"] = None

    # 퍼스널컬러 종합 분석 결과
    if "color_analysis_result" not in st.session_state:
        st.session_state[
            "color_analysis_result"
        ] = None

    # file_uploader를 완전히 초기화하기 위한 버전값
    if "uploader_version" not in st.session_state:
        st.session_state["uploader_version"] = 0