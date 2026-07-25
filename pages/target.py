from textwrap import dedent

import streamlit as st

from utils.navigation import go_to_page


TOTAL_STEPS = 7
CURRENT_STEP = 1


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
    HTML의 들여쓰기와 불필요한 줄바꿈을 제거합니다.
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
        clean_html(
            html_content
        ),
        unsafe_allow_html=True
    )


def get_slider_widget_key(persona_name):
    """
    Persona에 해당하는 슬라이더 key를 반환합니다.
    """

    return (
        f"target_"
        f"{persona_name.lower()}_slider"
    )


def clamp_slider_value(value):
    """
    값을 정수로 변환하고 0~100 범위로 제한합니다.
    """

    try:
        numeric_value = int(
            value
        )

    except (TypeError, ValueError):
        numeric_value = 0

    return max(
        0,
        min(
            100,
            numeric_value
        )
    )


def normalize_integer_values(
    values,
    total=100
):
    """
    사용자가 입력한 각 Persona의 상대적인 비율을 유지하면서
    Summary용 값의 합계를 정확히 100으로 맞춥니다.

    슬라이더 원본 값은 변경하지 않습니다.

    Largest Remainder 방식으로
    정수 반올림 오차를 처리합니다.
    """

    cleaned_values = {
        persona_name: max(
            0.0,
            float(
                values.get(
                    persona_name,
                    0
                )
            )
        )
        for persona_name in PERSONA_NAMES
    }

    current_total = sum(
        cleaned_values.values()
    )

    # 모두 0인 경우에는 균등한 기본 비율을 사용합니다.
    if current_total <= 0:
        base_value = (
            total
            // len(
                PERSONA_NAMES
            )
        )

        remainder = (
            total
            - (
                base_value
                * len(
                    PERSONA_NAMES
                )
            )
        )

        normalized_values = {
            persona_name: base_value
            for persona_name in PERSONA_NAMES
        }

        for persona_name in PERSONA_NAMES[
            :remainder
        ]:
            normalized_values[
                persona_name
            ] += 1

        return normalized_values

    exact_values = {
        persona_name: (
            cleaned_values[
                persona_name
            ]
            / current_total
            * total
        )
        for persona_name in PERSONA_NAMES
    }

    integer_values = {
        persona_name: int(
            exact_values[
                persona_name
            ]
        )
        for persona_name in PERSONA_NAMES
    }

    remaining_points = (
        total
        - sum(
            integer_values.values()
        )
    )

    remainder_order = sorted(
        PERSONA_NAMES,
        key=lambda persona_name: (
            exact_values[
                persona_name
            ]
            - integer_values[
                persona_name
            ]
        ),
        reverse=True
    )

    for persona_name in remainder_order[
        :remaining_points
    ]:
        integer_values[
            persona_name
        ] += 1

    return integer_values


def initialize_slider_values():
    """
    저장된 슬라이더 원본 값을 불러옵니다.

    이 함수에서는 합계를 100으로 조정하지 않습니다.
    각각의 슬라이더는 서로 독립적으로 유지됩니다.
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

    # 이전 프로젝트 키와의 호환성
    if "Creative" not in saved_values:
        if "Warm" in saved_values:
            saved_values[
                "Creative"
            ] = saved_values[
                "Warm"
            ]

        elif "Trustworthy" in saved_values:
            saved_values[
                "Creative"
            ] = saved_values[
                "Trustworthy"
            ]

    for persona_name in PERSONA_NAMES:
        widget_key = get_slider_widget_key(
            persona_name
        )

        if widget_key not in st.session_state:
            st.session_state[
                widget_key
            ] = clamp_slider_value(
                saved_values.get(
                    persona_name,
                    DEFAULT_SLIDER_VALUES[
                        persona_name
                    ]
                )
            )


def get_top_personas(
    persona_values,
    limit=3
):
    """
    값이 0보다 큰 Persona를 높은 순서로 반환합니다.
    """

    active_personas = [
        (
            persona_name,
            persona_values.get(
                persona_name,
                0
            )
        )
        for persona_name in PERSONA_NAMES
        if persona_values.get(
            persona_name,
            0
        ) > 0
    ]

    active_personas.sort(
        key=lambda item: (
            item[1]
        ),
        reverse=True
    )

    return [
        persona_name
        for persona_name, _
        in active_personas[
            :limit
        ]
    ]


def format_persona_names(
    persona_names
):
    """
    Persona 이름 목록을 자연스러운 문장으로 변환합니다.
    """

    if not persona_names:
        return ""

    if len(
        persona_names
    ) == 1:
        return persona_names[0]

    if len(
        persona_names
    ) == 2:
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
    normalized_values
):
    """
    합계가 정확히 100인 Summary 값을 이용해
    CSS conic-gradient를 생성합니다.
    """

    active_personas = [
        persona_name
        for persona_name in PERSONA_NAMES
        if normalized_values.get(
            persona_name,
            0
        ) > 0
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
        if index == (
            len(
                active_personas
            )
            - 1
        ):
            end_point = 100.0

        else:
            end_point = (
                start_point
                + normalized_values[
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
    normalized_values
):
    """
    Summary에 정규화된 Persona 비율을 표시합니다.

    이 값들의 합계는 항상 100입니다.
    """

    legend_items = []

    for persona_name in PERSONA_NAMES:
        color = PERSONA_COLORS[
            persona_name
        ]

        score = normalized_values.get(
            persona_name,
            0
        )

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


def build_progress_html():
    """
    현재 단계에 맞춰 1~7단계 진행 표시 HTML을 생성합니다.
    """

    progress_parts = []

    for step in range(
        1,
        TOTAL_STEPS + 1
    ):
        if step < CURRENT_STEP:
            state_class = "completed"

        elif step == CURRENT_STEP:
            state_class = "active"

        else:
            state_class = ""

        progress_parts.append(
            f"""
            <span class="target-progress-dot {state_class}">
                {step}
            </span>
            """
        )

        if step < TOTAL_STEPS:
            line_class = (
                "completed"
                if step < CURRENT_STEP
                else ""
            )

            progress_parts.append(
                f"""
                <span class="target-progress-line {line_class}">
                </span>
                """
            )

    return "".join(
        progress_parts
    )


def show_progress_header():
    """
    Back 버튼과 1~7단계 진행 표시를 렌더링합니다.
    """

    (
        back_column,
        progress_column,
        empty_column
    ) = st.columns(
        [1.05, 5.4, 1.05],
        vertical_alignment="center"
    )

    with back_column:
        if st.button(
            "‹ Back",
            key="target_top_back"
        ):
            go_to_page(
                "service_intro"
            )

    with progress_column:
        render_html(
            f"""
            <div class="target-progress">
                {build_progress_html()}
            </div>
            """
        )

    with empty_column:
        st.empty()


def show_page_header():
    """
    Target Persona 페이지 제목을 표시합니다.
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
    서로 독립적인 Persona 슬라이더를 표시합니다.

    각 슬라이더는 사용자가 자유롭게 0~100 사이에서 설정하며,
    다른 슬라이더의 값은 자동으로 변경되지 않습니다.
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

                <strong>
                    {current_value}%
                </strong>
            </div>
            """
        )

        # on_change와 rebalance 로직을 제거했습니다.
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
    raw_values,
    normalized_values
):
    """
    사용자의 원본 슬라이더 비율을 100%로 정규화하여
    Persona Summary, 범례, 도넛 그래프를 표시합니다.
    """

    raw_total = sum(
        raw_values.values()
    )

    top_personas = get_top_personas(
        normalized_values
    )

    persona_text = format_persona_names(
        top_personas
    )

    if raw_total <= 0:
        summary_text = (
            "No specific persona preference "
            "has been selected."
        )

        persona_summary_html = (
            "No specific preference selected."
        )

    elif top_personas:
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
        normalized_values
    )

    legend_html = build_persona_legend(
        normalized_values
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

                <div class="target-summary-total">
                    Normalized total: 100%
                </div>
            </div>

            <div class="target-donut-wrapper">
                <div
                    class="target-donut"
                    style="background: {donut_gradient};"
                >
                    <div class="target-donut-hole">
                        <span>
                            100%
                        </span>
                    </div>
                </div>
            </div>
        </div>
        """
    )


def clear_previous_results():
    """
    Target Persona가 변경된 경우
    이전 분석 결과를 제거합니다.
    """

    keys_to_remove = [
        "analysis_result",
        "analysis_status",
        "analysis_error_result",
        "photo_ranking",
        "best_photo_index",
        "selected_photo_index",
        "best_match_score",
        "selected_photo_match_score",
        "selected_photo_alignment",
        "match_report_strengths",
        "match_report_improvements",
        "match_report_color_result",
        "match_report_color_index"
    ]

    for key in keys_to_remove:
        st.session_state.pop(
            key,
            None
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

        show_persona_sliders()

        # 사용자가 실제로 입력한 원본 슬라이더 값
        raw_persona_values = {
            persona_name: clamp_slider_value(
                st.session_state.get(
                    get_slider_widget_key(
                        persona_name
                    ),
                    0
                )
            )
            for persona_name in PERSONA_NAMES
        }

        # Summary와 이후 분석에 사용할 100% 정규화 값
        normalized_persona_values = (
            normalize_integer_values(
                raw_persona_values,
                total=100
            )
        )

        # 사용자가 직접 입력한 원본 값
        st.session_state[
            "target_slider_values"
        ] = raw_persona_values.copy()

        st.session_state[
            "target_persona_raw"
        ] = raw_persona_values.copy()

        # 분석 및 Match Score 계산에는 정규화된 값 사용
        st.session_state[
            "target_persona"
        ] = normalized_persona_values.copy()

        st.session_state[
            "target_persona_distribution"
        ] = normalized_persona_values.copy()

        st.session_state[
            "target_persona_normalized"
        ] = normalized_persona_values.copy()

        show_persona_summary(
            raw_values=raw_persona_values,
            normalized_values=normalized_persona_values
        )

        render_html(
            '<div class="target-continue-space"></div>'
        )

        if st.button(
            "Continue",
            key="target_continue_button",
            type="primary",
            use_container_width=True
        ):
            clear_previous_results()

            go_to_page(
                "context"
            )