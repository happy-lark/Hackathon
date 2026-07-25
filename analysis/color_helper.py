"""
analysis/color_helper.py

"퍼스널컬러 확정 진단"이 아니라, 이 사진의 피부톤을 가볍게 샘플링해서
어울리는 색상 몇 개만 추천하는 가벼운 버전입니다.
(예전에 삭제한 color_analyzer.py의 시즌 분류 시스템과는 다름 — 계절 이름 안 붙임)
"""

import numpy as np
from PIL import Image

from analysis.analyzer import create_face_landmarker

# 웜톤 쪽에 어울리는 무난한 팔레트
WARM_PALETTE = ["#C19A6B", "#8B5E3C", "#E8DCC4", "#A9744F", "#D9C7A3", "#6E5849"]

# 쿨톤 쪽에 어울리는 무난한 팔레트 (스크린샷과 유사)
COOL_PALETTE = ["#5B6EE1", "#2E3A59", "#8C9298", "#D9D9D9", "#EFE7DA", "#8A7A63"]


def suggest_colors_for_photo(image: Image.Image) -> dict:
    """
    사진 속 얼굴 볼 영역 색상을 가볍게 샘플링해서,
    웜/쿨 중 더 가까운 팔레트를 추천합니다.
    진단이 아니라 참고용 추천이라는 점을 명확히 합니다.
    """
    try:
        import mediapipe as mp

        image_array = np.ascontiguousarray(np.array(image.convert("RGB"), dtype=np.uint8))
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_array)

        landmarker = create_face_landmarker()
        result = landmarker.detect(mp_image)

        if not result.face_landmarks:
            return {"success": False}

        landmarks = result.face_landmarks[0]
        height, width = image_array.shape[:2]

        # 왼쪽 볼(33 근처), 오른쪽 볼(263 근처) 대략 샘플링
        sample_points = [landmarks[50], landmarks[280]]
        colors = []
        for point in sample_points:
            x = int(point.x * width)
            y = int(point.y * height)
            x1, x2 = max(0, x - 5), min(width, x + 5)
            y1, y2 = max(0, y - 5), min(height, y + 5)
            patch = image_array[y1:y2, x1:x2]
            if patch.size > 0:
                colors.append(patch.reshape(-1, 3).mean(axis=0))

        if not colors:
            return {"success": False}

        avg_color = np.mean(colors, axis=0)
        r, g, b = avg_color

        is_warm = (r - b) > 0

        palette = WARM_PALETTE if is_warm else COOL_PALETTE

        return {
            "success": True,
            "colors": palette,
            "note": "이 사진의 피부톤을 기준으로 가볍게 추천된 색상이에요. 확정 진단이 아닙니다.",
        }

    except Exception:
        return {"success": False}