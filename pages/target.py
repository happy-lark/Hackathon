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
        clean_html(html_content),
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
        numeric_value = int(value)

    except (TypeError, ValueError):
        numeric_value = 0

    return max(
        0,
        min(100, numeric_value)
    )


def normalize_integer_values(
    values,
    total=100
):
    """
    여러 값을 기존 비율에 따라 정수로 재분배하고
    합계를 정확히 total로 맞춥니다.

    Largest Remainder 방식으로 반올림 오차를 처리합니다.
    """

    cleaned_values = {
        name: max(
            0,
            float(
                values.get(name, 0)
            )
        )
        for name in PERSONA_NAMES
    }

    current_total = sum(
        cleaned_values.values()
    )

    if current_total <= 0:
        base_value = (
            total
            // len(PERSONA_NAMES)
        )

        remainder = (
            total
            - base_value
            * len(PERSONA_NAMES)
        )

        result = {
            name: base_value
            for name in PERSONA_NAMES
        }

        for name in PERSONA_NAMES[
            :remainder
        ]:
            result[name] += 1

        return result

    exact_values = {
        name: (
            cleaned_values[name]
            / current_total
            * total
        )
        for name in PERSONA_NAMES
    }

    integer_values = {
        name: int(
            exact_values[name]
        )
        for name in PERSONA_NAMES
    }

    remaining_points = (
        total
        - sum(
            integer_values.values()
        )
    )

    remainder_order = sorted(
        PERSONA_NAMES,
        key=lambda name: (
            exact_values[name]
            - integer_values[name]
        ),
        reverse=True
    )

    for name in remainder_order[
        :remaining_points
    ]:
        integer_values[name] += 1

    return integer_values


def initialize_slider_values():
    """
    저장된 값을 불러오고 합계를 정확히 100으로 맞춥니다.
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

    # 이전 버전의 Persona 이름을 Creative로 이전
    if "Creative" not in saved_values:
        if "Warm" in saved_values:
            saved_values["Creative"] = (
                saved_values["Warm"]
            )

        elif "Trustworthy" in saved_values:
            saved_values["Creative"] = (
                saved_values["Trustworthy"]
            )

    current_values = {}

    for persona_name in PERSONA_NAMES:
        widget_key = get_slider_widget_key(
            persona_name
        )

        if widget_key in st.session_state:
            current_values[
                persona_name
            ] = clamp_slider_value(
                st.session_state[
                    widget_key
                ]
            )

        else:
            current_values[
                persona_name
            ] = clamp_slider_value(
                saved_values.get(
                    persona_name,
                    DEFAULT_SLIDER_VALUES[
                        persona_name
                    ]
                )
            )

    normalized_values = (
        normalize_integer_values(
            current_values,
            total=100
        )
    )

    for persona_name in PERSONA_NAMES:
        widget_key = get_slider_widget_key(
            persona_name
        )

        st.session_state[
            widget_key
        ] = normalized_values[
            persona_name
        ]


def rebalance_slider_values(
    changed_persona
):
    """
    한 슬라이더가 변경되면 나머지 세 슬라이더를
    자동 조정해 전체 합계를 100으로 유지합니다.
    """

    changed_key = get_slider_widget_key(
        changed_persona
    )

    changed_value = clamp_slider_value(
        st.session_state.get(
            changed_key,
            0
        )
    )

    st.session_state[
        changed_key
    ] = changed_value

    remaining_total = (
        100
        - changed_value
    )

    other_personas = [
        name
        for name in PERSONA_NAMES
        if name != changed_persona
    ]

    other_values = {
        name: clamp_slider_value(
            st.session_state.get(
                get_slider_widget_key(name),
                0
            )
        )
        for name in other_personas
    }

    other_sum = sum(
        other_values.values()
    )

    # 나머지 항목이 모두 0이면 균등 분배
    if other_sum <= 0:
        base_value = (
            remaining_total
            // len(other_personas)
        )

        remainder = (
            remaining_total
            - base_value
            * len(other_personas)
        )

        redistributed_values = {
            name: base_value
            for name in other_personas
        }

        for name in other_personas[
            :remainder
        ]:
            redistributed_values[name] += 1

    else:
        exact_values = {
            name: (
                other_values[name]
                / other_sum
                * remaining_total
            )
            for name in other_personas
        }

        redistributed_values = {
            name: int(
                exact_values[name]
            )
            for name in other_personas
        }

        missing_points = (
            remaining_total
            - sum(
                redistributed_values.values()
            )
        )

        remainder_order = sorted(
            other_personas,
            key=lambda name: (
                exact_values[name]
                - redistributed_values[name]
            ),
            reverse=True
        )

        for name in remainder_order[
            :missing_points
        ]:
            redistributed_values[name] += 1

    for persona_name in other_personas:
        widget_key = get_slider_widget_key(
            persona_name
        )

        st.session_state[
            widget_key
        ] = redistributed_values[
            persona_name
        ]


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
            persona_values[
                persona_name
            ]
        )
        for persona_name in PERSONA_NAMES
        if persona_values[
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
    Persona 이름 목록을 자연스러운 문장으로 변환합니다.
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
    persona_values
):
    """
    합계가 100인 Persona 값으로
    CSS conic-gradient를 생성합니다.
    """

    active_personas = [
        persona_name
        for persona_name in PERSONA_NAMES
        if persona_values[
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
            end_point = 100.0

        else:
            end_point = (
                start_point
                + persona_values[
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
    persona_values
):
    """
    Persona 색상, 이름, 퍼센트를 표시하는
    범례 HTML을 생성합니다.
    """

    legend_items = []

    for persona_name in PERSONA_NAMES:
        color = PERSONA_COLORS[
            persona_name
        ]

        score = persona_values[
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
    Back 버튼과 단계 표시를 렌더링합니다.
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
    합계가 항상 100인 Persona 슬라이더를 표시합니다.
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
            label_visibility="collapsed",
            on_change=rebalance_slider_values,
            args=(persona_name,)
        )

        render_html(
            '<div class="target-slider-spacing"></div>'
        )

    return slider_values


def show_persona_summary(
    persona_values
):
    """
    Persona 요약, 범례, 도넛 그래프를 표시합니다.
    """

    top_personas = get_top_personas(
        persona_values
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
        persona_values
    )

    legend_html = build_persona_legend(
        persona_values
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
                    Total: 100%
                </div>
            </div>

            <div class="target-donut-wrapper">
                <div
                    class="target-donut"
                    style="background: {donut_gradient};"
                >
                    <div class="target-donut-hole">
                        <span>100%</span>
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

        slider_values = (
            show_persona_sliders()
        )

        # callback 실행 후 session_state의 최신 값을 다시 읽습니다.
        persona_values = {
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

        # 안전장치: 합계가 100이 아닌 경우 재정규화
        if sum(
            persona_values.values()
        ) != 100:
            persona_values = (
                normalize_integer_values(
                    persona_values,
                    total=100
                )
            )

            for persona_name in PERSONA_NAMES:
                st.session_state[
                    get_slider_widget_key(
                        persona_name
                    )
                ] = persona_values[
                    persona_name
                ]

        st.session_state[
            "target_slider_values"
        ] = persona_values.copy()

        st.session_state[
            "target_persona"
        ] = persona_values.copy()

        st.session_state[
            "target_persona_distribution"
        ] = persona_values.copy()

        show_persona_summary(
            persona_values
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