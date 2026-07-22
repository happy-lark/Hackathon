import streamlit as st

from analysis.color_analyzer import analyze_personal_color
from utils.navigation import go_to_page


PALETTE_IMAGES = {
    "Spring Warm": "assets/springwarm.png",
    "Summer Cool": "assets/summercool.png",
    "Autumn Warm": "assets/autumnwarm.png",
    "Winter Cool": "assets/wintercool.png"
}


def show_personal_color_page():
    st.markdown(
        """
        <div class="page-title">
            Personal Color Analysis
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="page-description">
            업로드한 얼굴 사진을 기반으로
            퍼스널 컬러를 분석합니다.
        </div>
        """,
        unsafe_allow_html=True
    )

    if "uploaded_image" not in st.session_state:
        st.warning("업로드된 사진이 없습니다.")

        if st.button(
            "← Upload Page",
            use_container_width=True,
            key="no_image_back"
        ):
            go_to_page("upload")

        return

    image = st.session_state["uploaded_image"]

    st.image(
        image,
        caption="Uploaded Photo",
        use_container_width=True
    )

    st.info(
        "자연광에서 촬영한 무필터 사진을 사용하면 "
        "더 안정적인 결과를 얻을 수 있습니다."
    )

    back_column, analyze_column = st.columns(2)

    with back_column:
        if st.button(
            "← Back",
            use_container_width=True,
            key="color_back"
        ):
            go_to_page("upload")

    with analyze_column:
        color_analyze_clicked = st.button(
            "Analyze Personal Color 🎨",
            type="primary",
            use_container_width=True,
            key="color_analyze"
        )

    if color_analyze_clicked:
        with st.spinner(
            "Analyzing skin tone and color..."
        ):
            result = analyze_personal_color(image)

        if result["success"]:
            st.session_state[
                "color_analysis_result"
            ] = result

        else:
            st.session_state.pop(
                "color_analysis_result",
                None
            )

            st.error(result["message"])

    result = st.session_state.get(
        "color_analysis_result"
    )

    if result is not None:
        st.divider()

        st.subheader(
            f'🎨 {result["season"]}'
        )

        palette_path = PALETTE_IMAGES.get(
            result["season"]
        )

        if palette_path is not None:
            try:
                st.image(
                    palette_path,
                    caption=(
                        f'{result["season"]} '
                        "Color Palette"
                    ),
                    use_container_width=True
                )

            except Exception as error:
                st.error(
                    "팔레트 이미지를 불러오지 못했습니다."
                )
                st.code(str(error))

        else:
            st.warning(
                "분석 결과와 일치하는 팔레트가 없습니다."
            )

        metric_column1, metric_column2 = st.columns(2)

        with metric_column1:
            st.metric(
                "Undertone",
                result["undertone"]
            )

        with metric_column2:
            st.metric(
                "Estimated Confidence",
                f'{result["confidence"]}%'
            )

        st.write(result["description"])

        st.markdown(
            "#### Recommended Colors"
        )

        st.write(
            " · ".join(
                result["recommended_colors"]
            )
        )

        with st.expander(
            "View analysis details"
        ):
            st.json(
                result["color_features"]
            )

        st.caption(
            "이 결과는 사진 속 색상값을 기반으로 한 "
            "간단한 추정 결과입니다. 조명, 카메라 보정, "
            "필터와 배경색에 따라 달라질 수 있습니다."
        )