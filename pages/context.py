"""
pages/context.py

사진을 어디에 쓸지(Usage Context) 선택하는 페이지.
"모두에게 좋은 사진"이 아니라, "이 목적에 맞는 크롭/보정 수준"을 정하기 위한 선택입니다.
"""

import streamlit as st

from utils.navigation import go_to_page

TOTAL_STEPS = 5
CURRENT_STEP = 2

CONTEXT_OPTIONS = [
    {
        "key": "professional_profile",
        "icon": "💼",
        "title": "Professional Profile",
        "description": "LinkedIn, company profile, alumni page",
    },
    {
        "key": "portfolio",
        "icon": "🌐",
        "title": "Portfolio / Personal Website",
        "description": "Showcase your work and yourself",
    },
    {
        "key": "networking",
        "icon": "🤝",
        "title": "Networking / Conference",
        "description": "Events, meetups, speaker profile",
    },
    {
        "key": "creator",
        "icon": "🎨",
        "title": "Creator / Personal Brand",
        "description": "YouTube, blog, social media",
    },
    {
        "key": "resume",
        "icon": "📄",
        "title": "Resume",
        "description": "For applications where a photo is included",
    },
    {
        "key": "other",
        "icon": "✨",
        "title": "Other",
        "description": "Other purposes",
    },
]

CARD_CSS = """
<style>
div[data-testid="stRadio"] > div {
    gap: 10px;
}
div[data-testid="stRadio"] label[data-baseweb="radio"] {
    border: 1.5px solid #e5e5e5;
    border-radius: 12px;
    padding: 14px 16px;
    width: 100%;
    margin: 0 !important;
    transition: border-color 0.15s ease, background-color 0.15s ease;
}
div[data-testid="stRadio"] label[data-baseweb="radio"]:hover {
    border-color: #a78bfa;
}
div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {
    border-color: #7c3aed;
    background-color: #f5f3ff;
}
div[data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child {
    display: none;
}
</style>
"""


def _render_step_indicator():
    dots = []
    for step in range(1, TOTAL_STEPS + 1):
        if step == CURRENT_STEP:
            dots.append(f"**●{step}**")
        else:
            dots.append(f"○{step}")
    st.caption(" — ".join(dots))


def show_context_page():
    st.markdown(CARD_CSS, unsafe_allow_html=True)

    if st.button("← Back", key="context_back"):
        go_to_page("target")

    _render_step_indicator()

    st.markdown("### Step 2. Where will you use this photo?")
    st.caption("Choose the main context for your image.")
    st.caption(
        "이 선택은 '모두에게 좋은 사진'을 판단하기 위해서가 아니라, "
        "사용 목적에 맞는 크롭과 보정 수준을 결정하기 위해서입니다."
    )

    st.write("")

    if "usage_context" not in st.session_state:
        st.session_state["usage_context"] = CONTEXT_OPTIONS[0]["key"]

    option_labels = [
        f"{opt['icon']}  **{opt['title']}**  \n{opt['description']}"
        for opt in CONTEXT_OPTIONS
    ]
    option_keys = [opt["key"] for opt in CONTEXT_OPTIONS]

    current_index = option_keys.index(st.session_state["usage_context"])

    selected_label = st.radio(
        "Usage context",
        options=option_labels,
        index=current_index,
        label_visibility="collapsed",
    )

    selected_index = option_labels.index(selected_label)
    st.session_state["usage_context"] = option_keys[selected_index]

    st.write("")

    if st.button("Continue", type="primary", use_container_width=True):
        go_to_page("upload")