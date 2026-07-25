import streamlit as st

from utils.navigation import go_to_page
from utils.logo import get_logo_html

def show_service_intro_page():
    # =========================
    # 상단 브랜드
    # =========================
    st.markdown(
        get_logo_html(
            css_class="intro-brand",
            image_class="intro-brand-image"
        ),
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="intro-divider"></div>',
        unsafe_allow_html=True
    )

    # =========================
    # 페이지 제목
    # =========================
    st.markdown(
        '<div class="intro-header">'
        '<div class="intro-title">AI Image Branding Coach</div>'
        '<div class="intro-description">'
        '<span>PersonaLab helps you present your best self online.</span>'
        '<strong>We don’t judge you.</strong>'
        '<span>We help you show the image you want to present.</span>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    # =========================
    # DO / DON'T 비교
    # =========================
    dont_column, do_column = st.columns(
        2,
        gap="large"
    )

    with dont_column:
        st.markdown(
            '<div class="intro-compare-card intro-dont-card">'
            '<div class="intro-card-title intro-dont-title">'
            'What We DON’T Do'
            '</div>'
            '<div class="intro-list">'
            '<div class="intro-list-item">'
            '<span class="intro-list-icon intro-x">×</span>'
            '<span>Judge your personality</span>'
            '</div>'
            '<div class="intro-list-item">'
            '<span class="intro-list-icon intro-x">×</span>'
            '<span>Rate your looks</span>'
            '</div>'
            '<div class="intro-list-item">'
            '<span class="intro-list-icon intro-x">×</span>'
            '<span>Generate a new face</span>'
            '</div>'
            '<div class="intro-list-item">'
            '<span class="intro-list-icon intro-x">×</span>'
            '<span>Over-edit your photo</span>'
            '</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

    with do_column:
        st.markdown(
            '<div class="intro-compare-card intro-do-card">'
            '<div class="intro-card-title intro-do-title">'
            'What We DO'
            '</div>'
            '<div class="intro-list">'
            '<div class="intro-list-item">'
            '<span class="intro-list-icon intro-check">✓</span>'
            '<span>Analyze visual elements</span>'
            '</div>'
            '<div class="intro-list-item">'
            '<span class="intro-list-icon intro-check">✓</span>'
            '<span>Match your photo with your goal</span>'
            '</div>'
            '<div class="intro-list-item">'
            '<span class="intro-list-icon intro-check">✓</span>'
            '<span>Recommend the best photo</span>'
            '</div>'
            '<div class="intro-list-item">'
            '<span class="intro-list-icon intro-check">✓</span>'
            '<span>Optimize your image naturally</span>'
            '</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

    # =========================
    # 서비스 가치
    # =========================
    st.markdown(
        '<div class="intro-values-heading">'
        'Built on AI. Designed for You.'
        '</div>',
        unsafe_allow_html=True
    )

    privacy_column, ai_column, real_column = st.columns(
        3,
        gap="large"
    )

    with privacy_column:
        st.markdown(
            '<div class="intro-value-item">'
            '<div class="intro-value-icon">🛡️</div>'
            '<div class="intro-value-title">Privacy First</div>'
            '<div class="intro-value-description">'
            'Your photos stay secure.'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

    with ai_column:
        st.markdown(
            '<div class="intro-value-item">'
            '<div class="intro-value-icon">☀️</div>'
            '<div class="intro-value-title">AI-Powered</div>'
            '<div class="intro-value-description">'
            'Advanced image analysis.'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

    with real_column:
        st.markdown(
            '<div class="intro-value-item">'
            '<div class="intro-value-icon">👤</div>'
            '<div class="intro-value-title">Real You</div>'
            '<div class="intro-value-description">'
            'We keep your image authentic.'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

    # =========================
    # 하단 버튼
    # =========================
    st.markdown(
        '<div class="intro-button-space"></div>',
        unsafe_allow_html=True
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