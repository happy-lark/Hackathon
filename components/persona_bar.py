"""
components/persona_bar.py

세 번째 이미지(MBTI 스타일)처럼 생긴 슬라이더 바를 렌더링합니다.
막대그래프 대신, 하나의 가로 바 위에 Target(목표)과 Detected(분석결과) 위치를
점으로 표시해서 한눈에 격차를 보여줍니다.
"""

import streamlit as st

# 각 축의 색상 (원하는 색으로 자유롭게 바꿔도 됩니다)
AXIS_COLORS = {
    "Warm": "#e07a5f",
    "Confident": "#f2cc8f",
    "Professional": "#81b29a",
    "Approachable": "#3d5a80",
}


def render_persona_bar(axis_name: str, target: float, detected: float):
    """
    axis_name: "Warm" 등
    target: 0~100
    detected: 0~100
    """
    color = AXIS_COLORS.get(axis_name, "#3d5a80")
    gap = round(detected - target, 1)
    gap_text = f"+{gap}" if gap > 0 else str(gap)

    st.markdown(
        f"""
        <div style="margin-bottom: 28px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                <span style="font-weight:600;">{axis_name}</span>
                <span style="color:#888;">Target {target}% · Detected {detected}%
                    <span style="color:{'#4caf50' if gap>=0 else '#e57373'};">({gap_text})</span>
                </span>
            </div>
            <div style="position:relative; height:10px; background:#2a2a2a; border-radius:5px;">
                <!-- 채워진 바: 0부터 detected 값까지 -->
                <div style="
                    position:absolute; left:0; top:0; height:10px;
                    width:{detected}%; background:{color}; border-radius:5px; opacity:0.55;">
                </div>
                <!-- Target 위치 마커 (흰색 세로선) -->
                <div style="
                    position:absolute; left:{target}%; top:-4px;
                    width:2px; height:18px; background:white;">
                </div>
                <!-- Detected 위치 마커 (동그라미) -->
                <div style="
                    position:absolute; left:{detected}%; top:-5px;
                    width:20px; height:20px; margin-left:-10px;
                    background:{color}; border:2px solid white; border-radius:50%;">
                </div>
            </div>
            <div style="display:flex; justify-content:space-between; margin-top:4px; font-size:11px; color:#666;">
                <span>0</span>
                <span>100</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_all_persona_bars(target_persona: dict, detected_persona: dict):
    """
    4개 축을 한번에 렌더링합니다.
    사용 예: render_all_persona_bars(target_persona, detected_persona)
    """
    for axis in ["Warm", "Confident", "Professional", "Approachable"]:
        render_persona_bar(axis, target_persona[axis], detected_persona[axis])