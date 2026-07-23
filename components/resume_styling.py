"""
components/resume_styling.py

팀원의 analyze_personal_color() 결과(recommended_colors 리스트 하나)를
이력서용 "배경 추천 / 의상 추천"으로 나눠서 보여줍니다.
analysis/color_analyzer.py는 건드리지 않고, 그 결과를 가공만 합니다.
"""

# 각 시즌 색상 중 배경에 적합한 것과 의상에 적합한 것을 분류
# (팀원의 recommended_colors 리스트 순서에 맞춰 임의로 나눈 것 - 필요시 조정)
BACKGROUND_CANDIDATES = {
    "Coral", "Peach", "Ivory", "Warm Beige",
    "Terracotta", "Olive", "Mustard",
    "Lavender", "Sky Blue", "Cool Gray",
    "Pure White",
}


def split_resume_colors(personal_color: dict) -> dict:
    """
    personal_color: analyze_personal_color()의 반환값 (success=True인 경우)

    반환값: {"background": [...], "clothing": [...]}
    """
    colors = personal_color.get("recommended_colors", [])

    background = [c for c in colors if c in BACKGROUND_CANDIDATES]
    clothing = [c for c in colors if c not in BACKGROUND_CANDIDATES]

    # 혹시 한쪽이 비면, 전체 리스트를 그대로 보여줌 (안전장치)
    if not background:
        background = colors[:2]
    if not clothing:
        clothing = colors[-2:]

    return {"background": background, "clothing": clothing}