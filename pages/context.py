"""
pages/context.py

사진을 사용할 목적을 선택하는 Usage Context 페이지입니다.

선택된 목적은 이후 사진 추천, 크롭,
배경 및 이미지 보정 기준에 사용됩니다.
"""

from textwrap import dedent

import streamlit as st

from utils.navigation import go_to_page


TOTAL_STEPS = 7
CURRENT_STEP = 2


CONTEXT_OPTIONS = [
    {
        "key": "professional_profile",
        "icon": "▣",
        "title": "Professional Profile",
        "description": (
            "LinkedIn, company profile, alumni page"
        ),
        "color": "#6657E8",
        "background": "#F0EEFF",
    },
    {
        "key": "portfolio",
        "icon": "▱",
        "title": "Portfolio / Personal Website",
        "description": (
            "Showcase your work and yourself"
        ),
        "color": "#3978E9",
        "background": "#EEF5FF",
    },
    {
        "key": "networking",
        "icon": "♧",
        "title": "Networking / Conference",
        "description": (
            "Events, meetups, speaker profile"
        ),
        "color": "#8B5CF6",
        "background": "#F5F0FF",
    },
    {
        "key": "creator",
        "icon": "◉",
        "title": "Creator / Personal Brand",
        "description": (
            "YouTube, blog, social media"
        ),
        "color": "#E48A32",
        "background": "#FFF4E8",
    },
    {
        "key": "other",
        "icon": "⌁",
        "title": "Other",
        "description": "Other purposes",
        "color": "#22A38A",
        "background": "#ECFAF6",
    },
]


CONTEXT_OPTION_MAP = {
    option["key"]: option
    for option in CONTEXT_OPTIONS
}


def clean_html(html_content):
    """
    HTML의 들여쓰기와 줄바꿈을 제거합니다.
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


def initialize_context_state():
    """
    Usage Context 관련 session_state를 초기화합니다.
    """

    valid_option_keys = list(
        CONTEXT_OPTION_MAP.keys()
    )

    saved_context = st.session_state.get(
        "usage_context",
        valid_option_keys[0]
    )

    if saved_context not in valid_option_keys:
        saved_context = valid_option_keys[0]

    st.session_state[
        "usage_context"
    ] = saved_context


def build_progress_html():
    """
    1~7단계 진행 표시 HTML을 생성합니다.
    """

    parts = []

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

        parts.append(
            f"""
            <span
                class="context-progress-dot {state_class}"
            >
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

            parts.append(
                f"""
                <span
                    class="context-progress-line {line_class}"
                ></span>
                """
            )

    return "".join(
        parts
    )


def show_progress_header():
    """
    Back 버튼과 7단계 진행 상태를 표시합니다.
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
            key="context_back"
        ):
            go_to_page(
                "target"
            )

    with progress_column:
        render_html(
            f"""
            <div class="context-progress">
                {build_progress_html()}
            </div>
            """
        )

    with empty_column:
        st.empty()


def show_page_header():
    """
    Context 페이지 제목과 설명을 표시합니다.
    """

    render_html(
        """
        <div class="context-page-header">
            <div class="context-page-title">
                Step 2. Where will you use this photo?
            </div>

            <div class="context-page-description">
                Choose the main context for your image.
            </div>
        </div>
        """
    )


def render_context_card(
    option
):
    """
    하나의 Context 카드와 선택 버튼을 표시합니다.
    """

    is_selected = (
        st.session_state.get(
            "usage_context"
        )
        == option["key"]
    )

    selected_class = (
        "selected"
        if is_selected
        else ""
    )

    check_html = (
        """
        <div class="context-card-check">
            ✓
        </div>
        """
        if is_selected
        else ""
    )

    render_html(
        f"""
        <div class="context-card {selected_class}">
            <div
                class="context-card-icon"
                style="
                    color: {option["color"]};
                    background: {option["background"]};
                "
            >
                {option["icon"]}
            </div>

            <div class="context-card-text">
                <div class="context-card-title">
                    {option["title"]}
                </div>

                <div class="context-card-description">
                    {option["description"]}
                </div>
            </div>

            {check_html}
        </div>
        """
    )

    button_key = (
        f'context_card_{option["key"]}'
    )

    if st.button(
        option["title"],
        key=button_key,
        use_container_width=True
    ):
        st.session_state[
            "usage_context"
        ] = option["key"]

        st.rerun()


def show_context_options():
    """
    Usage Context 카드 목록을 표시합니다.
    """

    for option in CONTEXT_OPTIONS:
        render_context_card(
            option
        )

    selected_context = st.session_state.get(
        "usage_context"
    )

    selected_option = CONTEXT_OPTION_MAP[
        selected_context
    ]

    st.session_state[
        "usage_context_details"
    ] = {
        "key": selected_option["key"],
        "title": selected_option["title"],
        "description": selected_option[
            "description"
        ]
    }

    return selected_context


def clear_downstream_results():
    """
    Usage Context가 변경된 경우
    기존 분석 및 편집 결과를 제거합니다.
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
        "selected_photo_quality",
        "match_report_strengths",
        "match_report_improvements",
        "match_report_color_result",
        "match_report_color_index",
        "optimized_image",
        "edited_image",
        "original_match_score",
        "optimized_match_score",
        "improvement_summary",
        "improvement_report",
        "photo_editor_preview_result"
    ]

    for key in keys_to_remove:
        st.session_state.pop(
            key,
            None
        )


def show_context_page():
    """
    Step 2. Usage Context 선택 페이지입니다.
    """

    initialize_context_state()

    _, content_column, _ = st.columns(
        [0.45, 5.1, 0.45]
    )

    with content_column:
        show_progress_header()
        show_page_header()

        (
            option_left_space,
            option_column,
            option_right_space
        ) = st.columns(
            [0.45, 4.4, 0.45]
        )

        with option_column:
            selected_context = (
                show_context_options()
            )

            render_html(
                '<div class="context-continue-space"></div>'
            )

            continue_clicked = st.button(
                "Continue",
                type="primary",
                use_container_width=True,
                key="context_continue_button",
                disabled=not selected_context
            )

        if continue_clicked:
            previous_context = (
                st.session_state.get(
                    "confirmed_usage_context"
                )
            )

            if (
                previous_context
                != selected_context
            ):
                clear_downstream_results()

            st.session_state[
                "confirmed_usage_context"
            ] = selected_context

            go_to_page(
                "upload"
            )