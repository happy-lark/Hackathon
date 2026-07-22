import streamlit as st


def go_to_page(page_name):
    """
    지정된 페이지로 이동합니다.
    """
    st.session_state["page"] = page_name
    st.rerun()


def reset_analysis():
    """
    사진과 분석 결과만 초기화합니다.
    """
    st.session_state.pop("uploaded_image", None)
    st.session_state.pop("analysis_result", None)


def reset_all():
    """
    앱을 처음 상태로 초기화합니다.
    """
    keys_to_remove = [
        "uploaded_image",
        "analysis_result",
        "selected_mode",
        "target_persona",
        "target_slider_values"
    ]

    for key in keys_to_remove:
        st.session_state.pop(key, None)

    st.session_state["page"] = "landing"
    st.rerun()