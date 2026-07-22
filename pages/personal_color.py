import streamlit as st
from PIL import Image

from analysis.color_analyzer import analyze_personal_color
from utils.navigation import (
    go_to_page,
    reset_analysis
)


def show_personal_color_page():

    st.markdown(
        '<div class="step-text">PERSONAL COLOR ANALYSIS</div>',
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
            정면 얼굴 사진을 업로드하면
            피부색을 기반으로 퍼스널 컬러를 분석합니다.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="info-card">
            📸 권장 사진 조건<br>
            · 자연광에서 촬영한 사진<br>
            · 한 사람만 포함된 사진<br>
            · 이마와 양 볼이 잘 보이는 사진<br>
            · 필터가 적용되지 않은 사진
        </div>
        """,
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "Upload your photo",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
        key="personal_color_uploader"
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
                "이미지를 열 수 없습니다."
            )

    if "uploaded_image" in st.session_state:

        st.image(
            st.session_state[
                "uploaded_image"
            ],
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

            go_to_page(
                "analysis_type"
            )

    with analyze_column:

        analyze_clicked = st.button(
            "Analyze 🎨",
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
            "Analyzing personal color..."
        ):

            analysis_result = analyze_personal_color(
                image
            )

        if analysis_result["success"]:

            st.session_state[
                "color_analysis_result"
            ] = analysis_result

            go_to_page(
                "result"
            )

        else:

            st.session_state.pop(
                "color_analysis_result",
                None
            )

            st.error(
                analysis_result[
                    "message"
                ]
            )

    if st.button(
        "Clear uploaded photo",
        use_container_width=True
    ):

        reset_analysis()

        st.rerun()