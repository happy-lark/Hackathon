import pandas as pd
import streamlit as st

from utils.navigation import (
    go_to_page,
    reset_all
)

from components.persona_bar import render_all_persona_bars
from components.feedback import generate_detailed_feedback
from components.feature_bar import render_all_feature_bars
from components.resume_styling import split_resume_colors
from components.full_report import generate_full_report

def calculate_match_score(
    comparison_dataframe
):
    """
    Target과 Detected의 평균 절대 차이를 기반으로
    Match Score를 계산합니다.
    """

    average_difference = (
        comparison_dataframe["Difference"]
        .abs()
        .mean()
    )

    return round(
        max(
            0,
            100 - average_difference
        ),
        1
    )


def generate_feedback(comparison_dataframe):
    """
    Target Persona와 Detected Persona의 차이를 바탕으로
    간단한 피드백을 생성합니다.
    """

    largest_gap_row = comparison_dataframe.iloc[
        comparison_dataframe["Difference"]
        .abs()
        .argmax()
    ]

    persona = largest_gap_row["Persona"]
    difference = largest_gap_row["Difference"]

    if abs(difference) < 5:
        return (
            "목표 Persona와 실제 사진의 인상이 "
            "전반적으로 잘 일치합니다."
        )

    if difference < 0:
        feedback_by_persona = {
            "Warm": (
                "목표보다 따뜻한 인상이 낮습니다. "
                "입꼬리를 조금 더 올리고 자연스럽게 "
                "미소 지어보세요."
            ),
            "Confident": (
                "목표보다 자신감 있는 인상이 낮습니다. "
                "얼굴을 카메라 정면으로 향하고 "
                "고개를 수평으로 유지해보세요."
            ),
            "Professional": (
                "목표보다 전문적인 인상이 낮습니다. "
                "얼굴을 중앙에 두고 입을 자연스럽게 "
                "다문 사진을 사용해보세요."
            ),
            "Approachable": (
                "목표보다 친근한 인상이 낮습니다. "
                "눈을 자연스럽게 뜨고 부드러운 미소를 "
                "지어보세요."
            )
        }

        return feedback_by_persona[persona]

    feedback_by_persona = {
        "Warm": (
            "사진의 따뜻한 인상이 목표보다 강합니다. "
            "조금 더 차분한 표정을 사용하면 "
            "목표 비율에 가까워질 수 있습니다."
        ),
        "Confident": (
            "사진의 자신감 있는 인상이 목표보다 강합니다. "
            "시선과 자세를 조금 더 부드럽게 조절해보세요."
        ),
        "Professional": (
            "사진의 전문적인 인상이 목표보다 강합니다. "
            "조금 더 자연스러운 미소를 추가해보세요."
        ),
        "Approachable": (
            "사진의 친근한 인상이 목표보다 강합니다. "
            "조금 더 차분하고 절제된 표정을 사용해보세요."
        )
    }

    return feedback_by_persona[persona]


def show_result_page():
    if "analysis_result" not in st.session_state:
        st.error(
            "분석 결과를 찾을 수 없습니다. "
            "사진을 다시 업로드해주세요."
        )

        if st.button(
            "Return to Upload",
            use_container_width=True
        ):
            go_to_page("upload")

        return

    analysis_result = st.session_state[
        "analysis_result"
    ]

    features = analysis_result[
        "features"
    ]

    detected_persona = analysis_result[
        "detected_persona"
    ]

    target_persona = st.session_state[
        "target_persona"
    ]

    selected_mode = st.session_state[
        "selected_mode"
    ]

    st.markdown(
        """
        <div class="page-title">
            Your Persona Analysis ✨
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="page-description">
            Selected Mode: {selected_mode}
        </div>
        """,
        unsafe_allow_html=True
    )

    if "uploaded_image" in st.session_state:
        st.image(
            st.session_state[
                "uploaded_image"
            ],
            caption="Analyzed Photo",
            use_container_width=True
        )

    st.divider()

    # 얼굴 특징 분석
    st.subheader(
        "🔍 Facial Feature Analysis"
    )

    render_all_feature_bars(features)

    st.caption(
        "미소, 눈 개방도, 얼굴 정면도, "
        "고개 수평도, 입의 안정성 및 "
        "사진 속 얼굴 위치를 측정한 결과입니다."
    )

    st.divider()

    # Detected Persona
    st.subheader(
        "🧑 Detected Persona"
    )

    column1, column2, column3, column4 = st.columns(
        4
    )

    column1.metric(
        "Warm",
        f"{detected_persona['Warm']}%"
    )

    column2.metric(
        "Confident",
        f"{detected_persona['Confident']}%"
    )

    column3.metric(
        "Professional",
        f"{detected_persona['Professional']}%"
    )

    column4.metric(
        "Approachable",
        f"{detected_persona['Approachable']}%"
    )

    detected_dataframe = pd.DataFrame(
        {
            "Persona": list(
                detected_persona.keys()
            ),
            "Score": list(
                detected_persona.values()
            )
        }
    )

    st.bar_chart(
        detected_dataframe.set_index(
            "Persona"
        )
    )

    st.divider()

    # Target vs Detected
    st.subheader(
        "🎯 Target vs Detected"
    )

    comparison_rows = []

    for persona_name in target_persona:
        target_score = target_persona[
            persona_name
        ]

        detected_score = detected_persona[
            persona_name
        ]

        difference = round(
            detected_score - target_score,
            1
        )

        comparison_rows.append(
            {
                "Persona": persona_name,
                "Target": target_score,
                "Detected": detected_score,
                "Difference": difference
            }
        )

    comparison_dataframe = pd.DataFrame(
        comparison_rows
    )

    st.dataframe(
        comparison_dataframe,
        use_container_width=True,
        hide_index=True
    )

    comparison_chart = (
        comparison_dataframe
        .set_index("Persona")[
            ["Target", "Detected"]
        ]
    )

    st.bar_chart(
        comparison_chart
    )
    
    render_all_persona_bars(target_persona, detected_persona)

    match_score = calculate_match_score(
        comparison_dataframe
    )

    st.metric(
        "Persona Match Score",
        f"{match_score}%"
    )

    from components.feedback_report import generate_report_feedback

    report = generate_report_feedback(target_persona, detected_persona, selected_mode)

    st.subheader("📋 Persona Diagnostic Report")
    st.write(report["overview"])
    st.write("")

    for section in report["sections"]:
        gap_text = f"+{section['gap']}" if section['gap'] >= 0 else str(section['gap'])
        st.markdown(f"### {section['axis']} — {section['score']}% (Target {section['target']}%, {gap_text})")
        st.write(section["narrative"])
        st.markdown(f"💡 **Tip**: {section['tip']}")
        st.write("")

    if report["strengths"]:
        st.success(f"✅ 강점: {', '.join(report['strengths'])}")
    if report["improvements"]:
        st.warning(f"🔧 보완하면 좋은 부분: {', '.join(report['improvements'])}")

    st.caption(report["closing"])
    
    personal_color = analysis_result.get("personal_color")

    if personal_color:
        st.divider()
        st.subheader("🎨 Personal Color & Resume Styling")
        st.write(f"**{personal_color['season']}** (Confidence {personal_color['confidence']}%)")
        st.write(personal_color["description"])

        st.markdown("**추천 색상**")
        for color in personal_color["recommended_colors"]:
            st.markdown(f"- {color}")
            
        from components.full_report import generate_full_report

    full_report = generate_full_report(
        target_persona, detected_persona, features, personal_color, selected_mode
    )

    st.divider()
    st.subheader("📋 세부 특징 분석")

    st.markdown("#### 표정/구도 특징")
    for feat in full_report["sub_features"]:
        st.write(f"- **{feat['name']}** ({feat['value']}) — {feat['blurb']}")

    if full_report["color_profile"]:
        st.markdown("#### 컬러 프로필")
        for c in full_report["color_profile"]:
            st.write(f"- **{c['name']}** ({c['value']}) — {c['blurb']}")

    st.markdown(
        """
        <div class="result-notice">
            이 결과는 사람의 실제 성격, 능력, 지능 또는 직업을
            판단한 것이 아닙니다. 사진에서 관찰되는 미소, 눈의
            개방도, 얼굴 방향과 위치를 바탕으로 계산한 시각적
            인상 분석 결과입니다.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    back_column, space, restart_column = st.columns(
        [1, 2, 1]
    )

    with back_column:
        if st.button(
            "← Back",
            use_container_width=True
        ):
            go_to_page("upload")

    with restart_column:
        if st.button(
            "Start Again",
            type="primary",
            use_container_width=True
        ):
            reset_all()