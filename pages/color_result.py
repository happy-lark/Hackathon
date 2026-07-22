import streamlit as st

from utils.navigation import (
    go_to_page,
    reset_all
)


def show_color_result_page():

    if "color_analysis_result" not in st.session_state:

        st.error(
            "분석 결과를 찾을 수 없습니다."
        )

        if st.button(
            "Return",
            use_container_width=True
        ):
            go_to_page("personal_color")

        return

    result = st.session_state[
        "color_analysis_result"
    ]

    st.markdown(
        """
        <div class="page-title">
            Your Personal Color 🎨
        </div>
        """,
        unsafe_allow_html=True
    )

    if "uploaded_image" in st.session_state:

        st.image(
            st.session_state[
                "uploaded_image"
            ],
            caption="Analyzed Photo",
            use_container_width=True
        )

    st.divider()

    st.subheader(
        "🌈 Analysis Result"
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "Season",
        result["season"]
    )

    col2.metric(
        "Tone",
        result["tone"]
    )

    st.markdown(
        f"""
        <div class="info-card">
            {result["description"]}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.subheader(
        "🎨 Recommended Colors"
    )

    colors = result[
        "recommended_colors"
    ]

    columns = st.columns(
        len(colors)
    )

    for column, color in zip(
        columns,
        colors
    ):

        column.markdown(
            f"""
            <div style="
                background:{color['hex']};
                height:80px;
                border-radius:12px;
                border:1px solid #DDD;
            ">
            </div>

            <div style="
                text-align:center;
                margin-top:8px;
                font-weight:600;
            ">
                {color['name']}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    st.subheader(
        "📊 Skin Color Features"
    )

    features = result["features"]

    for key, value in features.items():

        st.metric(
            key,
            round(value, 2)
        )

    st.markdown(
        """
        <div class="result-notice">
            본 결과는 피부 영역의 평균 색상을 기반으로 한
            간이 퍼스널 컬러 분석입니다.
            실제 전문 퍼스널 컬러 진단과는 차이가 있을 수 있습니다.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    back_column, space, restart_column = st.columns(
        [1, 2, 1]
    )

    with back_column:

        if st.button(
            "← Back",
            use_container_width=True
        ):
            go_to_page(
                "personal_color"
            )

    with restart_column:

        if st.button(
            "Start Again",
            type="primary",
            use_container_width=True
        ):
            reset_all()