"""
components/full_report.py

기존 4대 축(Warm/Confident/Professional/Approachable) 리포트에
얼굴 세부 특징(features)과 컬러 프로필(color_features)을
"하위 항목"으로 추가한 풍부한 진단서를 만듭니다.

이미 analyzer.py, color_analyzer.py가 계산해둔 값을 재사용하므로
새로운 분석/API 호출이 필요 없습니다.
"""

# 얼굴 세부 특징에 대한 서술형 설명 (높을 때 / 낮을 때)
FEATURE_NARRATIVE = {
    "Smile": {
        "high": "자연스럽고 뚜렷한 미소가 담겨 있어요.",
        "low": "표정이 다소 무표정에 가까워요.",
    },
    "Eye Openness": {
        "high": "눈이 또렷하게 뜨여 있어 생기 있는 인상을 줘요.",
        "low": "눈이 약간 감기거나 졸린 듯한 인상을 줄 수 있어요.",
    },
    "Frontality": {
        "high": "얼굴이 카메라를 거의 정면으로 향하고 있어요.",
        "low": "얼굴이 살짝 옆으로 돌아가 있어요.",
    },
    "Head Level": {
        "high": "고개가 수평으로 잘 맞춰져 있어요.",
        "low": "고개가 한쪽으로 살짝 기울어져 있어요.",
    },
    "Mouth Control": {
        "high": "입매가 안정적으로 다물어져 있어요.",
        "low": "입이 다소 벌어진 상태로 보여요.",
    },
    "Face Centering": {
        "high": "얼굴이 사진 중앙에 잘 위치해 있어요.",
        "low": "얼굴이 사진 중앙에서 약간 벗어나 있어요.",
    },
}

COLOR_FEATURE_NARRATIVE = {
    "Warmth": "피부톤의 웜/쿨 정도를 나타내요. 값이 높을수록 따뜻한(웜) 톤에 가까워요.",
    "Saturation": "색의 선명도예요. 값이 높을수록 컬러가 또렷하고 생동감 있게 보여요.",
    "Brightness": "피부의 명도예요. 값이 높을수록 밝은 톤, 낮을수록 깊은 톤이에요.",
}


def _feature_blurb(name: str, value: float) -> str:
    narrative = FEATURE_NARRATIVE.get(name)
    if not narrative:
        return ""
    return narrative["high"] if value >= 60 else narrative["low"]


def generate_full_report(
    target_persona: dict,
    detected_persona: dict,
    features: dict,
    personal_color: dict | None,
    mode: str,
) -> dict:
    """
    반환값:
    {
        "core_axes": [...],           # 기존 4대 축 (Warm/Confident/Professional/Approachable)
        "sub_features": [...],        # 얼굴 세부 특징 6개
        "color_profile": [...],       # 컬러 하위 항목 (Warmth/Saturation/Brightness)
        "background_note": str | None,
    }
    """
    # 1. 핵심 4대 축 (기존 로직 재사용 가능한 형태로)
    core_axes = []
    for axis in ["Warm", "Confident", "Professional", "Approachable"]:
        score = detected_persona[axis]
        target = target_persona[axis]
        gap = round(score - target, 1)
        core_axes.append({"axis": axis, "score": score, "target": target, "gap": gap})

    # 2. 얼굴 세부 특징 (하위 항목)
    sub_features = []
    for name, value in features.items():
        sub_features.append({
            "name": name,
            "value": value,
            "blurb": _feature_blurb(name, value),
        })

    # 3. 컬러 프로필 (퍼스널컬러 분석이 성공했을 때만)
    color_profile = []
    if personal_color and personal_color.get("success"):
        color_features = personal_color.get("color_features", {})
        for key in ["Warmth", "Saturation", "Brightness"]:
            if key in color_features:
                color_profile.append({
                    "name": key,
                    "value": color_features[key],
                    "blurb": COLOR_FEATURE_NARRATIVE.get(key, ""),
                })

    return {
        "core_axes": core_axes,
        "sub_features": sub_features,
        "color_profile": color_profile,
    }