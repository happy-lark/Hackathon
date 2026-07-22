#app에서 계속 유지해하는 값을 초기화함 
#target_slider_values를 따로 저장한 이유는, 정규화된 퍼센트와 실제 슬라이더 위치를 구분하기 위해서야.
import streamlit as st

DEFAULT_PERSONA = {
    "Warm": 25.0,
    "Confident": 25.0,
    "Professional": 25.0,
    "Approachable": 25.0
}


def initialize_session_state():
    ...

    if "target_slider_values" not in st.session_state:
        st.session_state["target_slider_values"] = {
            "Warm": 25,
            "Confident": 25,
            "Professional": 25,
            "Approachable": 25
        }

    if "uploaded_image" not in st.session_state:
        st.session_state["uploaded_image"] = None

    if "analysis_result" not in st.session_state:
        st.session_state["analysis_result"] = None

    if "analysis_type" not in st.session_state:
        st.session_state["analysis_type"] = None

    if "color_analysis_result" not in st.session_state:
        st.session_state["color_analysis_result"] = None