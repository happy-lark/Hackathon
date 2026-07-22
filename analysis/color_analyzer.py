import cv2
import numpy as np
from PIL import Image

from analysis.analyzer import detect_single_face

# 피부색을 추출할 얼굴 랜드마크
# 입술·눈 화장 영향을 피하고 이마와 양 볼을 사용
SKIN_LANDMARK_INDICES = {
    "forehead": 10,
    "left_cheek": 50,
    "right_cheek": 280
}


def clamp(value, minimum=0.0, maximum=100.0):
    """
    값을 지정된 범위 안으로 제한합니다.
    """
    return max(minimum, min(maximum, value))


def get_face_width_pixels(landmarks, image_width):
    """
    얼굴의 가로 길이를 픽셀 단위로 계산합니다.
    """

    x_values = [
        landmark.x
        for landmark in landmarks
    ]

    normalized_width = (
        max(x_values) - min(x_values)
    )

    return normalized_width * image_width


def extract_landmark_patch(
    image_array,
    landmark,
    patch_radius
):
    """
    특정 랜드마크 주변의 정사각형 이미지 영역을 추출합니다.
    """

    image_height, image_width, _ = image_array.shape

    center_x = int(
        landmark.x * image_width
    )

    center_y = int(
        landmark.y * image_height
    )

    x1 = max(
        0,
        center_x - patch_radius
    )

    x2 = min(
        image_width,
        center_x + patch_radius
    )

    y1 = max(
        0,
        center_y - patch_radius
    )

    y2 = min(
        image_height,
        center_y + patch_radius
    )

    return image_array[
        y1:y2,
        x1:x2
    ]


def filter_skin_pixels(region_rgb):
    """
    YCrCb 색공간을 사용해 피부색 후보 픽셀만 추출합니다.
    """

    if region_rgb.size == 0:
        return np.empty(
            (0, 3),
            dtype=np.uint8
        )

    region_ycrcb = cv2.cvtColor(
        region_rgb,
        cv2.COLOR_RGB2YCrCb
    )

    lower_skin = np.array(
        [0, 133, 77],
        dtype=np.uint8
    )

    upper_skin = np.array(
        [255, 173, 127],
        dtype=np.uint8
    )

    skin_mask = cv2.inRange(
        region_ycrcb,
        lower_skin,
        upper_skin
    )

    return region_rgb[
        skin_mask > 0
    ]


def extract_face_skin_pixels(
    image_array,
    landmarks
):
    """
    이마와 양 볼 주변에서 피부색 후보 픽셀을 추출합니다.
    """

    _, image_width, _ = image_array.shape

    face_width = get_face_width_pixels(
        landmarks,
        image_width
    )

    # 사진 크기에 따라 피부 샘플 영역 크기를 조정
    patch_radius = max(
        4,
        int(face_width * 0.04)
    )

    extracted_pixels = []

    for landmark_index in SKIN_LANDMARK_INDICES.values():
        landmark = landmarks[
            landmark_index
        ]

        patch = extract_landmark_patch(
            image_array,
            landmark,
            patch_radius
        )

        skin_pixels = filter_skin_pixels(
            patch
        )

        if len(skin_pixels) > 0:
            extracted_pixels.append(
                skin_pixels
            )

    if not extracted_pixels:
        return np.empty(
            (0, 3),
            dtype=np.uint8
        )

    return np.concatenate(
        extracted_pixels,
        axis=0
    )


def calculate_color_features(skin_pixels):
    """
    피부 픽셀에서 RGB, HSV, Lab 특징을 계산합니다.
    """

    # 극단적인 조명 픽셀의 영향을 줄이기 위해 중앙값 사용
    median_rgb = np.median(
        skin_pixels,
        axis=0
    )

    pixel_array = skin_pixels.reshape(
        -1,
        1,
        3
    ).astype(np.uint8)

    hsv_pixels = cv2.cvtColor(
        pixel_array,
        cv2.COLOR_RGB2HSV
    ).reshape(-1, 3)

    lab_pixels = cv2.cvtColor(
        pixel_array,
        cv2.COLOR_RGB2LAB
    ).reshape(-1, 3)

    median_hsv = np.median(
        hsv_pixels,
        axis=0
    )

    median_lab = np.median(
        lab_pixels,
        axis=0
    )

    red, green, blue = median_rgb
    hue, saturation, value = median_hsv
    lightness, a_value, b_value = median_lab

    # OpenCV Lab에서는 a와 b의 중립점이 128
    lab_a = float(a_value) - 128
    lab_b = float(b_value) - 128

    warmth_score = (
        50
        + lab_b * 1.2
        + (
            float(red) - float(blue)
        ) * 0.25
    )

    brightness_score = (
        float(value)
        / 255
        * 100
    )

    saturation_score = (
        float(saturation)
        / 255
        * 100
    )

    return {
        "average_rgb": {
            "r": int(red),
            "g": int(green),
            "b": int(blue)
        },
        "warmth_score": round(
            clamp(warmth_score),
            1
        ),
        "brightness_score": round(
            clamp(brightness_score),
            1
        ),
        "saturation_score": round(
            clamp(saturation_score),
            1
        ),
        "lab": {
            "l": round(
                float(lightness),
                1
            ),
            "a": round(
                lab_a,
                1
            ),
            "b": round(
                lab_b,
                1
            )
        },
        "hsv": {
            "h": round(
                float(hue),
                1
            ),
            "s": round(
                float(saturation),
                1
            ),
            "v": round(
                float(value),
                1
            )
        }
    }


def classify_personal_color(features):
    """
    온도감, 밝기, 채도를 이용해
    간이 퍼스널 컬러 계절 타입을 추정합니다.
    """

    warmth = features[
        "warmth_score"
    ]

    brightness = features[
        "brightness_score"
    ]

    saturation = features[
        "saturation_score"
    ]

    is_warm = warmth >= 50
    is_bright = brightness >= 65
    is_clear = saturation >= 25

    if is_warm and (is_bright or is_clear):
        season = "Spring Warm"
        description = (
            "밝고 생기 있는 따뜻한 계열의 색상이 "
            "잘 어울릴 가능성이 높습니다."
        )
        recommended_colors = [
            {"name": "Coral", "hex": "#FF7F6A"},
            {"name": "Peach", "hex": "#FFB38A"},
            {"name": "Warm Ivory", "hex": "#FFF3D6"},
            {"name": "Fresh Green", "hex": "#8DBF67"},
            {"name": "Light Camel", "hex": "#C99A6B"}
        ]

    elif is_warm:
        season = "Autumn Warm"
        description = (
            "차분하고 깊이 있는 따뜻한 계열의 색상이 "
            "잘 어울릴 가능성이 높습니다."
        )
        recommended_colors = [
            {"name": "Terracotta", "hex": "#B85C43"},
            {"name": "Olive", "hex": "#7A7B3A"},
            {"name": "Camel", "hex": "#B88655"},
            {"name": "Mustard", "hex": "#C99728"},
            {"name": "Chocolate", "hex": "#5C3428"}
        ]

    elif is_bright and not is_clear:
        season = "Summer Cool"
        description = (
            "부드럽고 밝은 차가운 계열의 색상이 "
            "잘 어울릴 가능성이 높습니다."
        )
        recommended_colors = [
            {"name": "Dusty Rose", "hex": "#C58D9B"},
            {"name": "Lavender", "hex": "#B8A6D9"},
            {"name": "Powder Blue", "hex": "#AFCBE3"},
            {"name": "Soft Navy", "hex": "#596A8A"},
            {"name": "Cool Gray", "hex": "#A7A9B0"}
        ]

    else:
        season = "Winter Cool"
        description = (
            "선명하고 대비감 있는 차가운 계열의 색상이 "
            "잘 어울릴 가능성이 높습니다."
        )
        recommended_colors = [
            {"name": "Royal Blue", "hex": "#3154C8"},
            {"name": "Fuchsia", "hex": "#D42A86"},
            {"name": "Emerald", "hex": "#00896F"},
            {"name": "Pure White", "hex": "#FFFFFF"},
            {"name": "Black", "hex": "#111111"}
        ]

    return {
        "season": season,
        "tone": "Warm" if is_warm else "Cool",
        "description": description,
        "recommended_colors": recommended_colors
    }


def analyze_personal_color(image: Image.Image):
    """
    MediaPipe 얼굴 랜드마크를 활용해
    간이 퍼스널 컬러 분석을 수행합니다.
    """

    face_result = detect_single_face(
        image
    )

    if not face_result["success"]:
        return face_result

    image_array = face_result[
        "image_array"
    ]

    landmarks = face_result[
        "landmarks"
    ]

    skin_pixels = extract_face_skin_pixels(
        image_array,
        landmarks
    )

    if len(skin_pixels) < 30:
        return {
            "success": False,
            "message": (
                "피부색을 충분히 추출하지 못했습니다. "
                "자연광에서 촬영하고 이마와 양 볼이 "
                "잘 보이는 사진을 사용해주세요."
            )
        }

    features = calculate_color_features(
        skin_pixels
    )

    classification = classify_personal_color(
        features
    )

    return {
        "success": True,
        "season": classification[
            "season"
        ],
        "tone": classification[
            "tone"
        ],
        "description": classification[
            "description"
        ],
        "recommended_colors": classification[
            "recommended_colors"
        ],
        "features": features
    }