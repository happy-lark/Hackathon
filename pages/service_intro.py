"""
pages/service_intro.py

PersonaLab 서비스 소개 페이지입니다.
"""

import base64

from pathlib import Path
from textwrap import dedent

import streamlit as st

from utils.navigation import go_to_page


# =========================
# 프로젝트 경로
# =========================
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


# =========================
# HTML 유틸 함수
# =========================
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


def get_intro_logo_html():
    """
    PersonaLab 로고 이미지를 Base64 HTML로 변환합니다.

    이미지가 없으면 기존 P PersonaLab 로고를 대신 표시합니다.
    """

    if not LOGO_PATH.exists():
        return """
        <div class="intro-brand">
            <span class="intro-brand-icon">
                P
            </span>

            <span class="intro-brand-name">
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
    <div class="intro-brand">
        <img
            class="intro-brand-image"
            src="data:{mime_type};base64,{encoded_logo}"
            alt="PersonaLab"
        >
    </div>
    """


def show_service_intro_page():
    """
    PersonaLab 서비스 소개 페이지를 표시합니다.
    """

    # =========================
    # 상단 브랜드 로고
    # =========================
    render_html(
        get_intro_logo_html()
    )

    render_html(
        """
        <div class="intro-divider">
        </div>
        """
    )

    # =========================
    # 페이지 제목
    # =========================
    render_html(
        """
        <div class="intro-header">
            <div class="intro-title">
                AI Image Branding Coach
            </div>

            <div class="intro-description">
                <span>
                    PersonaLab helps you present your best self online.
                </span>

                <strong>
                    We don’t judge you.
                </strong>

                <span>
                    We help you show the image you want to present.
                </span>
            </div>
        </div>
        """
    )

    # =========================
    # DO / DON'T 비교
    # =========================
    dont_column, do_column = st.columns(
        2,
        gap="large"
    )

    with dont_column:
        render_html(
            """
            <div class="intro-compare-card intro-dont-card">
                <div class="intro-card-title intro-dont-title">
                    What We DON’T Do
                </div>

                <div class="intro-list">
                    <div class="intro-list-item">
                        <span class="intro-list-icon intro-x">
                            ×
                        </span>

                        <span>
                            Judge your personality
                        </span>
                    </div>

                    <div class="intro-list-item">
                        <span class="intro-list-icon intro-x">
                            ×
                        </span>

                        <span>
                            Rate your looks
                        </span>
                    </div>

                    <div class="intro-list-item">
                        <span class="intro-list-icon intro-x">
                            ×
                        </span>

                        <span>
                            Generate a new face
                        </span>
                    </div>

                    <div class="intro-list-item">
                        <span class="intro-list-icon intro-x">
                            ×
                        </span>

                        <span>
                            Over-edit your photo
                        </span>
                    </div>
                </div>
            </div>
            """
        )

    with do_column:
        render_html(
            """
            <div class="intro-compare-card intro-do-card">
                <div class="intro-card-title intro-do-title">
                    What We DO
                </div>

                <div class="intro-list">
                    <div class="intro-list-item">
                        <span class="intro-list-icon intro-check">
                            ✓
                        </span>

                        <span>
                            Analyze visual elements
                        </span>
                    </div>

                    <div class="intro-list-item">
                        <span class="intro-list-icon intro-check">
                            ✓
                        </span>

                        <span>
                            Match your photo with your goal
                        </span>
                    </div>

                    <div class="intro-list-item">
                        <span class="intro-list-icon intro-check">
                            ✓
                        </span>

                        <span>
                            Recommend the best photo
                        </span>
                    </div>

                    <div class="intro-list-item">
                        <span class="intro-list-icon intro-check">
                            ✓
                        </span>

                        <span>
                            Optimize your image naturally
                        </span>
                    </div>
                </div>
            </div>
            """
        )

    # =========================
    # 서비스 가치
    # =========================
    render_html(
        """
        <div class="intro-values-heading">
            Built on AI. Designed for You.
        </div>
        """
    )

    privacy_column, ai_column, real_column = st.columns(
        3,
        gap="large"
    )

    with privacy_column:
        render_html(
            """
            <div class="intro-value-item">
                <div class="intro-value-icon">
                    🛡️
                </div>

                <div class="intro-value-title">
                    Privacy First
                </div>

                <div class="intro-value-description">
                    Your photos stay secure.
                </div>
            </div>
            """
        )

    with ai_column:
        render_html(
            """
            <div class="intro-value-item">
                <div class="intro-value-icon">
                    ☀️
                </div>

                <div class="intro-value-title">
                    AI-Powered
                </div>

                <div class="intro-value-description">
                    Advanced image analysis.
                </div>
            </div>
            """
        )

    with real_column:
        render_html(
            """
            <div class="intro-value-item">
                <div class="intro-value-icon">
                    👤
                </div>

                <div class="intro-value-title">
                    Real You
                </div>

                <div class="intro-value-description">
                    We keep your image authentic.
                </div>
            </div>
            """
        )

    # =========================
    # 하단 버튼
    # =========================
    render_html(
        """
        <div class="intro-button-space">
        </div>
        """
    )

    back_column, empty_column, start_column = st.columns(
        [1, 0.4, 2]
    )

    with back_column:
        if st.button(
            "← Back",
            key="intro_back_button",
            use_container_width=True
        ):
            go_to_page(
                "landing"
            )

    with empty_column:
        st.empty()

    with start_column:
        if st.button(
            "Set My Goal →",
            key="intro_start_button",
            type="primary",
            use_container_width=True
        ):
            go_to_page(
                "target"
            )