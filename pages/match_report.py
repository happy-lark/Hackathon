"""
pages/match_report.py

"8. Image Match Report" - 스크린샷 디자인을 반영한 결과 리포트 페이지.
Overall Match Score / Persona Alignment / Strengths / Areas to Improve / Color Recommendation
"""

import streamlit as st

from utils.navigation import go_to_page



PERSONA_AXES = ["Professional", "Confident", "Approachable", "Creative"]


def _match_label(score: float) -> tuple:
    """점수대별 한 줄 라벨과 격려 문구"""
    if score >= 85:
        return "Excellent Match", "Your photo aligns perfectly with your goal!"
    elif score >= 70:
        return "Good Match", "You're on the right track!"
    elif score >= 50:
        return "Fair Match", "A few tweaks could really help."
    else:
        return "Needs Work", "Let's find ways to get closer to your goal."


def _generate_strengths_and_improvements(features: dict, target_persona: dict, detected_persona: dict):
    """features/gap을 바탕으로 짧은 강점/개선점 문구 리스트를 만듭니다."""
    strengths = []
    improvements = []

    if features.get("Face Centering", 0) >= 70:
        strengths.append("Good facial visibility")
    if features.get("Smile", 0) >= 40:
        strengths.append("Natural expression")
    if features.get("Frontality", 0) >= 70 and features.get("Head Level", 0) >= 70:
        strengths.append("Professional appearance")
    if features.get("Face Centering", 0) >= 70 and features.get("Mouth Control", 0) >= 60:
        strengths.append("Clean composition")

    if features.get("Face Centering", 0) < 60:
        improvements.append("Background could be simpler")
    if features.get("Smile", 0) < 30 and features.get("Eye Openness", 0) < 60:
        improvements.append("Increase brightness slightly")

    for axis in PERSONA_AXES:
        if axis == "Creative":
            continue  # 위 features 기반으로 이미 커버
        gap = detected_persona.get(axis, 0) - target_persona.get(axis, 0)
        if gap < -10:
            improvements.append(f"Stronger {axis.lower()} presence needed")

    if features.get("Face Centering", 0) < 80:
        improvements.append("Tighter crop recommended")

    if not strengths:
        strengths.append("Solid overall composition")
    if not improvements:
        improvements.append("No major issues found")

    return strengths[:4], improvements[:4]


def show_match_report_page():
    if st.button("← Back", key="match_report_back"):
        go_to_page("result")

    st.markdown("## Your Image Match Report")
    st.caption("Based on your target persona and selected context.")
    st.write("")

    analysis_result = st.session_state.get("analysis_result")
    target_persona = st.session_state.get("target_persona")

    if not analysis_result or not target_persona:
        st.error("분석 결과를 찾을 수 없습니다. 사진을 다시 업로드해주세요.")
        if st.button("Return to Upload"):
            go_to_page("upload")
        return

    detected_persona = analysis_result["detected_persona"]
    features = analysis_result.get("features", {})


    # 전체 Match Score 계산
    gaps = [abs(detected_persona.get(a, 0) - target_persona.get(a, 0)) for a in ["Professional", "Confident", "Approachable", "Creative"]]
    match_score = round(max(0, 100 - (sum(gaps) / len(gaps))), 0)
    match_label, match_message = _match_label(match_score)

    score_col, alignment_col = st.columns(2)

    with score_col:
        with st.container(border=True):
            st.markdown("**Overall Match Score**")
            st.markdown(f"<div style='font-size:56px; font-weight:700; color:#7c3aed;'>{int(match_score)}%</div>", unsafe_allow_html=True)
            st.markdown(f"**{match_label}**")
            st.caption(match_message)

    with alignment_col:
        with st.container(border=True):
            st.markdown("**Persona Alignment**")
            st.write("")
            for axis in PERSONA_AXES:
                value = round(detected_persona.get(axis, 0), 0)
                st.markdown(
                    f"""
                    <div style="margin-bottom:14px;">
                        <div style="display:flex; justify-content:space-between; font-size:14px;">
                            <span>{axis}</span><span>{int(value)}%</span>
                        </div>
                        <div style="height:8px; background:#eee; border-radius:4px; margin-top:4px;">
                            <div style="width:{value}%; height:8px; background:#7c3aed; border-radius:4px;"></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.write("")

    strengths, improvements = _generate_strengths_and_improvements(features, target_persona, detected_persona)

    strengths_col, improvements_col = st.columns(2)

    with strengths_col:
        with st.container(border=True):
            st.markdown("**Strengths**")
            for item in strengths:
                st.markdown(f"✅ {item}")

    with improvements_col:
        with st.container(border=True):
            st.markdown("**Areas to Improve**")
            for item in improvements:
                if item == "No major issues found":
                    st.markdown(f"✅ {item}")
                else:
                    st.markdown(f"❌ {item}")
                    
    st.write("")
    
    st.markdown(
        """
        <div class="result-notice">
            이 결과는 사람의 실제 성격, 능력, 지능 또는 직업을
            판단한 것이 아닙니다. 사진에서 관찰되는 시각적 요소를
            바탕으로 계산한 목표 일치도 리포트입니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    color_recommendation = analysis_result.get("color_recommendation")

    if color_recommendation:
        with st.container(border=True):
            st.markdown("**Color Recommendation**")
            st.caption("These colors work well with your skin tone")

            swatch_html = "<div style='display:flex; gap:10px; margin-top:8px;'>"
            for hex_color in color_recommendation["colors"]:
                swatch_html += (
                    f"<div style='width:36px; height:36px; border-radius:8px; "
                    f"background:{hex_color}; border:1px solid #ddd;'></div>"
                )
            swatch_html += "</div>"
            st.markdown(swatch_html, unsafe_allow_html=True)

        st.write("")
        
    if st.button("Continue to Editing →", type="primary", use_container_width=True):
        go_to_page("photo_editor")

