import streamlit as st

from analysis.color_analyzer import (
    analyze_multiple_personal_colors
)
from utils.navigation import go_to_page


PALETTE_IMAGES = {
    "Spring Warm": "assets/springwarm.png",
    "Summer Cool": "assets/summercool.png",
    "Autumn Warm": "assets/autumnwarm.png",
    "Winter Cool": "assets/wintercool.png"
}


def show_image_previews(images):
    """
    분석 대상 사진을 표시합니다.
    """
    columns = st.columns(3)

    for index, image in enumerate(images):
        with columns[index % 3]:
            st.image(
                image,
                caption=f"Photo {index + 1}",
                use_container_width=True
            )


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
            업로드한 여러 얼굴 사진의 색상값을 종합해
            퍼스널 컬러를 분석합니다.
        </div>
        """,
        unsafe_allow_html=True
    )

    images = st.session_state.get(
        "uploaded_images",
        []
    )

    if not images:
        st.warning(
            "업로드된 사진이 없습니다."
        )

        if st.button(
            "← Upload Page",
            use_container_width=True,
            key="no_image_back"
        ):
            go_to_page("upload")

        return

    show_image_previews(
        images
    )

    st.info(
        "자연광에서 촬영한 무필터 사진을 여러 장 사용하면 "
        "조명에 따른 오차를 줄이는 데 도움이 됩니다."
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
            "Analyzing skin tones from all photos..."
        ):
            result = (
                analyze_multiple_personal_colors(
                    images
                )
            )

        if result["success"]:
            st.session_state[
                "color_analysis_result"
            ] = result

        else:
            st.session_state.pop(
                "color_analysis_result",
                None
            )

            st.error(
                result["message"]
            )

    result = st.session_state.get(
        "color_analysis_result"
    )

    if result is not None:
        st.divider()

        valid_count = result.get(
            "valid_count",
            1
        )

        total_count = result.get(
            "total_count",
            valid_count
        )

        failed_count = result.get(
            "failed_count",
            0
        )

        if failed_count:
            st.warning(
                f"{total_count}장 중 {valid_count}장의 "
                "색상값을 종합했습니다. "
                f"{failed_count}장은 분석에서 제외되었습니다."
            )

        else:
            st.success(
                f"{valid_count}장의 사진 색상값을 "
                "종합했습니다."
            )

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

                st.code(
                    str(error)
                )

        else:
            st.warning(
                "분석 결과와 일치하는 팔레트가 없습니다."
            )

        metric_column1, metric_column2 = (
            st.columns(2)
        )

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

        st.write(
            result["description"]
        )

        st.markdown(
            "#### Recommended Colors"
        )

        st.write(
            " · ".join(
                result["recommended_colors"]
            )
        )

        with st.expander(
            "View combined analysis details"
        ):
            st.json(
                result["color_features"]
            )

        individual_results = result.get(
            "individual_results",
            []
        )

        with st.expander(
            "View individual photo results"
        ):
            for item in individual_results:
                image_number = (
                    item["image_index"] + 1
                )

                st.markdown(
                    f"#### Photo {image_number}"
                )

                if item["success"]:
                    st.write(
                        f'Season: {item["season"]}'
                    )

                    st.write(
                        f'Undertone: {item["undertone"]}'
                    )

                    st.json(
                        item["color_features"]
                    )

                else:
                    st.error(
                        item["message"]
                    )

        st.caption(
            "이 결과는 사진 속 색상값을 기반으로 한 "
            "간단한 추정 결과입니다. 조명, 카메라 보정, "
            "필터, 화장과 배경색에 따라 달라질 수 있습니다."
        )