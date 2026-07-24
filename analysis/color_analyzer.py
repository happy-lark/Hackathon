import colorsys

import mediapipe as mp
import numpy as np
from PIL import Image

from analysis.analyzer import (
    check_face_size,
    clamp,
    create_face_landmarker
)


def get_face_bounds(landmarks, width, height):
    """
    얼굴 랜드마크를 기준으로 얼굴 영역의 좌표를 구합니다.
    """
    x_values = [
        landmark.x * width
        for landmark in landmarks
    ]

    y_values = [
        landmark.y * height
        for landmark in landmarks
    ]

    left = max(
        0,
        int(min(x_values))
    )

    right = min(
        width,
        int(max(x_values))
    )

    top = max(
        0,
        int(min(y_values))
    )

    bottom = min(
        height,
        int(max(y_values))
    )

    return left, top, right, bottom


def extract_cheek_regions(
    image_array,
    face_bounds
):
    """
    얼굴 영역 안에서 왼쪽과 오른쪽 볼 부분을 추출합니다.
    """
    left, top, right, bottom = face_bounds

    face_width = right - left
    face_height = bottom - top

    if face_width <= 0 or face_height <= 0:
        return []

    cheek_width = max(
        4,
        int(face_width * 0.14)
    )

    cheek_height = max(
        4,
        int(face_height * 0.12)
    )

    cheek_y = int(
        top + face_height * 0.57
    )

    left_cheek_x = int(
        left + face_width * 0.31
    )

    right_cheek_x = int(
        left + face_width * 0.69
    )

    cheek_regions = []

    for center_x in [
        left_cheek_x,
        right_cheek_x
    ]:
        x1 = max(
            0,
            center_x - cheek_width // 2
        )

        x2 = min(
            image_array.shape[1],
            center_x + cheek_width // 2
        )

        y1 = max(
            0,
            cheek_y - cheek_height // 2
        )

        y2 = min(
            image_array.shape[0],
            cheek_y + cheek_height // 2
        )

        region = image_array[
            y1:y2,
            x1:x2
        ]

        if region.size > 0:
            cheek_regions.append(region)

    return cheek_regions


def calculate_skin_color(cheek_regions):
    """
    볼 영역에서 피부색의 대표 RGB 값을 계산합니다.
    """
    if not cheek_regions:
        return None

    pixels = np.concatenate(
        [
            region.reshape(-1, 3)
            for region in cheek_regions
        ],
        axis=0
    ).astype(np.float32)

    brightness = pixels.mean(
        axis=1
    )

    valid_pixels = pixels[
        (brightness > 35)
        & (brightness < 245)
    ]

    if len(valid_pixels) < 10:
        valid_pixels = pixels

    median_rgb = np.median(
        valid_pixels,
        axis=0
    )

    return {
        "r": float(median_rgb[0]),
        "g": float(median_rgb[1]),
        "b": float(median_rgb[2])
    }


def calculate_color_features(skin_color):
    """
    대표 피부색을 이용해 밝기, 채도, 웜/쿨 지표를 계산합니다.
    """
    red = skin_color["r"]
    green = skin_color["g"]
    blue = skin_color["b"]

    normalized_rgb = (
        red / 255,
        green / 255,
        blue / 255
    )

    hue, saturation, value = colorsys.rgb_to_hsv(
        *normalized_rgb
    )

    warmth = (
        (red - blue) * 0.65
        + (green - blue) * 0.35
    )

    brightness = (
        red * 0.299
        + green * 0.587
        + blue * 0.114
    )

    return {
        "Red": round(red, 1),
        "Green": round(green, 1),
        "Blue": round(blue, 1),
        "Brightness": round(
            clamp(
                brightness / 255 * 100
            ),
            1
        ),
        "Saturation": round(
            clamp(
                saturation * 100
            ),
            1
        ),
        "Warmth": round(
            warmth,
            1
        ),
        "Hue": round(
            hue * 360,
            1
        )
    }


def classify_personal_color(features):
    """
    색상 특징을 기반으로 계절 타입을 추정합니다.
    """
    brightness = features[
        "Brightness"
    ]

    saturation = features[
        "Saturation"
    ]

    warmth = features[
        "Warmth"
    ]

    is_warm = warmth >= 18
    is_bright = brightness >= 62

    if is_warm and is_bright:
        season = "Spring Warm"
        undertone = "Warm"
        description = (
            "밝고 생기 있는 따뜻한 색상이 "
            "잘 어울릴 가능성이 있습니다."
        )

        recommended_colors = [
            "Coral",
            "Peach",
            "Ivory",
            "Warm Beige",
            "Light Camel"
        ]

    elif is_warm and not is_bright:
        season = "Autumn Warm"
        undertone = "Warm"
        description = (
            "차분하고 깊이 있는 따뜻한 색상이 "
            "잘 어울릴 가능성이 있습니다."
        )

        recommended_colors = [
            "Terracotta",
            "Olive",
            "Camel",
            "Mustard",
            "Chocolate Brown"
        ]

    elif not is_warm and is_bright:
        season = "Summer Cool"
        undertone = "Cool"
        description = (
            "부드럽고 맑은 차가운 색상이 "
            "잘 어울릴 가능성이 있습니다."
        )

        recommended_colors = [
            "Lavender",
            "Rose Pink",
            "Sky Blue",
            "Soft Navy",
            "Cool Gray"
        ]

    else:
        season = "Winter Cool"
        undertone = "Cool"
        description = (
            "선명하고 대비가 강한 차가운 색상이 "
            "잘 어울릴 가능성이 있습니다."
        )

        recommended_colors = [
            "Black",
            "Pure White",
            "Cobalt Blue",
            "Burgundy",
            "Emerald"
        ]

    confidence = (
        abs(warmth - 18) * 1.2
        + abs(brightness - 62) * 0.6
        + saturation * 0.15
    )

    confidence = round(
        clamp(
            50 + confidence,
            50,
            90
        ),
        1
    )

    return {
        "season": season,
        "undertone": undertone,
        "description": description,
        "recommended_colors": recommended_colors,
        "confidence": confidence
    }


def analyze_personal_color(
    image: Image.Image
):
    """
    얼굴 볼 영역의 색상을 분석해
    퍼스널 컬러 타입을 추정합니다.
    """
    try:
        image = image.convert("RGB")
        image_array = np.asarray(image)

        image_array = np.ascontiguousarray(
            image_array
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=image_array
        )

        landmarker = create_face_landmarker()
        result = landmarker.detect(
            mp_image
        )

    except Exception as error:
        return {
            "success": False,
            "message": (
                "사진을 분석하는 중 오류가 발생했습니다. "
                "다른 사진을 사용해주세요."
            ),
            "error": str(error)
        }

    if not result.face_landmarks:
        return {
            "success": False,
            "message": (
                "얼굴을 감지하지 못했습니다. "
                "얼굴이 선명하게 보이는 사진을 "
                "업로드해주세요."
            )
        }

    if len(result.face_landmarks) > 1:
        return {
            "success": False,
            "message": (
                "여러 명의 얼굴이 감지되었습니다. "
                "한 사람만 포함된 사진을 "
                "업로드해주세요."
            )
        }

    landmarks = result.face_landmarks[0]

    if not check_face_size(landmarks):
        return {
            "success": False,
            "message": (
                "사진 속 얼굴이 너무 작습니다. "
                "얼굴이 더 크게 보이는 사진을 "
                "업로드해주세요."
            )
        }

    height, width = image_array.shape[:2]

    face_bounds = get_face_bounds(
        landmarks,
        width,
        height
    )

    cheek_regions = extract_cheek_regions(
        image_array,
        face_bounds
    )

    skin_color = calculate_skin_color(
        cheek_regions
    )

    if skin_color is None:
        return {
            "success": False,
            "message": (
                "피부색을 분석하지 못했습니다. "
                "조명이 밝고 얼굴에 그림자가 적은 "
                "사진을 사용해주세요."
            )
        }

    color_features = calculate_color_features(
        skin_color
    )

    classification = classify_personal_color(
        color_features
    )

    return {
        "success": True,
        "season": classification["season"],
        "undertone": classification["undertone"],
        "description": classification["description"],
        "recommended_colors": classification[
            "recommended_colors"
        ],
        "confidence": classification["confidence"],
        "color_features": color_features
    }


def analyze_multiple_personal_colors(images):
    """
    여러 사진의 색상 특징을 평균 내어
    하나의 퍼스널컬러 결과를 생성합니다.
    """
    individual_results = []
    valid_results = []
    failed_results = []

    for index, image in enumerate(images):
        result = analyze_personal_color(
            image
        )

        result_with_index = {
            "image_index": index,
            **result
        }

        individual_results.append(
            result_with_index
        )

        if result["success"]:
            valid_results.append(
                result_with_index
            )

        else:
            failed_results.append(
                result_with_index
            )

    if not valid_results:
        return {
            "success": False,
            "message": (
                "퍼스널컬러를 분석할 수 있는 사진이 없습니다. "
                "자연광에서 촬영한 얼굴 사진을 사용해주세요."
            ),
            "individual_results": individual_results,
            "valid_count": 0,
            "failed_count": len(failed_results),
            "total_count": len(images)
        }

    averaged_skin_color = {
        "r": float(np.mean([
            result["color_features"]["Red"]
            for result in valid_results
        ])),
        "g": float(np.mean([
            result["color_features"]["Green"]
            for result in valid_results
        ])),
        "b": float(np.mean([
            result["color_features"]["Blue"]
            for result in valid_results
        ]))
    }

    averaged_features = calculate_color_features(
        averaged_skin_color
    )

    classification = classify_personal_color(
        averaged_features
    )

    return {
        "success": True,
        "season": classification["season"],
        "undertone": classification["undertone"],
        "description": classification["description"],
        "recommended_colors": classification[
            "recommended_colors"
        ],
        "confidence": classification["confidence"],
        "color_features": averaged_features,
        "individual_results": individual_results,
        "valid_count": len(valid_results),
        "failed_count": len(failed_results),
        "total_count": len(images)
    }