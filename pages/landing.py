from pathlib import Path

import streamlit as st

from utils.navigation import go_to_page


MASCOT_PATH = Path("assets/persona_mascot.png")


def show_landing_page():
    # 상단 메뉴
    logo_col, home_col, how_col, feature_col, start_col = st.columns(
        [2.3, 0.8, 1.2, 1.0, 1.3],
        vertical_alignment="center"
    )

    with logo_col:
        st.markdown(
            '<div class="landing-logo"><span class="landing-logo-icon">P</span><span>PersonaLab</span></div>',
            unsafe_allow_html=True
        )

    with home_col:
        st.markdown(
            '<div class="landing-nav-item">Home</div>',
            unsafe_allow_html=True
        )

    with how_col:
        st.markdown(
            '<div class="landing-nav-item">How It Works</div>',
            unsafe_allow_html=True
        )

    with feature_col:
        st.markdown(
            '<div class="landing-nav-item">Features</div>',
            unsafe_allow_html=True
        )

    with start_col:
        if st.button(
            "Get Started",
            key="landing_top_start",
            type="primary",
            use_container_width=True
        ):
            go_to_page("service_intro")

    st.markdown(
        '<div class="landing-nav-divider"></div>',
        unsafe_allow_html=True
    )

    # 메인 영역
    text_col, image_col = st.columns(
    [1, 2],
    gap="medium",
    vertical_alignment="center"
)

    with text_col:
        st.markdown(
            '<div class="landing-hero-title">Show the image<br>you want to present.</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="landing-hero-description">AI analyzes your photos and finds the one that best matches your desired persona.</div>',
            unsafe_allow_html=True
        )

        button_col, empty_col = st.columns(
            [1.35, 0.65]
        )

        with button_col:
            if st.button(
                "Start My Image Analysis",
                key="landing_main_start",
                type="primary",
                use_container_width=True
            ):
                go_to_page("service_intro")

        st.markdown(
            '<div class="landing-trust-row"><span class="landing-stars">★★★★★</span><span class="landing-trust-text">Designed for better first impressions</span></div>',
            unsafe_allow_html=True
        )

    with image_col:
        if MASCOT_PATH.exists():
            st.image(
                str(MASCOT_PATH),
                use_container_width=True
            )
        else:
            st.markdown(
                '<div class="landing-mascot-placeholder"><div class="mascot-emoji">🤖</div><div>Add persona_mascot.png<br>to the assets folder</div></div>',
                unsafe_allow_html=True
            )

    # 하단 기능 설명
    st.markdown(
        '<div class="landing-feature-space"></div>',
        unsafe_allow_html=True
    )

    goal_col, upload_col, report_col = st.columns(
        3,
        gap="large"
    )

    with goal_col:
        st.markdown(
            '<div class="landing-feature-card"><div class="landing-feature-icon">🎯</div><div class="landing-feature-title">Set Your Goal</div><div class="landing-feature-description">Choose how you want<br>to be perceived.</div></div>',
            unsafe_allow_html=True
        )

    with upload_col:
        st.markdown(
            '<div class="landing-feature-card"><div class="landing-feature-icon">📷</div><div class="landing-feature-title">Upload Photos</div><div class="landing-feature-description">Add up to 5 photos<br>of yourself.</div></div>',
            unsafe_allow_html=True
        )

    with report_col:
        st.markdown(
            '<div class="landing-feature-card"><div class="landing-feature-icon">📈</div><div class="landing-feature-title">Get Your Report</div><div class="landing-feature-description">AI analyzes and recommends<br>your best match.</div></div>',
            unsafe_allow_html=True
        )