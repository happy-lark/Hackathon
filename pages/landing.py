"""
pages/landing.py

PersonaLab 랜딩 페이지입니다.
"""

import base64

from pathlib import Path
from textwrap import dedent

import streamlit as st

from utils.navigation import go_to_page


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)


LOGO_PATH = (
    PROJECT_ROOT
    / "assets"
    / "Logo_cropped.png"
)


MASCOT_PATH = (
    PROJECT_ROOT
    / "assets"
    / "persona_mascot.png"
)


def clean_html(html_content):
    """
    Streamlit이 들여쓰기된 HTML을 코드 블록으로
    인식하지 않도록 줄바꿈과 들여쓰기를 정리합니다.
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
    정리된 HTML을 Streamlit 화면에 렌더링합니다.
    """

    st.markdown(
        clean_html(
            html_content
        ),
        unsafe_allow_html=True
    )


def get_image_mime_type(image_path):
    """
    이미지 확장자에 맞는 MIME type을 반환합니다.
    """

    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp"
    }

    return mime_types.get(
        image_path.suffix.lower(),
        "image/png"
    )


def get_logo_html():
    """
    로고 이미지를 Base64 HTML 이미지로 변환합니다.

    st.image가 아니라 HTML img로 출력하여
    로고 크기와 정렬을 CSS에서 정확히 제어합니다.
    """

    if not LOGO_PATH.exists():
        return """
        <div class="landing-logo-fallback">
            <span class="landing-logo-fallback-icon">
                P
            </span>

            <span>
                PersonaLab
            </span>
        </div>
        """

    encoded_logo = base64.b64encode(
        LOGO_PATH.read_bytes()
    ).decode(
        "utf-8"
    )

    mime_type = get_image_mime_type(
        LOGO_PATH
    )

    return f"""
    <div class="landing-logo">
        <img
            class="landing-logo-image"
            src="data:{mime_type};base64,{encoded_logo}"
            alt="PersonaLab"
        >
    </div>
    """


def show_top_navigation():
    """
    상단 로고와 내비게이션 메뉴를 표시합니다.
    """

    (
        logo_col,
        home_col,
        how_col,
        feature_col,
        start_col
    ) = st.columns(
        [
            2.3,
            0.8,
            1.2,
            1.0,
            1.3
        ],
        vertical_alignment="center"
    )

    with logo_col:
        render_html(
            get_logo_html()
        )

    with home_col:
        render_html(
            """
            <div class="landing-nav-item">
                Home
            </div>
            """
        )

    with how_col:
        render_html(
            """
            <div class="landing-nav-item">
                How It Works
            </div>
            """
        )

    with feature_col:
        render_html(
            """
            <div class="landing-nav-item">
                Features
            </div>
            """
        )

    with start_col:
        if st.button(
            "Get Started",
            key="landing_top_start",
            type="primary",
            use_container_width=True
        ):
            go_to_page(
                "service_intro"
            )

    render_html(
        """
        <div class="landing-nav-divider">
        </div>
        """
    )


def show_hero_section():
    """
    랜딩 페이지의 Hero 영역을 표시합니다.
    """

    text_col, image_col = st.columns(
        [1, 1.65],
        gap="large",
        vertical_alignment="center"
    )

    with text_col:
        render_html(
            """
            <div class="landing-hero-title">
                Show the image<br>
                you want to present.
            </div>
            """
        )

        render_html(
            """
            <div class="landing-hero-description">
                AI analyzes your photos and finds the one
                that best matches your desired persona.
            </div>
            """
        )

        button_col, empty_col = st.columns(
            [1.45, 0.55]
        )

        with button_col:
            if st.button(
                "Start My Image Analysis",
                key="landing_main_start",
                type="primary",
                use_container_width=True
            ):
                go_to_page(
                    "service_intro"
                )

        with empty_col:
            st.empty()

        render_html(
            """
            <div class="landing-trust-row">
                <span class="landing-stars">
                    ★★★★★
                </span>

                <span class="landing-trust-text">
                    Designed for better first impressions
                </span>
            </div>
            """
        )

    with image_col:
        if MASCOT_PATH.exists():
            st.image(
                str(
                    MASCOT_PATH
                ),
                use_container_width=True
            )

        else:
            render_html(
                """
                <div class="landing-mascot-placeholder">
                    <div class="mascot-emoji">
                        🤖
                    </div>

                    <div>
                        Add persona_mascot.png<br>
                        to the assets folder
                    </div>
                </div>
                """
            )


def show_feature_cards():
    """
    하단 기능 소개 카드 3개를 표시합니다.
    """

    render_html(
        """
        <div class="landing-feature-space">
        </div>
        """
    )

    goal_col, upload_col, report_col = st.columns(
        3,
        gap="large"
    )

    with goal_col:
        render_html(
            """
            <div class="landing-feature-card">
                <div class="landing-feature-icon">
                    🎯
                </div>

                <div class="landing-feature-title">
                    Set Your Goal
                </div>

                <div class="landing-feature-description">
                    Choose how you want<br>
                    to be perceived.
                </div>
            </div>
            """
        )

    with upload_col:
        render_html(
            """
            <div class="landing-feature-card">
                <div class="landing-feature-icon">
                    📷
                </div>

                <div class="landing-feature-title">
                    Upload Photos
                </div>

                <div class="landing-feature-description">
                    Add up to 5 photos<br>
                    of yourself.
                </div>
            </div>
            """
        )

    with report_col:
        render_html(
            """
            <div class="landing-feature-card">
                <div class="landing-feature-icon">
                    📈
                </div>

                <div class="landing-feature-title">
                    Get Your Report
                </div>

                <div class="landing-feature-description">
                    AI analyzes and recommends<br>
                    your best match.
                </div>
            </div>
            """
        )


def show_landing_page():
    """
    PersonaLab 랜딩 페이지를 표시합니다.
    """

    show_top_navigation()
    show_hero_section()
    show_feature_cards()