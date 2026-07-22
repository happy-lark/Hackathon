import streamlit as st

from utils.navigation import go_to_page


def normalize_target_persona(
    warm,
    confident,
    professional,
    approachable
):
    total = (
        warm
        + confident
        + professional
        + approachable
    )

    if total == 0:
        return {
            "Warm": 25.0,
            "Confident": 25.0,
            "Professional": 25.0,
            "Approachable": 25.0
        }

    return {
        "Warm": round(
            warm / total * 100,
            1
        ),
        "Confident": round(
            confident / total * 100,
            1
        ),
        "Professional": round(
            professional / total * 100,
            1
        ),
        "Approachable": round(
            approachable / total * 100,
            1
        )
    }


def show_target_page():
    st.markdown(
        '<div class="step-text">STEP 2 OF 3</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="page-title">
            Set Your Target Persona
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="page-description">
            사진에서 전달하고 싶은 인상의 비율을 설정해주세요.<br>
            네 값의 합은 자동으로 100%로 변환됩니다.
        </div>
        """,
        unsafe_allow_html=True
    )

    slider_values = st.session_state[
        "target_slider_values"
    ]

    warm = st.slider(
        "☀️ Warm",
        min_value=0,
        max_value=100,
        value=slider_values["Warm"],
        key="warm_slider"
    )

    confident = st.slider(
        "💪 Confident",
        min_value=0,
        max_value=100,
        value=slider_values["Confident"],
        key="confident_slider"
    )

    professional = st.slider(
        "💼 Professional",
        min_value=0,
        max_value=100,
        value=slider_values["Professional"],
        key="professional_slider"
    )

    approachable = st.slider(
        "🌷 Approachable",
        min_value=0,
        max_value=100,
        value=slider_values["Approachable"],
        key="approachable_slider"
    )

    st.session_state[
        "target_slider_values"
    ] = {
        "Warm": warm,
        "Confident": confident,
        "Professional": professional,
        "Approachable": approachable
    }

    normalized_persona = normalize_target_persona(
        warm,
        confident,
        professional,
        approachable
    )

    st.session_state[
        "target_persona"
    ] = normalized_persona

    if (
        warm
        + confident
        + professional
        + approachable
        == 0
    ):
        st.warning(
            "모든 값을 0으로 설정할 수 없습니다. "
            "현재는 각 항목을 25%로 계산합니다."
        )

    st.caption("Normalized Target Persona")

    column1, column2, column3, column4 = st.columns(
        4
    )

    column1.metric(
        "Warm",
        f"{normalized_persona['Warm']}%"
    )

    column2.metric(
        "Confident",
        f"{normalized_persona['Confident']}%"
    )

    column3.metric(
        "Professional",
        f"{normalized_persona['Professional']}%"
    )

    column4.metric(
        "Approachable",
        f"{normalized_persona['Approachable']}%"
    )

    st.write("")

    back_column, space, next_column = st.columns(
        [1, 2, 1]
    )

    with back_column:
        if st.button(
            "← Back",
            use_container_width=True
        ):
            go_to_page("mode")

    with next_column:
        if st.button(
            "Next →",
            type="primary",
            use_container_width=True
        ):
            go_to_page("upload")