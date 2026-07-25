from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from PIL import (
    Image,
    ImageDraw,
    ImageFilter
)


PERSONAL_COLOR_BACKGROUNDS = {
    "Spring Warm": {
        "color": (250, 218, 174),
        "name": "Warm Peach"
    },
    "Summer Cool": {
        "color": (220, 216, 239),
        "name": "Soft Lavender"
    },
    "Autumn Warm": {
        "color": (196, 158, 117),
        "name": "Warm Camel"
    },
    "Winter Cool": {
        "color": (210, 230, 243),
        "name": "Icy Blue"
    }
}


NATURE_BACKGROUND_FILES = {
    "Spring Warm": (
        "assets/backgrounds/spring_nature.jpg"
    ),
    "Summer Cool": (
        "assets/backgrounds/summer_nature.jpg"
    ),
    "Autumn Warm": (
        "assets/backgrounds/autumn_nature.jpg"
    ),
    "Winter Cool": (
        "assets/backgrounds/winter_nature.jpg"
    )
}


def extract_personal_color_name(
    color_analysis_result
):
    """
    퍼스널컬러 분석 결과에서 시즌 이름을 가져옵니다.

    프로젝트마다 결과 딕셔너리의 key가 달라도
    어느 정도 대응할 수 있도록 여러 key를 확인합니다.
    """
    if isinstance(
        color_analysis_result,
        str
    ):
        return color_analysis_result

    if not isinstance(
        color_analysis_result,
        dict
    ):
        return None

    possible_keys = [
        "season",
        "personal_color",
        "color_type",
        "result",
        "final_result",
        "final_season",
        "dominant_season"
    ]

    for key in possible_keys:
        value = color_analysis_result.get(
            key
        )

        if isinstance(value, str):
            return value

    for value in color_analysis_result.values():
        if isinstance(value, dict):
            nested_result = (
                extract_personal_color_name(
                    value
                )
            )

            if nested_result:
                return nested_result

    return None


def normalize_personal_color_name(
    personal_color_name
):
    """
    분석 결과 문자열을 프로젝트에서 사용하는
    시즌 명칭으로 정규화합니다.
    """
    if not personal_color_name:
        return None

    normalized_name = (
        personal_color_name
        .strip()
        .lower()
    )

    aliases = {
        "spring": "Spring Warm",
        "spring warm": "Spring Warm",
        "봄": "Spring Warm",
        "봄 웜": "Spring Warm",
        "봄웜": "Spring Warm",

        "summer": "Summer Cool",
        "summer cool": "Summer Cool",
        "여름": "Summer Cool",
        "여름 쿨": "Summer Cool",
        "여름쿨": "Summer Cool",

        "autumn": "Autumn Warm",
        "autumn warm": "Autumn Warm",
        "가을": "Autumn Warm",
        "가을 웜": "Autumn Warm",
        "가을웜": "Autumn Warm",

        "winter": "Winter Cool",
        "winter cool": "Winter Cool",
        "겨울": "Winter Cool",
        "겨울 쿨": "Winter Cool",
        "겨울쿨": "Winter Cool"
    }

    return aliases.get(
        normalized_name,
        personal_color_name
    )


def create_person_mask(image):
    """
    MediaPipe Selfie Segmentation으로
    인물 영역 마스크를 생성합니다.
    """
    image_array = np.array(
        image.convert("RGB")
    )

    selfie_segmentation = (
        mp.solutions.selfie_segmentation
    )

    with selfie_segmentation.SelfieSegmentation(
        model_selection=1
    ) as segmenter:
        result = segmenter.process(
            image_array
        )

    if result.segmentation_mask is None:
        raise ValueError(
            "사진에서 사람 영역을 분리하지 못했습니다."
        )

    mask = result.segmentation_mask

    mask = np.clip(
        (mask - 0.1) / 0.8,
        0,
        1
    )

    mask = cv2.GaussianBlur(
        mask,
        (21, 21),
        0
    )

    return mask


def create_solid_background(
    size,
    personal_color_name
):
    """
    퍼스널컬러에 맞는 단색 배경을 생성합니다.
    """
    background_info = (
        PERSONAL_COLOR_BACKGROUNDS.get(
            personal_color_name,
            {
                "color": (239, 235, 225),
                "name": "Neutral Ivory"
            }
        )
    )

    background = Image.new(
        "RGB",
        size,
        background_info["color"]
    )

    return (
        background,
        background_info["name"]
    )


def create_generated_nature_background(
    size,
    personal_color_name
):
    """
    자연환경 이미지 파일이 없을 경우 사용할
    자연풍 배경을 생성합니다.
    """
    width, height = size

    palette_by_season = {
        "Spring Warm": {
            "sky": (244, 205, 157),
            "ground": (132, 167, 105),
            "accent": (238, 175, 125)
        },
        "Summer Cool": {
            "sky": (200, 217, 232),
            "ground": (125, 160, 151),
            "accent": (177, 167, 206)
        },
        "Autumn Warm": {
            "sky": (219, 181, 134),
            "ground": (122, 119, 71),
            "accent": (175, 107, 69)
        },
        "Winter Cool": {
            "sky": (195, 221, 237),
            "ground": (91, 126, 120),
            "accent": (225, 235, 241)
        }
    }

    palette = palette_by_season.get(
        personal_color_name,
        palette_by_season["Spring Warm"]
    )

    background = Image.new(
        "RGB",
        size
    )

    pixels = background.load()

    horizon = int(
        height * 0.58
    )

    for y in range(height):
        if y < horizon:
            ratio = y / max(
                horizon,
                1
            )

            color = tuple(
                int(
                    palette["sky"][channel]
                    * (1 - ratio * 0.15)
                )
                for channel in range(3)
            )

        else:
            ratio = (
                (y - horizon)
                / max(
                    height - horizon,
                    1
                )
            )

            color = tuple(
                int(
                    palette["ground"][channel]
                    * (1 - ratio * 0.25)
                )
                for channel in range(3)
            )

        for x in range(width):
            pixels[x, y] = color

    draw = ImageDraw.Draw(
        background,
        "RGBA"
    )

    mountain_points = [
        (0, horizon),
        (
            int(width * 0.25),
            int(height * 0.32)
        ),
        (
            int(width * 0.50),
            horizon
        ),
        (
            int(width * 0.72),
            int(height * 0.38)
        ),
        (width, horizon)
    ]

    draw.polygon(
        mountain_points,
        fill=(
            palette["accent"][0],
            palette["accent"][1],
            palette["accent"][2],
            150
        )
    )

    for center_x in [
        int(width * 0.08),
        int(width * 0.20),
        int(width * 0.82),
        int(width * 0.94)
    ]:
        draw.ellipse(
            (
                center_x - int(width * 0.12),
                int(height * 0.40),
                center_x + int(width * 0.12),
                int(height * 0.80)
            ),
            fill=(
                palette["ground"][0],
                palette["ground"][1],
                palette["ground"][2],
                190
            )
        )

    background = background.filter(
        ImageFilter.GaussianBlur(
            radius=max(
                6,
                int(width * 0.012)
            )
        )
    )

    return background


def create_nature_background(
    size,
    personal_color_name
):
    """
    시즌별 자연환경 배경 이미지를 불러옵니다.

    이미지 파일이 없으면 자동 생성한 자연풍 배경을 사용합니다.
    """
    background_path = (
        NATURE_BACKGROUND_FILES.get(
            personal_color_name
        )
    )

    if (
        background_path
        and Path(background_path).exists()
    ):
        background = Image.open(
            background_path
        ).convert("RGB")

        background = background.resize(
            size,
            Image.Resampling.LANCZOS
        )

        return (
            background,
            Path(background_path).name,
            False
        )

    generated_background = (
        create_generated_nature_background(
            size,
            personal_color_name
        )
    )

    return (
        generated_background,
        "Generated nature background",
        True
    )


def composite_person_and_background(
    person_image,
    background_image,
    mask
):
    """
    인물 이미지와 새 배경을 합성합니다.
    """
    person_array = np.array(
        person_image.convert("RGB")
    ).astype(
        np.float32
    )

    background_array = np.array(
        background_image.convert("RGB")
    ).astype(
        np.float32
    )

    mask_3_channels = np.repeat(
        mask[:, :, np.newaxis],
        3,
        axis=2
    ).astype(
        np.float32
    )

    composite_array = (
        person_array * mask_3_channels
        + background_array * (
            1 - mask_3_channels
        )
    )

    composite_array = np.clip(
        composite_array,
        0,
        255
    ).astype(
        np.uint8
    )

    return Image.fromarray(
        composite_array
    )


def change_background(
    image,
    background_type,
    color_analysis_result
):
    """
    사람은 유지하고 배경만 변경합니다.
    """
    personal_color_name = (
        extract_personal_color_name(
            color_analysis_result
        )
    )

    personal_color_name = (
        normalize_personal_color_name(
            personal_color_name
        )
    )

    if not personal_color_name:
        personal_color_name = (
            "Spring Warm"
        )

    original_image = image.convert(
        "RGB"
    )

    mask = create_person_mask(
        original_image
    )

    if (
        background_type
        == "퍼스널컬러 추천 단색"
    ):
        background_image, color_name = (
            create_solid_background(
                original_image.size,
                personal_color_name
            )
        )

        description = (
            f"{personal_color_name} 진단 결과에 어울리는 "
            f"{color_name} 계열의 단색으로 배경을 변경했습니다. "
            "사진 속 인물 영역은 유지하고 배경 영역만 교체했습니다."
        )

    else:
        (
            background_image,
            background_name,
            generated
        ) = create_nature_background(
            original_image.size,
            personal_color_name
        )

        if generated:
            background_source_description = (
                "시즌 색조를 반영한 자연풍 배경을 "
                "자동 생성해 사용했습니다."
            )

        else:
            background_source_description = (
                f"{background_name} 이미지를 사용했습니다."
            )

        description = (
            f"{personal_color_name}의 색감과 조화를 이루도록 "
            "자연환경 배경으로 변경했습니다. "
            "사진 속 인물은 유지하고 배경 영역만 교체했습니다. "
            f"{background_source_description}"
        )

    changed_image = (
        composite_person_and_background(
            person_image=original_image,
            background_image=background_image,
            mask=mask
        )
    )

    return {
        "image": changed_image,
        "description": description,
        "personal_color": personal_color_name
    }


def _get_mask_and_arrays(image):
    """공용: 인물 마스크 + 배열 준비"""
    original_image = image.convert("RGB")
    mask = create_person_mask(original_image)  # 이미 이 파일에 있는 함수 재사용
    original_array = np.array(original_image, dtype=np.float32)
    mask_3d = np.repeat(mask[:, :, np.newaxis], 3, axis=2)
    return original_image, original_array, mask_3d
 
 
def blur_background(image, blur_radius=15):
    """배경만 블러 처리하고 인물은 선명하게 유지"""
    original_image, original_array, mask_3d = _get_mask_and_arrays(image)
 
    blurred = original_image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    blurred_array = np.array(blurred, dtype=np.float32)
 
    result_array = original_array * mask_3d + blurred_array * (1 - mask_3d)
    result_array = np.clip(result_array, 0, 255).astype(np.uint8)
    return Image.fromarray(result_array)
 
 
def apply_solid_color_background(image, hex_color):
    """배경을 지정한 단색으로 교체"""
    hex_color = hex_color.lstrip("#")
    rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
 
    original_image, original_array, mask_3d = _get_mask_and_arrays(image)
    background_array = np.full(original_array.shape, rgb, dtype=np.float32)
 
    result_array = original_array * mask_3d + background_array * (1 - mask_3d)
    result_array = np.clip(result_array, 0, 255).astype(np.uint8)
    return Image.fromarray(result_array)
 
 
def _generate_office_background(size):
    """사진 파일 없이 코드로 만드는 간단한 오피스 느낌 배경"""
    width, height = size
    bg = Image.new("RGB", size, (223, 226, 231))
    draw = ImageDraw.Draw(bg)
    # 창문/파티션 느낌의 세로 라인
    for x in range(0, width, max(40, width // 8)):
        draw.line([(x, 0), (x, height)], fill=(200, 204, 210), width=2)
    draw.rectangle([0, int(height * 0.75), width, height], fill=(210, 213, 218))
    return bg.filter(ImageFilter.GaussianBlur(radius=8))
 
 
def _generate_urban_background(size):
    """사진 파일 없이 코드로 만드는 간단한 도시 느낌 배경"""
    width, height = size
    bg = Image.new("RGB", size, (176, 184, 196))
    draw = ImageDraw.Draw(bg)
    horizon = int(height * 0.62)
    draw.rectangle([0, horizon, width, height], fill=(150, 156, 165))
    # 건물 실루엣
    import random
    random.seed(42)
    x = 0
    while x < width:
        w = random.randint(width // 10, width // 6)
        h = random.randint(int(height * 0.25), int(height * 0.5))
        draw.rectangle([x, horizon - h, x + w, horizon], fill=(130, 138, 150))
        x += w + random.randint(5, 15)
    return bg.filter(ImageFilter.GaussianBlur(radius=6))
 
 
def apply_generated_background(image, background_type):
    """Office / Urban 같은 생성 배경을 합성"""
    original_image, original_array, mask_3d = _get_mask_and_arrays(image)
 
    if background_type == "Office":
        bg = _generate_office_background(original_image.size)
    elif background_type == "Urban":
        bg = _generate_urban_background(original_image.size)
    else:
        return original_image
 
    bg_array = np.array(bg, dtype=np.float32)
    result_array = original_array * mask_3d + bg_array * (1 - mask_3d)
    result_array = np.clip(result_array, 0, 255).astype(np.uint8)
    return Image.fromarray(result_array)