import streamlit as st

from utils.navigation import go_to_page


def show_service_intro_page():
    st.markdown(
        """
        <div style="
            text-align: center;
            padding-top: 25px;
            padding-bottom: 20px;
        ">
            <h1>✨ Meet PersonaLab</h1>
            <p style="
                font-size: 18px;
                color: #666666;
                line-height: 1.7;
            ">
                PersonaLab analyzes the impression conveyed by your photo
                and helps you create an image that better matches
                your intended persona.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.subheader(
        "How PersonaLab Works"
    )

    step1, step2, step3 = st.columns(3)

    with step1:
        st.markdown(
            """
            <div style="
                padding: 22px;
                min-height: 210px;
                border: 1px solid #E5E5E5;
                border-radius: 16px;
                text-align: center;
            ">
                <div style="font-size: 40px;">🎯</div>
                <h3>1. Choose Your Goal</h3>
                <p style="color: #666666;">
                    Select the situation and define
                    the impression you want to convey.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with step2:
        st.markdown(
            """
            <div style="
                padding: 22px;
                min-height: 210px;
                border: 1px solid #E5E5E5;
                border-radius: 16px;
                text-align: center;
            ">
                <div style="font-size: 40px;">📷</div>
                <h3>2. Upload Photos</h3>
                <p style="color: #666666;">
                    Upload one or more photos
                    showing your facial expression and style.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with step3:
        st.markdown(
            """
            <div style="
                padding: 22px;
                min-height: 210px;
                border: 1px solid #E5E5E5;
                border-radius: 16px;
                text-align: center;
            ">
                <div style="font-size: 40px;">✨</div>
                <h3>3. Analyze & Improve</h3>
                <p style="color: #666666;">
                    Compare your detected persona with your target
                    and receive personalized suggestions.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    st.subheader(
        "Available Features"
    )

    feature1, feature2 = st.columns(2)

    with feature1:
        st.markdown(
            """
            ### 🧠 Persona Analysis

            Analyze impressions such as:

            - Trustworthy
            - Confident
            - Professional
            - Approachable
            """
        )

    with feature2:
        st.markdown(
            """
            ### 🎨 Photo Enhancement

            Improve your photos with:

            - Personal color analysis
            - Background color replacement
            - Forest, ocean, and nature backgrounds
            - Custom background uploads
            """
        )

    st.info(
        "PersonaLab provides AI-based visual feedback. "
        "Results may vary depending on lighting, facial angle, "
        "photo quality, and background."
    )

    st.write("")

    back_column, start_column = st.columns(
        [1, 2]
    )

    with back_column:
        if st.button(
            "← Back",
            use_container_width=True
        ):
            go_to_page(
                "landing"
            )

    with start_column:
        if st.button(
            "Get Started →",
            type="primary",
            use_container_width=True
        ):
            go_to_page(
                "mode"
            )