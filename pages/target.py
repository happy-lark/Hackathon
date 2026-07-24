from textwrap import dedent

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
    "Professional": "#3B82F6",
    "Confident": "#7C3AED",
    "Approachable": "#10B981",
    "Creative": "#F59E0B"
}


def clean_html(html_content):
    """
    HTML의 들여쓰기, 줄바꿈, 빈 줄을 제거합니다.

    Streamlit에서 HTML이 코드 블록으로 표시되는
    문제를 방지합니다.
    """

    return " ".join(
        line.strip()
        for line in dedent(
            html_content
        ).strip().splitlines()
        if line.strip()
    )


def render_html(html_content):
    """
    HTML을 Streamlit 화면에 렌더링합니다.
    """

    st.markdown(
        clean_html(html_content),
        unsafe_allow_html=True
    )


def get_slider_widget_key(persona_name):
    """
    Persona 이름에 해당하는 Streamlit 슬라이더 키를 반환합니다.
    """

    return (
        f"target_"
        f"{persona_name.lower()}_slider"
    )


def clamp_slider_value(value):
    """
    슬라이더 값을 정수로 변환하고 0~100 범위로 제한합니다.
    """

    try:
        numeric_value = int(value)

    except (TypeError, ValueError):
        numeric_value = 0

    return max(
        0,
        min(100, numeric_value)
    )


def initialize_slider_values():
    """
    저장된 Target Persona 값을 슬라이더 위젯 상태에 적용합니다.
    """

    saved_values = st.session_state.get(
        "target_slider_values",
        {}
    )

    if not isinstance(
        saved_values,
        dict
    ):
        saved_values = {}

    # 이전 버전의 Persona 이름을 Creative로 이전합니다.
    if "Creative" not in saved_values:
        if "Warm" in saved_values:
            saved_values["Creative"] = (
                saved_values["Warm"]
            )

        elif "Trustworthy" in saved_values:
            saved_values["Creative"] = (
                saved_values["Trustworthy"]
            )

    for persona_name in PERSONA_NAMES:
        widget_key = get_slider_widget_key(
            persona_name
        )

        # 이미 생성된 위젯 값은 덮어쓰지 않습니다.
        if widget_key in st.session_state:
            continue

        saved_value = saved_values.get(
            persona_name,
            DEFAULT_SLIDER_VALUES[
                persona_name
            ]
        )

        st.session_state[
            widget_key
        ] = clamp_slider_value(
            saved_value
        )


def normalize_target_persona(
    slider_values
):
    """
    도넛 그래프 표시를 위해 슬라이더 값을
    합계 100%의 비율로 변환합니다.

    Ranking 비교에는 이 값이 아닌 원래 슬라이더 값을 사용합니다.
    """

    total = sum(
        slider_values.values()
    )

    if total <= 0:
        return {
            persona_name: 0.0
            for persona_name in PERSONA_NAMES
        }

    normalized_values = {}

    for persona_name in PERSONA_NAMES:
        normalized_values[
            persona_name
        ] = round(
            (
                slider_values[
                    persona_name
                ]
                / total
            )
            * 100,
            1
        )

    return normalized_values


def get_top_personas(
    slider_values,
    limit=3
):
    """
    슬라이더 값이 0보다 큰 Persona만
    점수가 높은 순서로 반환합니다.
    """

    active_personas = [
        (
            persona_name,
            slider_values[
                persona_name
            ]
        )
        for persona_name in PERSONA_NAMES
        if slider_values[
            persona_name
        ] > 0
    ]

    active_personas.sort(
        key=lambda item: item[1],
        reverse=True
    )

    return [
        persona_name
        for persona_name, _
        in active_personas[:limit]
    ]


def format_persona_names(
    persona_names
):
    """
    Persona 이름 목록을 자연스러운 영어 문장으로 변환합니다.
    """

    if not persona_names:
        return ""

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


def build_donut_gradient(
    normalized_persona
):
    """
    점수가 0보다 큰 항목만 사용하여
    CSS conic-gradient 문자열을 생성합니다.
    """

    active_personas = [
        persona_name
        for persona_name in PERSONA_NAMES
        if normalized_persona[
            persona_name
        ] > 0
    ]

    if not active_personas:
        return (
            "conic-gradient("
            "#ECEAF2 0% 100%"
            ")"
        )

    gradient_sections = []
    start_point = 0.0

    for index, persona_name in enumerate(
        active_personas
    ):
        if index == len(
            active_personas
        ) - 1:
            # 반올림 오차가 있어도 마지막 항목은
            # 반드시 100%까지 채웁니다.
            end_point = 100.0

        else:
            end_point = min(
                100.0,
                start_point
                + normalized_persona[
                    persona_name
                ]
            )

        color = PERSONA_COLORS[
            persona_name
        ]

        gradient_sections.append(
            f"{color} "
            f"{start_point:.1f}% "
            f"{end_point:.1f}%"
        )

        start_point = end_point

    return (
        "conic-gradient("
        + ", ".join(
            gradient_sections
        )
        + ")"
    )


def build_persona_legend(
    slider_values
):
    """
    Persona 색상, 이름, 원래 슬라이더 값을 표시하는
    범례 HTML을 생성합니다.
    """

    legend_items = []

    for persona_name in PERSONA_NAMES:
        color = PERSONA_COLORS[
            persona_name
        ]

        score = slider_values[
            persona_name
        ]

        opacity = (
            "1"
            if score > 0
            else "0.45"
        )

        legend_items.append(
            (
                '<div class="target-legend-item" '
                f'style="opacity: {opacity};">'

                '<span class="target-legend-color" '
                'style="'
                'display: inline-block; '
                'width: 11px; '
                'height: 11px; '
                'border-radius: 50%; '
                f'background-color: {color};'
                '">'
                '</span>'

                '<span class="target-legend-name">'
                f'{persona_name}'
                '</span>'

                '<span class="target-legend-value">'
                f'{score}%'
                '</span>'

                '</div>'
            )
        )

    return "".join(
        legend_items
    )


def show_progress_header():
    """
    Back 버튼과 5단계 진행 상태를 표시합니다.
    """

    (
        back_column,
        progress_column,
        empty_column
    ) = st.columns(
        [1.2, 4.2, 1.2],
        vertical_alignment="center"
    )

    with back_column:
        if st.button(
            "‹ Back",
            key="target_top_back",
            use_container_width=True
        ):
            go_to_page(
                "service_intro"
            )

    with progress_column:
        render_html(
            """
            <div class="target-progress">
                <span class="target-progress-dot active">1</span>
                <span class="target-progress-line"></span>
                <span class="target-progress-dot">2</span>
                <span class="target-progress-line"></span>
                <span class="target-progress-dot">3</span>
                <span class="target-progress-line"></span>
                <span class="target-progress-dot">4</span>
                <span class="target-progress-line"></span>
                <span class="target-progress-dot">5</span>
            </div>
            """
        )

    with empty_column:
        st.empty()


def show_page_header():
    """
    Target Persona 페이지의 제목과 설명을 표시합니다.
    """

    render_html(
        """
        <div class="target-page-header">
            <div class="target-page-title">
                Step 1. Choose Your Target Persona
            </div>

            <div class="target-page-description">
                How do you want to be perceived?
            </div>
        </div>
        """
    )


def show_persona_sliders():
    """
    네 가지 Target Persona 슬라이더를 표시하고
    현재 값을 반환합니다.
    """

    slider_values = {}

    for persona_name in PERSONA_NAMES:
        widget_key = get_slider_widget_key(
            persona_name
        )

        current_value = clamp_slider_value(
            st.session_state.get(
                widget_key,
                DEFAULT_SLIDER_VALUES[
                    persona_name
                ]
            )
        )

        persona_color = PERSONA_COLORS[
            persona_name
        ]

        render_html(
            f"""
            <div class="target-slider-header">
                <span class="target-slider-name">
                    <span
                        class="target-slider-color"
                        style="
                            display: inline-block;
                            width: 11px;
                            height: 11px;
                            margin-right: 8px;
                            border-radius: 50%;
                            background-color: {persona_color};
                        "
                    ></span>
                    {persona_name}
                </span>

                <strong>{current_value}%</strong>
            </div>
            """
        )

        slider_values[
            persona_name
        ] = st.slider(
            persona_name,
            min_value=0,
            max_value=100,
            step=1,
            key=widget_key,
            label_visibility="collapsed"
        )

        render_html(
            '<div class="target-slider-spacing"></div>'
        )

    return slider_values


def show_persona_summary(
    slider_values,
    normalized_persona
):
    """
    선택된 Persona 요약, 색상 범례, 도넛 그래프를 표시합니다.
    """

    top_personas = get_top_personas(
        slider_values
    )

    persona_text = format_persona_names(
        top_personas
    )

    if top_personas:
        summary_text = (
            "You want to be seen as: "
            f"{persona_text}."
        )

        persona_summary_html = (
            f"{persona_text}."
        )

    else:
        summary_text = (
            "No persona has been selected yet."
        )

        persona_summary_html = (
            "Adjust the sliders to create "
            "your target persona."
        )

    st.session_state[
        "target_persona_summary"
    ] = summary_text

    donut_gradient = build_donut_gradient(
        normalized_persona
    )

    legend_html = build_persona_legend(
        slider_values
    )

    render_html(
        f"""
        <div class="target-summary-card">
            <div class="target-summary-content">
                <div class="target-summary-title">
                    Your Persona Summary
                </div>

                <div class="target-summary-label">
                    You want to be seen as:
                </div>

                <div class="target-summary-personas">
                    {persona_summary_html}
                </div>

                <div class="target-summary-legend">
                    {legend_html}
                </div>
            </div>

            <div class="target-donut-wrapper">
                <div
                    class="target-donut"
                    style="background: {donut_gradient};"
                >
                    <div class="target-donut-hole"></div>
                </div>
            </div>
        </div>
        """
    )


def show_target_page():
    """
    Step 1. Target Persona 선택 페이지입니다.
    """

    initialize_slider_values()

    _, content_column, _ = st.columns(
        [0.6, 5, 0.6]
    )

    with content_column:
        show_progress_header()
        show_page_header()

        slider_values = (
            show_persona_sliders()
        )

        # 원래 슬라이더 값을 저장합니다.
        # Photo Comparison은 이 값을 사용하여
        # 사진별 Persona 점수와 비교합니다.
        st.session_state[
            "target_slider_values"
        ] = slider_values

        st.session_state[
            "target_persona"
        ] = slider_values.copy()

        # 도넛 그래프 표시용 정규화 비율입니다.
        normalized_persona = (
            normalize_target_persona(
                slider_values
            )
        )

        st.session_state[
            "target_persona_distribution"
        ] = normalized_persona

        all_values_zero = (
            sum(
                slider_values.values()
            )
            == 0
        )

        if all_values_zero:
            st.warning(
                "Choose at least one persona value "
                "greater than zero."
            )

        show_persona_summary(
            slider_values=slider_values,
            normalized_persona=normalized_persona
        )

        render_html(
            '<div class="target-continue-space"></div>'
        )

        if st.button(
            "Continue",
            key="target_continue_button",
            type="primary",
            use_container_width=True,
            disabled=all_values_zero
        ):
            # Target이 변경되면 이전 분석 및 Ranking 결과를 제거합니다.
            keys_to_remove = [
                "analysis_result",
                "analysis_status",
                "analysis_error_result",
                "photo_ranking",
                "best_photo_index",
                "selected_photo_index",
                "best_match_score"
            ]

            for key in keys_to_remove:
                st.session_state.pop(
                    key,
                    None
                )

            go_to_page(
                "upload"
            )