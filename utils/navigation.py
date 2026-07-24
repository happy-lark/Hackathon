import streamlit as st


def go_to_page(page_name):
    """
    지정된 페이지로 이동합니다.
    """
    st.session_state["page"] = page_name
    st.rerun()


def reset_analysis():
    """
    업로드한 사진과 분석 결과만 초기화합니다.

    선택한 Mode와 Target Persona는 유지합니다.
    """

    st.session_state.pop(
        "uploaded_images",
        None
    )

    st.session_state.pop(
        "uploaded_image",
        None
    )

    st.session_state.pop(
        "analysis_result",
        None
    )

    st.session_state.pop(
        "color_analysis_result",
        None
    )

    # Streamlit file_uploader 위젯 자체를 초기화하기 위해
    # key에 사용되는 버전값을 증가시킵니다.
    st.session_state["uploader_version"] = (
        st.session_state.get(
            "uploader_version",
            0
        ) + 1
    )


def reset_all():
    """
    앱을 처음 상태로 초기화합니다.
    """

    next_uploader_version = (
        st.session_state.get(
            "uploader_version",
            0
        ) + 1
    )

    keys_to_remove = [
        "uploaded_image",
        "uploaded_images",
        "analysis_result",
        "color_analysis_result",
        "selected_mode",
        "target_persona",
        "target_slider_values"
    ]

    for key in keys_to_remove:
        st.session_state.pop(
            key,
            None
        )

    st.session_state[
        "uploader_version"
    ] = next_uploader_version

    st.session_state["page"] = "landing"

    st.rerun()