"""
components/feedback.py

지금은 가장 격차 큰 축 하나만 언급하는 짧은 피드백인데,
이걸 축별로 다 짚어주는 상세 피드백으로 확장합니다.
"""

# 축별로 "낮을 때 어떻게 하면 좋은지" 제안 문구
IMPROVEMENT_TIPS = {
    "Warm": "입꼬리를 조금 더 올리고 자연스럽게 미소 지어보세요.",
    "Confident": "정면을 응시하고 고개를 살짝 들어올린 사진을 사용해보세요.",
    "Professional": "고개를 수평으로 맞추고, 입을 편안하게 다문 표정을 시도해보세요.",
    "Approachable": "밝은 표정과 정면 구도를 함께 사용하면 도움이 됩니다.",
}


def generate_detailed_feedback(target_persona: dict, detected_persona: dict) -> dict:
    """
    target_persona, detected_persona: {"Warm": .., "Confident": .., ...} (합 100%)

    반환값:
    {
        "summary": "전체 요약 한 줄",
        "axis_feedback": ["Warm: ...", "Confident: ...", ...],  # 격차 큰 순으로 정렬
        "top_tip": "가장 시급한 개선 제안 한 줄"
    }
    """
    gaps = {
        axis: round(detected_persona[axis] - target_persona[axis], 1)
        for axis in target_persona
    }

    # 격차가 큰 순서대로 정렬 (절댓값 기준)
    sorted_axes = sorted(gaps.items(), key=lambda x: abs(x[1]), reverse=True)

    axis_feedback = []
    for axis, gap in sorted_axes:
        if abs(gap) < 3:
            axis_feedback.append(f"**{axis}**: 목표와 거의 일치해요 (차이 {gap:+.1f}%p).")
        elif gap < 0:
            axis_feedback.append(
                f"**{axis}**: 목표보다 {abs(gap):.1f}%p 낮아요. {IMPROVEMENT_TIPS.get(axis, '')}"
            )
        else:
            axis_feedback.append(
                f"**{axis}**: 목표보다 {gap:.1f}%p 높아요. 의도한 것보다 강하게 전달되고 있어요."
            )

    # 전체 요약 (평균 절대 격차 기준)
    avg_gap = sum(abs(g) for g in gaps.values()) / len(gaps)
    if avg_gap < 5:
        summary = "전반적으로 의도한 인상과 실제 사진이 잘 일치하고 있어요."
    elif avg_gap < 15:
        summary = "전반적으로는 비슷하지만, 몇몇 축에서 목표와 차이가 있어요."
    else:
        summary = "의도한 인상과 실제 전달되는 인상 사이에 꽤 큰 차이가 있어요."

    weakest_axis, weakest_gap = sorted_axes[0]
    top_tip = (
        f"가장 먼저 신경 쓰면 좋은 부분은 **{weakest_axis}**예요. "
        f"{IMPROVEMENT_TIPS.get(weakest_axis, '')}"
    )

    return {
        "summary": summary,
        "axis_feedback": axis_feedback,
        "top_tip": top_tip,
    }