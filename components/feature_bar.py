"""
components/feature_bar.py

Target 없이 단일 값(0~100)만 보여주는 슬라이더 바입니다.
Facial Feature Analysis (Smile, Eye Openness, Frontality 등)처럼
"목표"가 없는 순수 측정값을 보여줄 때 씁니다.
"""

import streamlit as st

FEATURE_COLORS = {
    "Smile": "#e07a5f",
    "Eye Openness": "#f2cc8f",
    "Frontality": "#81b29a",
    "Head Level": "#3d5a80",
    "Mouth Control": "#9b5de5",
    "Face Centering": "#00bbf9",
}


def render_feature_bar(feature_name: str, value: float):
    """
    feature_name: "Smile" 등
    value: 0~100
    """
    color = FEATURE_COLORS.get(feature_name, "#3d5a80")

    st.markdown(
        f"""
        <div style="margin-bottom: 22px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                <span style="font-weight:600;">{feature_name}</span>
                <span style="color:#888;">{value}%</span>
            </div>
            <div style="position:relative; height:10px; background:#2a2a2a; border-radius:5px;">
                <div style="
                    position:absolute; left:0; top:0; height:10px;
                    width:{value}%; background:{color}; border-radius:5px;">
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_all_feature_bars(features: dict):
    """
    features: {"Smile": 3.1, "Eye Openness": 90.4, ...}
    딕셔너리 순서 그대로 렌더링합니다.
    """
    for name, value in features.items():
        render_feature_bar(name, value)