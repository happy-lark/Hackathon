import streamlit as st

from utils.navigation import go_to_page


MODES = [
    "First Date",
    "Job Interview",
    "Networking"
]


MODE_DESCRIPTIONS = {
    "First Date": (
        "따뜻하고 편안한 첫인상을 확인합니다."
    ),
    "Job Interview": (
        "신뢰감 있고 전문적인 인상을 확인합니다."
    ),
    "Networking": (
        "자신감 있고 친근한 인상을 확인합니다."
    )
}


def show_mode_page():
    st.markdown(
        '<div class="step-text">STEP 1 OF 3</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-title">Choose Your Mode</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="page-description">
            어떤 상황에서 전달하고 싶은 인상인지 선택해주세요.
        </div>
        """,
        unsafe_allow_html=True
    )

    current_mode = st.session_state[
        "selected_mode"
    ]

    selected_index = MODES.index(
        current_mode
    )

    selected_mode = st.radio(
        "Mode",
        MODES,
        index=selected_index,
        label_visibility="collapsed"
    )

    st.session_state[
        "selected_mode"
    ] = selected_mode

    st.markdown(
        f"""
        <div class="info-card">
            <strong>{selected_mode}</strong><br>
            {MODE_DESCRIPTIONS[selected_mode]}
        </div>
        """,
        unsafe_allow_html=True
    )

    back_column, space, next_column = st.columns(
        [1, 2, 1]
    )

    with back_column:
        if st.button(
            "← Back",
            use_container_width=True
        ):
            go_to_page("service_intro")

    with next_column:
        if st.button(
            "Next →",
            type="primary",
            use_container_width=True
        ):
            go_to_page("target")