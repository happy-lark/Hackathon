"""
components/feedback_report.py

MBTI 진단서 스타일의 상세 피드백 리포트를 생성합니다.
축별 서술형 설명 + 강점/보완점 섹션 + 실전 팁으로 구성됩니다.
"""

# 각 축이 높을 때 / 낮을 때 어떤 인상을 주는지 서술형 설명
AXIS_NARRATIVE = {
    "Professional": {
        "high": "전문적이고 신뢰할 수 있는 인상이 잘 전달되고 있어요. "
                "격식 있는 구도와 절제된 표현이 균형 있게 어우러져 있어요.",
        "low": "전문성이 다소 약하게 느껴질 수 있어요. "
               "캐주얼한 톤이 과하면 진지한 자리(면접, 비즈니스 미팅)에서는 "
               "신뢰도를 낮게 볼 위험이 있어요.",
    },
    "Confident": {
        "high": "자신감 있는 태도가 사진과 글 전반에 잘 드러나고 있어요. "
                "정면을 응시하는 구도와 명확한 어조가 신뢰감을 더해줘요.",
        "low": "지금 프로필에서는 자신감이 다소 약하게 느껴져요. "
               "시선 처리나 자세, 문장의 확신도를 조금 더 분명하게 가져가면 좋아요.",
    },
    "Approachable": {
        "high": "친근하고 다가가기 쉬운 인상이 강하게 느껴져요. "
                "상대방이 말을 걸기 편안한 분위기를 만들고 있어요.",
        "low": "다가가기 조금 어려운 인상으로 비칠 수 있어요. "
               "표정이나 어조가 다소 딱딱하게 느껴질 가능성이 있어요.",
    },
    "Creative": {
        "high": "표현력 있고 생동감 있는 인상이 느껴져요. "
                "자유롭고 개성 있는 분위기가 잘 드러나고 있어요.",
        "low": "다소 정형화되고 무난한 인상으로 보여요. "
               "좀 더 자연스럽고 개성 있는 표현을 시도해볼 수 있어요.",
    },
}
 
# 상황(모드)별 실전 팁
MODE_TIPS = {
    "Job Interview": {
        "Professional": "정장 또는 단정한 복장, 깔끔한 배경의 사진을 사용하고, "
                        "소개글에서는 전문 용어나 직무 관련 키워드를 적절히 섞어보세요.",
        "Confident": "면접관 정면을 향한 구도와, 자기소개에서 구체적인 성과·경험을 "
                     "명확한 문장으로 서술하면 자신감이 더 잘 전달돼요.",
        "Approachable": "너무 딱딱해 보이지 않도록, 자기소개에 협업 경험이나 "
                        "팀워크 관련 문장을 한 줄 추가하면 균형이 좋아져요.",
        "Creative": "면접에서는 과한 개성보다, 절제된 선에서 본인만의 강점을 "
                    "드러내는 정도가 좋아요.",
    },
    "Networking": {
        "Professional": "너무 격식 차리기보다 '준비된 전문성'을 보여주는 정도가 적당해요.",
        "Confident": "관심 분야를 구체적으로 언급하면 자신감 있는 인상과 함께 "
                     "대화 시작점도 자연스럽게 만들어져요.",
        "Approachable": "질문을 유도하는 한 문장(예: '~에 관심 있으신 분 환영해요')을 "
                        "추가하면 접근성이 크게 올라가요.",
        "Creative": "본인만의 개성이 드러나는 표정이나 분위기를 자연스럽게 "
                    "보여줘도 좋아요.",
    },
    "First Date": {
        "Professional": "이 상황에서는 전문성보다 진솔함이 더 중요할 수 있어요.",
        "Confident": "과하지 않은 선에서 본인의 취향이나 관심사를 구체적으로 적으면 "
                     "자신감 있는 인상을 줄 수 있어요.",
        "Approachable": "짧은 유머나 질문형 문장을 넣으면 대화를 시작하기 쉬운 "
                        "인상을 줄 수 있어요.",
        "Creative": "자연스럽고 편안한 표현이 매력적으로 보일 수 있어요.",
    },
}


def generate_report_feedback(target_persona: dict, detected_persona: dict, mode: str = "Job Interview") -> dict:
    """
    MBTI 스타일 상세 리포트를 생성합니다.

    반환값:
    {
        "overview": "전체 요약 (2~3문장)",
        "sections": [
            {"axis": "Warm", "score": 27.3, "target": 25, "gap": 2.3,
             "narrative": "...", "tip": "..."},
            ...
        ],
        "strengths": ["Warm", "Approachable"],       # gap이 -3 이상인 축들
        "improvements": ["Professional"],             # gap이 -3 미만인 축들
        "closing": "면책 문구"
    }
    """
    mode_tips = MODE_TIPS.get(mode, MODE_TIPS["Job Interview"])

    sections = []
    strengths = []
    improvements = []

    for axis in ["Professional", "Confident", "Approachable", "Creative"]:
        score = detected_persona[axis]
        target = target_persona[axis]
        gap = round(score - target, 1)

        level = "high" if score >= target else "low"
        narrative = AXIS_NARRATIVE[axis][level]
        tip = mode_tips.get(axis, "")

        sections.append({
            "axis": axis,
            "score": score,
            "target": target,
            "gap": gap,
            "narrative": narrative,
            "tip": tip,
        })

        if gap >= -3:
            strengths.append(axis)
        else:
            improvements.append(axis)

    avg_abs_gap = sum(abs(s["gap"]) for s in sections) / len(sections)

    if avg_abs_gap < 5:
        overview = (
            f"현재 프로필은 '{mode}' 상황에서 목표한 인상과 전반적으로 잘 일치하고 있어요. "
            f"강점을 유지하면서 세부적인 부분만 다듬으면 충분히 좋은 인상을 전달할 수 있어요."
        )
    elif avg_abs_gap < 15:
        overview = (
            f"현재 프로필은 '{mode}' 상황에서 의도한 인상과 부분적으로 차이가 있어요. "
            f"아래 항목별 설명을 참고해서 몇 가지만 조정하면 목표에 훨씬 가까워질 수 있어요."
        )
    else:
        overview = (
            f"현재 프로필은 '{mode}' 상황에서 목표한 인상과 상당한 차이를 보이고 있어요. "
            f"사진과 소개글을 함께 재구성하는 것을 고려해보는 게 좋아요."
        )

    closing = (
        "※ 이 리포트는 사람의 실제 성격, 능력, 지능 또는 자격을 판단한 것이 아닙니다. "
        "사진과 글에서 관찰되는 시각적·언어적 신호를 바탕으로 계산된 인상 분석 결과이며, "
        "참고용 가이드로만 활용해주세요."
    )

    return {
        "overview": overview,
        "sections": sections,
        "strengths": strengths,
        "improvements": improvements,
        "closing": closing,
    }