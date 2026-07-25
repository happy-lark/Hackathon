import streamlit as st

from utils.navigation import go_to_page


PERSONA_NAMES = [
    "Professional",
    "Confident",
    "Approachable",
    "Creative"
]

DEFAULT_SLIDER_VALUES = {
    "Professional": 25,
    "Confident": 25,
    "Approachable": 25,
    "Creative": 25
}

PERSONA_COLORS = {
    "Professional": "#4F67E8",
    "Confident": "#6750E8",
    "Approachable": "#8A65F0",
    "Creative": "#4EA4E8"
}


def initialize_slider_values():
    """
    저장된 슬라이더 값을 Streamlit 위젯 상태에 적용합니다.
    """
    saved_values = st.session_state.get(
        "target_slider_values",
        {}
    )

    if not isinstance(saved_values, dict):
        saved_values = {}

    # 이전 항목이 남아 있는 경우 Creative 값으로 이전
    if "Creative" not in saved_values:
        if "Warm" in saved_values:
            saved_values["Creative"] = saved_values["Warm"]

        elif "Trustworthy" in saved_values:
            saved_values["Creative"] = saved_values[
                "Trustworthy"
            ]

    for persona_name in PERSONA_NAMES:
        widget_key = (
            f"target_{persona_name.lower()}_slider"
        )

        if widget_key not in st.session_state:
            saved_value = saved_values.get(
                persona_name,
                DEFAULT_SLIDER_VALUES[persona_name]
            )

            try:
                saved_value = int(saved_value)

            except (TypeError, ValueError):
                saved_value = DEFAULT_SLIDER_VALUES[
                    persona_name
                ]

            st.session_state[widget_key] = max(
                0,
                min(100, saved_value)
            )


def normalize_target_persona(slider_values):
    """
    슬라이더 값을 합계 100%로 정규화합니다.
    """
    total = sum(slider_values.values())

    if total == 0:
        return {
            "Professional": 25.0,
            "Confident": 25.0,
            "Approachable": 25.0,
            "Creative": 25.0
        }

    return {
        persona_name: round(
            slider_values[persona_name] / total * 100,
            1
        )
        for persona_name in PERSONA_NAMES
    }


def get_top_personas(normalized_persona):
    """
    비율이 높은 상위 세 가지 persona를 반환합니다.
    """
    sorted_personas = sorted(
        normalized_persona.items(),
        key=lambda item: item[1],
        reverse=True
    )

    return [
        persona_name
        for persona_name, score in sorted_personas[:3]
    ]


def format_persona_names(persona_names):
    """
    Professional, Approachable, and Confident 형식으로 만듭니다.
    """
    if len(persona_names) == 1:
        return persona_names[0]

    if len(persona_names) == 2:
        return (
            f"{persona_names[0]} and "
            f"{persona_names[1]}"
        )

    return (
        f"{persona_names[0]}, "
        f"{persona_names[1]}, and "
        f"{persona_names[2]}"
    )


def build_donut_gradient(normalized_persona):
    """
    CSS conic-gradient용 문자열을 생성합니다.
    """
    gradient_sections = []
    start_point = 0.0

    for index, persona_name in enumerate(
        PERSONA_NAMES
    ):
        if index == len(PERSONA_NAMES) - 1:
            end_point = 100.0

        else:
            end_point = min(
                100.0,
                start_point
                + normalized_persona[persona_name]
            )

        gradient_sections.append(
            f"{PERSONA_COLORS[persona_name]} "
            f"{start_point:.1f}% "
            f"{end_point:.1f}%"
        )

        start_point = end_point

    return (
        "conic-gradient("
        + ", ".join(gradient_sections)
        + ")"
    )


def show_target_page():
    initialize_slider_values()

    outer_left, content_column, outer_right = (
        st.columns([0.6, 5, 0.6])
    )

    with content_column:
        # =========================
        # 상단 Back / 단계 표시
        # =========================
        back_column, progress_column, empty_column = (
            st.columns(
                [1.2, 4.2, 1.2],
                vertical_alignment="center"
            )
        )

        with back_column:
            if st.button(
                "‹  Back",
                key="target_top_back",
                use_container_width=True
            ):
                go_to_page("service_intro")

        with progress_column:
            st.markdown(
                '<div class="target-progress">'
                '<span class="target-progress-dot active">1</span>'
                '<span class="target-progress-line"></span>'
                '<span class="target-progress-dot">2</span>'
                '<span class="target-progress-line"></span>'
                '<span class="target-progress-dot">3</span>'
                '<span class="target-progress-line"></span>'
                '<span class="target-progress-dot">4</span>'
                '<span class="target-progress-line"></span>'
                '<span class="target-progress-dot">5</span>'
                '</div>',
                unsafe_allow_html=True
            )

        # =========================
        # 제목
        # =========================
        st.markdown(
            '<div class="target-page-header">'
            '<div class="target-page-title">'
            'Step 1. Choose Your Target Persona'
            '</div>'
            '<div class="target-page-description">'
            'How do you want to be perceived?'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

        # =========================
        # 슬라이더
        # =========================
        slider_values = {}

        for persona_name in PERSONA_NAMES:
            widget_key = (
                f"target_{persona_name.lower()}_slider"
            )

            current_value = int(
                st.session_state.get(
                    widget_key,
                    DEFAULT_SLIDER_VALUES[
                        persona_name
                    ]
                )
            )

            st.markdown(
                '<div class="target-slider-header">'
                f'<span>{persona_name}</span>'
                f'<strong>{current_value}%</strong>'
                '</div>',
                unsafe_allow_html=True
            )

            slider_values[persona_name] = st.slider(
                persona_name,
                min_value=0,
                max_value=100,
                step=1,
                key=widget_key,
                label_visibility="collapsed"
            )

            st.markdown(
                '<div class="target-slider-spacing"></div>',
                unsafe_allow_html=True
            )

        st.session_state[
            "target_slider_values"
        ] = slider_values

        normalized_persona = (
            normalize_target_persona(
                slider_values
            )
        )

        st.session_state[
            "target_persona"
        ] = normalized_persona

        if sum(slider_values.values()) == 0:
            st.warning(
                "All values are set to zero, so each "
                "persona is currently calculated as 25%."
            )

        # =========================
        # Persona Summary
        # =========================
        top_personas = get_top_personas(
            normalized_persona
        )

        persona_text = format_persona_names(
            top_personas
        )

        summary_text = (
            f"You want to be seen as: {persona_text}."
        )

        st.session_state[
            "target_persona_summary"
        ] = summary_text

        donut_gradient = build_donut_gradient(
            normalized_persona
        )

        st.markdown(
            '<div class="target-summary-card">'
            '<div class="target-summary-content">'
            '<div class="target-summary-title">'
            'Your Persona Summary'
            '</div>'
            '<div class="target-summary-label">'
            'You want to be seen as:'
            '</div>'
            '<div class="target-summary-personas">'
            f'{persona_text}.'
            '</div>'
            '</div>'
            '<div class="target-donut-wrapper">'
            '<div class="target-donut" '
            f'style="background: {donut_gradient};">'
            '<div class="target-donut-hole"></div>'
            '</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

        # =========================
        # Continue 버튼
        # =========================
        st.markdown(
            '<div class="target-continue-space"></div>',
            unsafe_allow_html=True
        )

        if st.button(
            "Continue",
            key="target_continue_button",
            type="primary",
            use_container_width=True
        ):
            go_to_page("context")