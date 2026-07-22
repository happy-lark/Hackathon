import streamlit as st
from PIL import Image

from analysis.analyzer import analyze_face_persona
from utils.navigation import (
    go_to_page,
    reset_analysis
)


def show_upload_page():
    st.markdown(
        '<div class="step-text">STEP 3 OF 3</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="page-title">
            Upload Your Photo
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="page-description">
            한 사람의 얼굴이 선명하게 보이는 사진을 업로드해주세요.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="info-card">
            📸 권장 사진 조건<br>
            · 얼굴이 정면에 가까운 사진<br>
            · 한 사람만 포함된 사진<br>
            · 눈, 코, 입이 가려지지 않은 사진<br>
            · 얼굴이 너무 작지 않은 사진
        </div>
        """,
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "Upload your photo",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
        key="photo_uploader"
    )

    if uploaded_file is not None:
        try:
            image = Image.open(
                uploaded_file
            ).convert("RGB")

            st.session_state[
                "uploaded_image"
            ] = image

        except Exception:
            st.session_state.pop(
                "uploaded_image",
                None
            )

            st.error(
                "이미지 파일을 열 수 없습니다. "
                "JPG, JPEG 또는 PNG 형식의 "
                "정상적인 파일을 업로드해주세요."
            )

    if "uploaded_image" in st.session_state:
        st.image(
            st.session_state["uploaded_image"],
            caption="Uploaded Photo",
            use_container_width=True
        )

    st.write("")

    back_column, space, analyze_column = st.columns(
        [1, 2, 1]
    )

    with back_column:
        if st.button(
            "← Back",
            use_container_width=True
        ):
            go_to_page("target")

    with analyze_column:
        analyze_clicked = st.button(
            "Analyze ✨",
            type="primary",
            use_container_width=True,
            disabled=(
                "uploaded_image"
                not in st.session_state
            )
        )

    if analyze_clicked:
        image = st.session_state[
            "uploaded_image"
        ]

        with st.spinner(
            "Analyzing facial expression "
            "and visual impression..."
        ):
            analysis_result = analyze_face_persona(
                image
            )

        if analysis_result["success"]:
            st.session_state[
                "analysis_result"
            ] = analysis_result

            go_to_page("result")

        else:
            st.session_state.pop(
                "analysis_result",
                None
            )

            st.error(
                analysis_result["message"]
            )

    if st.button(
        "Clear uploaded photo",
        use_container_width=True
    ):
        reset_analysis()
        st.rerun()