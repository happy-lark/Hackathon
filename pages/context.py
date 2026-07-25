"""
pages/context.py

사진을 사용할 목적을 선택하는 Usage Context 페이지입니다.

선택된 목적은 이후 사진 추천, 크롭,
배경 및 이미지 보정 기준에 사용됩니다.
"""

from textwrap import dedent

import streamlit as st

from utils.navigation import go_to_page


TOTAL_STEPS = 5
CURRENT_STEP = 2


CONTEXT_OPTIONS = [
    {
        "key": "professional_profile",
        "icon": "▣",
        "title": "Professional Profile",
        "description": (
            "LinkedIn, company profile, alumni page"
        ),
    },
    {
        "key": "portfolio",
        "icon": "▱",
        "title": "Portfolio / Personal Website",
        "description": (
            "Showcase your work and yourself"
        ),
    },
    {
        "key": "networking",
        "icon": "♧",
        "title": "Networking / Conference",
        "description": (
            "Events, meetups, speaker profile"
        ),
    },
    {
        "key": "creator",
        "icon": "◉",
        "title": "Creator / Personal Brand",
        "description": (
            "YouTube, blog, social media"
        ),
    },
    {
        "key": "other",
        "icon": "⌁",
        "title": "Other",
        "description": "Other purposes",
    },
]


CONTEXT_OPTION_MAP = {
    option["key"]: option
    for option in CONTEXT_OPTIONS
}


def clean_html(html_content):
    """
    HTML의 들여쓰기와 불필요한 줄바꿈을 제거합니다.

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

    radio_key = "context_usage_radio"

    if radio_key not in st.session_state:
        st.session_state[
            radio_key
        ] = saved_context

    elif (
        st.session_state[radio_key]
        not in valid_option_keys
    ):
        st.session_state[
            radio_key
        ] = saved_context


def format_context_option(option_key):
    """
    Radio 항목에 표시할 아이콘과 제목을 반환합니다.
    """

    option = CONTEXT_OPTION_MAP[
        option_key
    ]

    return (
        f'{option["icon"]}    '
        f'{option["title"]}'
    )


def get_context_captions():
    """
    각 Context 항목의 설명 목록을 반환합니다.
    """

    return [
        option["description"]
        for option in CONTEXT_OPTIONS
    ]


def show_progress_header():
    """
    Back 버튼과 상단 5단계 진행 상태를 표시합니다.
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
            key="context_back"
        ):
            go_to_page(
                "target"
            )

    with progress_column:
        render_html(
            """
            <div class="context-progress">
                <span class="context-progress-dot completed">
                    1
                </span>

                <span class="context-progress-line completed">
                </span>

                <span class="context-progress-dot active">
                    2
                </span>

                <span class="context-progress-line">
                </span>

                <span class="context-progress-dot">
                    3
                </span>

                <span class="context-progress-line">
                </span>

                <span class="context-progress-dot">
                    4
                </span>

                <span class="context-progress-line">
                </span>

                <span class="context-progress-dot">
                    5
                </span>
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


def show_context_options():
    """
    Usage Context 선택 카드를 표시하고
    선택된 Context 키를 반환합니다.
    """

    option_keys = [
        option["key"]
        for option in CONTEXT_OPTIONS
    ]

    selected_context = st.radio(
        "Usage context",
        options=option_keys,
        format_func=format_context_option,
        captions=get_context_captions(),
        label_visibility="collapsed",
        key="context_usage_radio"
    )

    st.session_state[
        "usage_context"
    ] = selected_context

    selected_option = CONTEXT_OPTION_MAP[
        selected_context
    ]

    st.session_state[
        "usage_context_details"
    ] = {
        "key": selected_option["key"],
        "title": selected_option["title"],
        "description": (
            selected_option[
                "description"
            ]
        )
    }

    return selected_context


def clear_downstream_results():
    """
    Usage Context가 변경된 후 기존 분석 결과가
    잘못 재사용되지 않도록 제거합니다.
    """

    keys_to_remove = [
        "analysis_result",
        "analysis_status",
        "analysis_error_result",
        "photo_ranking",
        "best_photo_index",
        "selected_photo_index",
        "best_match_score",
        "optimized_image",
        "original_match_score",
        "optimized_match_score",
        "improvement_summary",
        "improvement_report"
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
        [0.6, 5, 0.6]
    )

    with content_column:
        show_progress_header()
        show_page_header()

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